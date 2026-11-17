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


def creer_paires(donnees: pd.DataFrame) -> pd.DataFrame:
    donnees = donnees.sort_values(["province", "annee_scolaire"]).copy()
    groupe = donnees.groupby("province", sort=False)
    donnees["annee_cible"] = groupe["annee_scolaire"].shift(-1)
    donnees["score_cible"] = groupe["score_risque"].shift(-1)
    donnees["region_2025_cible"] = groupe["region_2025"].shift(-1)
    paires = donnees.dropna(subset=["annee_cible", "score_cible"]).copy()
    paires[VARIABLES] = paires[VARIABLES].fillna(0)
    return paires


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


def evaluer(
    entree: Path,
    sortie_previsions: Path,
    sortie_projection_future: Path,
    sortie_importance: Path,
    sortie_modele: Path,
    rapport_path: Path,
) -> dict:
    donnees = pd.read_csv(entree)
    paires = creer_paires(donnees)
    test = paires[paires["annee_cible"] == "2024-2025"].copy()
    entrainement = paires[paires["annee_cible"] < "2024-2025"].copy()
    if len(test) != donnees["province"].nunique():
        raise RuntimeError("Le jeu de test 2024-2025 n'a pas une ligne par province.")

    alpha, validation = choisir_alpha(entrainement)
    modele = pipeline_ridge(alpha)
    modele.fit(entrainement[VARIABLES], entrainement["score_cible"])
    prediction_ridge = np.clip(modele.predict(test[VARIABLES]), 0, 100)
    prediction_reference = test["score_risque"].to_numpy()

    metriques_reference = metriques(
        test["score_cible"], prediction_reference, test["province"]
    )
    metriques_ridge = metriques(test["score_cible"], prediction_ridge, test["province"])
    modele_retenu = "ridge" if metriques_ridge["mae"] < metriques_reference["mae"] else "reference_naive"
    prediction_retenue = prediction_ridge if modele_retenu == "ridge" else prediction_reference

    previsions = pd.DataFrame(
        {
            "province": test["province"].values,
            "region_2025": test["region_2025_cible"].values,
            "annee_source": test["annee_scolaire"].values,
            "annee_cible": test["annee_cible"].values,
            "score_observe": test["score_cible"].values,
            "prediction_reference": np.round(prediction_reference, 2),
            "prediction_ridge": np.round(prediction_ridge, 2),
            "prediction_retenue": np.round(prediction_retenue, 2),
            "modele_retenu": modele_retenu,
        }
    ).sort_values("prediction_retenue", ascending=False)
    sortie_previsions.parent.mkdir(parents=True, exist_ok=True)
    previsions.to_csv(sortie_previsions, index=False, encoding="utf-8-sig")

    # Une fois le protocole de test terminé, on réentraîne sur toutes les
    # transitions observées. La dernière année disponible (2024-2025) sert
    # alors à produire l'alerte prospective 2025-2026.
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
    projection_future = pd.DataFrame(
        {
            "province": derniere_annee["province"].values,
            "region_2025": derniere_annee["region_2025"].values,
            "annee_source": "2024-2025",
            "annee_cible": "2025-2026",
            "score_actuel": np.round(derniere_annee["score_risque"].values, 2),
            "score_prevu": np.round(prediction_future, 2),
            "variation_prevue": np.round(
                prediction_future - derniere_annee["score_risque"].values, 2
            ),
            "modele": modele_retenu,
        }
    ).sort_values("score_prevu", ascending=False)
    sortie_projection_future.parent.mkdir(parents=True, exist_ok=True)
    projection_future.to_csv(
        sortie_projection_future, index=False, encoding="utf-8-sig"
    )

    ridge = modele.named_steps["ridge"]
    importance = pd.DataFrame(
        {"variable": VARIABLES, "coefficient_standardise": ridge.coef_}
    )
    importance["importance_absolue"] = importance["coefficient_standardise"].abs()
    importance = importance.sort_values("importance_absolue", ascending=False)
    sortie_importance.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(sortie_importance, index=False, encoding="utf-8-sig")
    joblib.dump(modele_final, sortie_modele)

    rapport = {
        "rapport": "evaluation_prevision_risque",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "protocole": "Paires année t vers t+1 ; entraînement jusqu'à 2023-2024 ; test cible 2024-2025.",
        "lignes_entrainement": int(len(entrainement)),
        "lignes_test": int(len(test)),
        "variables": VARIABLES,
        "selection_alpha": validation,
        "alpha_retenu": alpha,
        "reference_naive": metriques_reference,
        "ridge": metriques_ridge,
        "modele_retenu": modele_retenu,
        "annee_projection_future": "2025-2026",
        "provinces_projetees": int(len(projection_future)),
        "gain_mae_vs_reference": round(
            metriques_reference["mae"] - metriques_ridge["mae"], 4
        ),
        "empreinte_entree": empreinte_sha256(entree),
        "empreinte_previsions": empreinte_sha256(sortie_previsions),
        "empreinte_projection_future": empreinte_sha256(sortie_projection_future),
        "limite": (
            "Le jeu est petit et le score cible est un indice relatif. Les prédictions servent "
            "à prioriser une revue humaine, pas à décider automatiquement."
        ),
    }
    rapport_path.parent.mkdir(parents=True, exist_ok=True)
    rapport_path.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(description="Évalue la prévision du score de risque.")
    parseur.add_argument(
        "--entree", default="03_transformation/SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
    )
    parseur.add_argument("--previsions", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_previsions-2024-2025_v1.csv")
    parseur.add_argument(
        "--projection-future", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2026_v1.csv"
    )
    parseur.add_argument("--importance", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_importance-modele_v1.csv")
    parseur.add_argument("--modele", default="04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_modele-ridge_v1.joblib")
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
    print(f"Évaluation terminée : modèle retenu = {rapport['modele_retenu']}.")
    print("Seules des métriques agrégées sont écrites dans le rapport.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
