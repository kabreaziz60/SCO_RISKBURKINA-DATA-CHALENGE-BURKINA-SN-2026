from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from outils_excel import empreinte_sha256


ANNEE_REFERENCE = "2024-2025"
SEUIL_ELEVE = 55
SEUIL_CRITIQUE = 75


def tendance_recente(groupe: pd.DataFrame) -> float:
    recent = groupe.sort_values("annee_scolaire").tail(3)
    if len(recent) < 2:
        return float("nan")
    x = np.arange(len(recent), dtype=float)
    return round(float(np.polyfit(x, recent["score_risque"], 1)[0]), 2)


def libelle_tendance(pente: float) -> str:
    if pente >= 5:
        return "Forte hausse"
    if pente >= 2:
        return "Hausse"
    if pente > -2:
        return "Stable"
    if pente > -5:
        return "Baisse"
    return "Forte baisse"


def niveau_priorite(score: float, pente: float) -> str:
    if score >= SEUIL_CRITIQUE or (score >= SEUIL_ELEVE and pente >= 2):
        return "Priorité immédiate"
    if score >= SEUIL_ELEVE or (score >= 35 and pente >= 5):
        return "Surveillance renforcée"
    return "Veille"


def facteur_dominant(ligne: pd.Series) -> str:
    contributions = {
        "Abandon provincial": 0.50 * float(ligne["rang_abandon"]),
        "Redoublement provincial": 0.30 * float(ligne["rang_redoublement"]),
        "Non-achèvement régional": 0.20 * float(ligne["rang_non_achevement"]),
    }
    return max(contributions, key=contributions.get)


def recommandation(facteur: str, pente: float, persistance: int) -> str:
    actions = {
        "Abandon provincial": (
            "Renforcer le suivi précoce des absences, la recherche des élèves sortis "
            "et les dispositifs de retour à l'école."
        ),
        "Redoublement provincial": (
            "Cibler le soutien pédagogique, le rattrapage et l'accompagnement des "
            "classes où le redoublement est le plus élevé."
        ),
        "Non-achèvement régional": (
            "Coordonner avec la région un plan de maintien jusqu'au CM2 et examiner "
            "les obstacles à la continuité du parcours primaire."
        ),
    }
    action = actions[facteur]
    if pente >= 5:
        action += " Déclencher une revue territoriale rapide car le risque augmente fortement."
    elif pente >= 2:
        action += " Vérifier rapidement les causes de la hausse récente."
    if persistance >= 4:
        action += " Inscrire la réponse dans un plan pluriannuel, le risque étant persistant."
    return action


def construire(
    entree: Path,
    sortie_priorites: Path,
    sortie_regions: Path,
    rapport_path: Path,
) -> dict:
    donnees = pd.read_csv(entree)
    historique = donnees[donnees["annee_scolaire"] <= ANNEE_REFERENCE].copy()
    reference = historique[historique["annee_scolaire"] == ANNEE_REFERENCE].copy()
    if len(reference) != historique["province"].nunique():
        raise RuntimeError("L'année de référence n'a pas une ligne par province.")

    pentes = historique.groupby("province").apply(
        tendance_recente, include_groups=False
    )
    persistance = (
        historique.assign(risque_eleve=historique["score_risque"] >= SEUIL_ELEVE)
        .groupby("province")["risque_eleve"]
        .sum()
    )
    reference["tendance_score_3_ans"] = reference["province"].map(pentes)
    reference["tendance_recente"] = reference["tendance_score_3_ans"].map(
        libelle_tendance
    )
    reference["annees_risque_eleve"] = (
        reference["province"].map(persistance).astype(int)
    )
    reference["facteur_dominant"] = reference.apply(facteur_dominant, axis=1)
    reference["priorite_decision"] = reference.apply(
        lambda ligne: niveau_priorite(
            float(ligne["score_risque"]), float(ligne["tendance_score_3_ans"])
        ),
        axis=1,
    )
    reference["recommandation"] = reference.apply(
        lambda ligne: recommandation(
            str(ligne["facteur_dominant"]),
            float(ligne["tendance_score_3_ans"]),
            int(ligne["annees_risque_eleve"]),
        ),
        axis=1,
    )
    reference = reference.sort_values(
        ["score_risque", "tendance_score_3_ans"], ascending=False
    ).reset_index(drop=True)
    reference["rang_national"] = np.arange(1, len(reference) + 1)
    reference["interpretation_facteur"] = (
        "Contribution dominante au score relatif ; ne constitue pas une preuve de causalité."
    )

    colonnes = [
        "rang_national",
        "province",
        "region_historique",
        "region_2025",
        "annee_scolaire",
        "score_risque",
        "niveau_alerte",
        "priorite_decision",
        "tendance_score_3_ans",
        "tendance_recente",
        "annees_risque_eleve",
        "facteur_dominant",
        "taux_abandon",
        "taux_redoublement",
        "taux_achevement",
        "fiabilite",
        "statut_qualite",
        "recommandation",
        "interpretation_facteur",
    ]
    sortie_priorites.parent.mkdir(parents=True, exist_ok=True)
    reference[colonnes].to_csv(
        sortie_priorites, index=False, encoding="utf-8-sig"
    )

    regions = (
        reference.groupby("region_historique", as_index=False)
        .agg(
            nombre_provinces=("province", "nunique"),
            score_median=("score_risque", "median"),
            tendance_moyenne_3_ans=("tendance_score_3_ans", "mean"),
            priorites_immediates=(
                "priorite_decision",
                lambda s: int((s == "Priorité immédiate").sum()),
            ),
            surveillances_renforcees=(
                "priorite_decision",
                lambda s: int((s == "Surveillance renforcée").sum()),
            ),
        )
    )
    sommet = reference.loc[
        reference.groupby("region_historique")["score_risque"].idxmax(),
        ["region_historique", "province", "score_risque"],
    ].rename(
        columns={"province": "province_plus_risquee", "score_risque": "score_max"}
    )
    regions = regions.merge(sommet, on="region_historique", how="left")
    regions["part_provinces_priorite_immediate"] = (
        regions["priorites_immediates"] / regions["nombre_provinces"]
    ).round(4)
    regions = regions.sort_values(
        ["part_provinces_priorite_immediate", "score_median"], ascending=False
    )
    regions.to_csv(sortie_regions, index=False, encoding="utf-8-sig")

    repartition = reference["priorite_decision"].value_counts().to_dict()
    facteurs = reference["facteur_dominant"].value_counts().to_dict()
    rapport = {
        "rapport": "interpretation_priorites_decrochage",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "annee_reference": ANNEE_REFERENCE,
        "nombre_provinces": int(len(reference)),
        "nombre_regions_historiques": int(regions["region_historique"].nunique()),
        "repartition_priorites": {str(k): int(v) for k, v in repartition.items()},
        "facteurs_dominants": {str(k): int(v) for k, v in facteurs.items()},
        "methode_tendance": "Pente linéaire du score sur les trois dernières années observées.",
        "seuils": {
            "score_eleve": SEUIL_ELEVE,
            "score_critique": SEUIL_CRITIQUE,
            "hausse": 2,
            "forte_hausse": 5,
        },
        "empreinte_entree": empreinte_sha256(entree),
        "empreinte_priorites": empreinte_sha256(sortie_priorites),
        "empreinte_regions": empreinte_sha256(sortie_regions),
        "limites": [
            "Les priorités sont relatives aux 45 provinces observées.",
            "Les résultats utilisent les 13 régions historiques présentes dans les sources.",
            "Le facteur dominant décrit une contribution au score, pas une cause démontrée.",
            "L'achèvement est régional et partagé entre les provinces d'une même région.",
            "Les recommandations doivent être confrontées à la connaissance locale avant action.",
        ],
    }
    rapport_path.parent.mkdir(parents=True, exist_ok=True)
    rapport_path.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Produit les priorités et recommandations du défi 1."
    )
    parseur.add_argument(
        "--entree", default="03_transformation/SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
    )
    parseur.add_argument(
        "--priorites", default="05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_priorites-2024-2025_v1.csv"
    )
    parseur.add_argument(
        "--regions", default="05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_synthese-regions-2024-2025_v1.csv"
    )
    parseur.add_argument(
        "--rapport", default="rapports_prives/09_interpretation_priorites.json"
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]

    def chemin(valeur: str) -> Path:
        p = Path(valeur)
        return p if p.is_absolute() else racine / p

    rapport = construire(
        chemin(args.entree),
        chemin(args.priorites),
        chemin(args.regions),
        chemin(args.rapport),
    )
    print(
        f"Interprétation terminée : {rapport['nombre_provinces']} provinces, "
        f"{rapport['nombre_regions_historiques']} régions historiques."
    )
    print("Le rapport console ne contient aucune valeur provinciale.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
