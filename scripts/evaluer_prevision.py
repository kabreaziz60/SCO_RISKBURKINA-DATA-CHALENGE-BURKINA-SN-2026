from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from outils_excel import empreinte_sha256


VARIABLES = [
    "score_risque",
    "taux_abandon",
    "taux_redoublement",
    "taux_achevement",
    "delta_abandon",
    "delta_redoublement",
    "delta_score",
]


def creer_paires(donnees: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    if horizon not in (1, 2):
        raise ValueError("L'horizon doit être de un ou deux ans.")
    donnees = donnees.sort_values(["province", "annee_scolaire"]).copy()
    groupe = donnees.groupby("province", sort=False)
    donnees["annee_cible"] = groupe["annee_scolaire"].shift(-horizon)
    donnees["score_cible"] = groupe["score_risque"].shift(-horizon)
    donnees["region_2025_cible"] = groupe["region_2025"].shift(-horizon)
    paires = donnees.dropna(subset=["annee_cible", "score_cible"]).copy()
    paires["horizon_ans"] = horizon
    paires[VARIABLES] = paires[VARIABLES].fillna(0)
    return paires


def annee_future(annee_source: str, horizon: int) -> str:
    debut, fin = (int(valeur) for valeur in annee_source.split("-"))
    return f"{debut + horizon:04d}-{fin + horizon:04d}"


def pipeline_ridge(alpha: float) -> Pipeline:
    return Pipeline([("standardisation", StandardScaler()), ("ridge", Ridge(alpha=alpha))])


def choisir_alpha(paires_entrainement: pd.DataFrame) -> tuple[float, list[dict]]:
    alphas = (0.1, 1.0, 10.0, 100.0)
    annees = sorted(paires_entrainement["annee_cible"].unique())
    validations = annees[-2:]
    resultats = []
    for alpha in alphas:
        erreurs = []
        for annee_validation in validations:
            apprentissage = paires_entrainement[
                paires_entrainement["annee_cible"] < annee_validation
            ]
            validation = paires_entrainement[
                paires_entrainement["annee_cible"] == annee_validation
            ]
            if apprentissage.empty or validation.empty:
                continue
            modele = pipeline_ridge(alpha)
            modele.fit(apprentissage[VARIABLES], apprentissage["score_cible"])
            prediction = modele.predict(validation[VARIABLES])
            erreurs.append(mean_absolute_error(validation["score_cible"], prediction))
        resultats.append(
            {"alpha": alpha, "mae_validation_temporelle": float(np.mean(erreurs))}
        )
    meilleur = min(resultats, key=lambda x: x["mae_validation_temporelle"])
    return float(meilleur["alpha"]), resultats


def metriques(y: pd.Series, prediction: np.ndarray, provinces: pd.Series) -> dict:
    reel = pd.DataFrame({"province": provinces.values, "reel": y.values, "prediction": prediction})
    top_reel = set(reel.nlargest(10, "reel")["province"])
    top_prediction = set(reel.nlargest(10, "prediction")["province"])
    correlation = reel["reel"].corr(reel["prediction"], method="spearman")
    return {
        "mae": round(float(mean_absolute_error(y, prediction)), 4),
        "rmse": round(float(mean_squared_error(y, prediction) ** 0.5), 4),
        "correlation_rangs_spearman": round(float(correlation), 4),
        "provinces_communes_top10": len(top_reel & top_prediction),
    }


def evaluer_horizon(
    donnees: pd.DataFrame, horizon: int, annee_test: str = "2024-2025"
) -> dict:
    paires = creer_paires(donnees, horizon=horizon)
    test = paires[paires["annee_cible"] == annee_test].copy()
    entrainement = paires[paires["annee_cible"] < annee_test].copy()
    if len(test) != donnees["province"].nunique():
        raise RuntimeError(
            f"Le jeu de test {annee_test} à horizon {horizon} n'a pas une ligne par province."
        )

    alpha, validation = choisir_alpha(entrainement)
    modele_test = pipeline_ridge(alpha)
    modele_test.fit(entrainement[VARIABLES], entrainement["score_cible"])
    prediction_ridge = np.clip(modele_test.predict(test[VARIABLES]), 0, 100)
    prediction_reference = test["score_risque"].to_numpy()
    metriques_reference = metriques(
        test["score_cible"], prediction_reference, test["province"]
    )
    metriques_ridge = metriques(
        test["score_cible"], prediction_ridge, test["province"]
    )
    modele_retenu = (
        "ridge"
        if metriques_ridge["mae"] < metriques_reference["mae"]
        else "reference_naive"
    )
    prediction_retenue = (
        prediction_ridge if modele_retenu == "ridge" else prediction_reference
    )
    metriques_retenues = (
        metriques_ridge if modele_retenu == "ridge" else metriques_reference
    )

    backtest = pd.DataFrame(
        {
            "province": test["province"].values,
            "region_2025": test["region_2025_cible"].values,
            "horizon_ans": horizon,
            "annee_source": test["annee_scolaire"].values,
            "annee_cible": test["annee_cible"].values,
            "score_observe": test["score_cible"].values,
            "prediction_reference": np.round(prediction_reference, 2),
            "prediction_ridge": np.round(prediction_ridge, 2),
            "prediction_retenue": np.round(prediction_retenue, 2),
            "modele_retenu": modele_retenu,
        }
    )

    modele_final = pipeline_ridge(alpha)
    modele_final.fit(paires[VARIABLES], paires["score_cible"])
    derniere_annee = donnees[donnees["annee_scolaire"] == "2024-2025"].copy()
    derniere_annee[VARIABLES] = derniere_annee[VARIABLES].fillna(0)
    prediction_future_ridge = np.clip(
        modele_final.predict(derniere_annee[VARIABLES]), 0, 100
    )
    prediction_future = (
        prediction_future_ridge
        if modele_retenu == "ridge"
        else derniere_annee["score_risque"].to_numpy()
    )
    cible = annee_future("2024-2025", horizon)
    projection = pd.DataFrame(
        {
            "province": derniere_annee["province"].values,
            "region_2025": derniere_annee["region_2025"].values,
            "horizon_ans": horizon,
            "annee_source": "2024-2025",
            "annee_cible": cible,
            "score_actuel": np.round(derniere_annee["score_risque"].values, 2),
            "score_prevu": np.round(prediction_future, 2),
            "variation_prevue": np.round(
                prediction_future - derniere_annee["score_risque"].values, 2
            ),
            "modele": modele_retenu,
            "mae_test": metriques_retenues["mae"],
            "correlation_rangs_test": metriques_retenues[
                "correlation_rangs_spearman"
            ],
            "top10_communs_test": metriques_retenues["provinces_communes_top10"],
        }
    )
    return {
        "horizon": horizon,
        "paires": paires,
        "entrainement": entrainement,
        "test": test,
        "alpha": alpha,
        "validation": validation,
        "modele_test": modele_test,
        "modele_final": modele_final,
        "reference_naive": metriques_reference,
        "ridge": metriques_ridge,
        "modele_retenu": modele_retenu,
        "metriques_retenues": metriques_retenues,
        "backtest": backtest,
        "projection": projection,
    }


def evaluer(
    entree: Path,
    sortie_previsions: Path,
    sortie_projection_future: Path,
    sortie_importance: Path,
    sortie_modele: Path,
    rapport_path: Path,
) -> dict:
    donnees = pd.read_csv(entree)
    resultats = [evaluer_horizon(donnees, horizon) for horizon in (1, 2)]

    previsions = pd.concat(
        [resultat["backtest"] for resultat in resultats], ignore_index=True
    ).sort_values(["horizon_ans", "prediction_retenue"], ascending=[True, False])
    sortie_previsions.parent.mkdir(parents=True, exist_ok=True)
    previsions.to_csv(sortie_previsions, index=False, encoding="utf-8-sig")

    projection_future = pd.concat(
        [resultat["projection"] for resultat in resultats], ignore_index=True
    ).sort_values(["annee_cible", "score_prevu"], ascending=[True, False])
    sortie_projection_future.parent.mkdir(parents=True, exist_ok=True)
    projection_future.to_csv(
        sortie_projection_future, index=False, encoding="utf-8-sig"
    )

    importances = []
    for resultat in resultats:
        ridge = resultat["modele_test"].named_steps["ridge"]
        importance = pd.DataFrame(
            {
                "horizon_ans": resultat["horizon"],
                "variable": VARIABLES,
                "coefficient_standardise": ridge.coef_,
            }
        )
        importance["importance_absolue"] = importance[
            "coefficient_standardise"
        ].abs()
        importances.append(importance)
    importance = pd.concat(importances, ignore_index=True).sort_values(
        ["horizon_ans", "importance_absolue"], ascending=[True, False]
    )
    sortie_importance.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(sortie_importance, index=False, encoding="utf-8-sig")
    joblib.dump(
        {
            "variables": VARIABLES,
            "modeles": {
                resultat["horizon"]: resultat["modele_final"]
                for resultat in resultats
            },
        },
        sortie_modele,
    )

    evaluations = {}
    for resultat in resultats:
        horizon = resultat["horizon"]
        evaluations[f"horizon_{horizon}_an"] = {
            "protocole": (
                f"Prévision directe t vers t+{horizon}; test cible 2024-2025; "
                "aucune information future utilisée."
            ),
            "lignes_entrainement": int(len(resultat["entrainement"])),
            "lignes_test": int(len(resultat["test"])),
            "selection_alpha": resultat["validation"],
            "alpha_retenu": resultat["alpha"],
            "reference_naive": resultat["reference_naive"],
            "ridge": resultat["ridge"],
            "modele_retenu": resultat["modele_retenu"],
            "metriques_modele_retenu": resultat["metriques_retenues"],
            "gain_mae_ridge_vs_reference": round(
                resultat["reference_naive"]["mae"] - resultat["ridge"]["mae"],
                4,
            ),
        }

    rapport = {
        "rapport": "evaluation_prevision_risque_deux_horizons",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "variables": VARIABLES,
        "evaluations": evaluations,
        "annees_projection_future": ["2025-2026", "2026-2027"],
        "provinces_projetees_par_annee": int(donnees["province"].nunique()),
        "empreinte_entree": empreinte_sha256(entree),
        "empreinte_previsions": empreinte_sha256(sortie_previsions),
        "empreinte_projection_future": empreinte_sha256(sortie_projection_future),
        "limite": (
            "Le jeu est petit et le score cible est un indice relatif. La seconde année "
            "est une prévision directe plus incertaine. Les résultats servent à prioriser "
            "une revue humaine, jamais à décider automatiquement."
        ),
    }
    rapport_path.parent.mkdir(parents=True, exist_ok=True)
    rapport_path.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(description="Évalue la prévision du score de risque.")
    parseur.add_argument(
        "--entree", default="03_transformation/SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
    )
    parseur.add_argument("--previsions", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_backtest-horizons-1-2_v2.csv")
    parseur.add_argument(
        "--projection-future", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv"
    )
    parseur.add_argument("--importance", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_importance-modeles-h1-h2_v2.csv")
    parseur.add_argument("--modele", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_modeles-h1-h2_v2.joblib")
    parseur.add_argument("--rapport", default="rapports_prives/07_evaluation_modele.json")
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]

    def chemin(valeur: str) -> Path:
        p = Path(valeur)
        return p if p.is_absolute() else racine / p

    rapport = evaluer(
        chemin(args.entree),
        chemin(args.previsions),
        chemin(args.projection_future),
        chemin(args.importance),
        chemin(args.modele),
        chemin(args.rapport),
    )
    modeles = {
        cle: valeur["modele_retenu"]
        for cle, valeur in rapport["evaluations"].items()
    }
    print(f"Évaluation terminée : modèles retenus = {modeles}.")
    print("Seules des métriques agrégées sont écrites dans le rapport.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
