from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from outils_excel import empreinte_sha256


POIDS = {
    "principal": {"abandon": 0.50, "redoublement": 0.30, "non_achevement": 0.20},
    "abandon_dominant": {"abandon": 0.60, "redoublement": 0.25, "non_achevement": 0.15},
    "equilibre": {"abandon": 0.40, "redoublement": 0.30, "non_achevement": 0.30},
}


def score_pondere(
    rang_abandon: pd.Series,
    rang_redoublement: pd.Series,
    rang_non_achevement: pd.Series,
    poids: dict[str, float],
) -> pd.Series:
    return (
        poids["abandon"] * rang_abandon
        + poids["redoublement"] * rang_redoublement
        + poids["non_achevement"] * rang_non_achevement
    )


def categorie_risque(score: float) -> str:
    if score >= 75:
        return "Critique"
    if score >= 55:
        return "Élevé"
    if score >= 35:
        return "Modéré"
    return "Faible"


def transformer(entree: Path, sortie: Path, sensibilite: Path, rapport_path: Path) -> dict:
    donnees = pd.read_csv(entree)
    attendues = {
        "province",
        "region_historique",
        "region_2025",
        "annee_scolaire",
        "taux_abandon_moyen_non_pondere",
        "taux_redoublement_moyen_non_pondere",
        "taux_achevement_region",
        "statut_qualite",
    }
    absentes = sorted(attendues - set(donnees.columns))
    if absentes:
        raise ValueError("Colonnes absentes : " + ", ".join(absentes))

    donnees = donnees.sort_values(["province", "annee_scolaire"]).copy()
    donnees["taux_abandon"] = donnees["taux_abandon_moyen_non_pondere"]
    donnees["taux_redoublement"] = donnees["taux_redoublement_moyen_non_pondere"]
    donnees["taux_achevement"] = donnees["taux_achevement_region"]
    donnees["taux_non_achevement"] = 100 - donnees["taux_achevement"]

    for source, cible in (
        ("taux_abandon", "rang_abandon"),
        ("taux_redoublement", "rang_redoublement"),
        ("taux_non_achevement", "rang_non_achevement"),
    ):
        donnees[cible] = donnees.groupby("annee_scolaire")[source].rank(
            method="average", pct=True
        ) * 100

    for scenario, poids in POIDS.items():
        donnees[f"score_{scenario}"] = score_pondere(
            donnees["rang_abandon"],
            donnees["rang_redoublement"],
            donnees["rang_non_achevement"],
            poids,
        ).round(2)

    donnees["score_risque"] = donnees["score_principal"]
    donnees["niveau_alerte"] = donnees["score_risque"].map(categorie_risque)
    donnees["fiabilite"] = np.where(donnees["statut_qualite"].eq("ok"), 0.85, 0.65)

    groupe = donnees.groupby("province", sort=False)
    donnees["delta_abandon"] = groupe["taux_abandon"].diff()
    donnees["delta_redoublement"] = groupe["taux_redoublement"].diff()
    donnees["delta_score"] = groupe["score_risque"].diff()

    lignes_sensibilite = []
    for annee, cadre in donnees.groupby("annee_scolaire"):
        top_principal = set(cadre.nlargest(10, "score_principal")["province"])
        for scenario in ("abandon_dominant", "equilibre"):
            correlation = cadre["score_principal"].corr(
                cadre[f"score_{scenario}"], method="spearman"
            )
            top_scenario = set(cadre.nlargest(10, f"score_{scenario}")["province"])
            lignes_sensibilite.append(
                {
                    "annee_scolaire": annee,
                    "scenario": scenario,
                    "correlation_rangs_spearman": round(float(correlation), 4),
                    "provinces_communes_top10": len(top_principal & top_scenario),
                }
            )
    cadre_sensibilite = pd.DataFrame(lignes_sensibilite)

    colonnes_sortie = [
        "province",
        "region_historique",
        "region_2025",
        "annee_scolaire",
        "taux_abandon",
        "taux_redoublement",
        "taux_achevement",
        "taux_non_achevement",
        "rang_abandon",
        "rang_redoublement",
        "rang_non_achevement",
        "score_risque",
        "score_abandon_dominant",
        "score_equilibre",
        "niveau_alerte",
        "delta_abandon",
        "delta_redoublement",
        "delta_score",
        "fiabilite",
        "statut_qualite",
        "niveau_geographique_achevement",
        "source_indicateurs_province",
        "source_achevement",
        "page_source",
    ]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    donnees.sort_values(["annee_scolaire", "province"])[colonnes_sortie].to_csv(
        sortie, index=False, encoding="utf-8-sig"
    )
    sensibilite.parent.mkdir(parents=True, exist_ok=True)
    cadre_sensibilite.to_csv(sensibilite, index=False, encoding="utf-8-sig")

    doublons = int(donnees.duplicated(["province", "annee_scolaire"]).sum())
    manquants = {
        colonne: int(donnees[colonne].isna().sum())
        for colonne in ("taux_abandon", "taux_redoublement", "taux_achevement", "score_risque")
    }
    hors_plage = int((~donnees["score_risque"].between(0, 100)).sum())
    rapport = {
        "rapport": "transformation_indice_risque",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "nombre_lignes": int(len(donnees)),
        "nombre_provinces": int(donnees["province"].nunique()),
        "nombre_annees": int(donnees["annee_scolaire"].nunique()),
        "doublons_province_annee": doublons,
        "valeurs_manquantes": manquants,
        "scores_hors_plage": hors_plage,
        "poids": POIDS,
        "sensibilite_correlation_minimale": round(
            float(cadre_sensibilite["correlation_rangs_spearman"].min()), 4
        ),
        "sensibilite_top10_commun_minimum": int(
            cadre_sensibilite["provinces_communes_top10"].min()
        ),
        "empreinte_entree": empreinte_sha256(entree),
        "empreinte_sortie": empreinte_sha256(sortie),
        "limites": [
            "L'abandon et le redoublement sont des moyennes non pondérées des niveaux.",
            "L'achèvement est régional et sert de contexte partagé entre provinces d'une région.",
            "Le score est relatif aux provinces observées pour chaque année scolaire.",
        ],
    }
    rapport_path.parent.mkdir(parents=True, exist_ok=True)
    rapport_path.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(description="Construit l'indice transparent du défi 1.")
    parseur.add_argument(
        "--entree", default="02_nettoyage/SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv"
    )
    parseur.add_argument(
        "--sortie", default="03_transformation/SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
    )
    parseur.add_argument(
        "--sensibilite", default="03_transformation/SCO-RISKBurkina_03-transformation_D1_data-scientist_sensibilite-ponderations_v1.csv"
    )
    parseur.add_argument(
        "--rapport", default="rapports_prives/06_qualite_indice_risque.json"
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]

    def chemin(valeur: str) -> Path:
        p = Path(valeur)
        return p if p.is_absolute() else racine / p

    rapport = transformer(
        chemin(args.entree), chemin(args.sortie), chemin(args.sensibilite), chemin(args.rapport)
    )
    print(
        f"Indice construit : {rapport['nombre_lignes']} lignes, "
        f"{rapport['nombre_provinces']} provinces."
    )
    print("Aucune valeur individuelle n'a été affichée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
