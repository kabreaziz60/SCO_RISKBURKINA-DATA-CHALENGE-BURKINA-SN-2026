from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


RACINE = Path(__file__).resolve().parents[1]
SOURCE = RACINE / "01_collecte" / "Rapport_statistique_mensuel_ESU_Février_2026.csv"
NETTOYE = RACINE / "02_nettoyage" / (
    "SCO-RISKBurkina_02-nettoyage_D1_engineer_"
    "esu-regions-fevrier-2026-propre_v1.csv"
)
TRANSFORME = RACINE / "03_transformation" / (
    "SCO-RISKBurkina_03-transformation_D1_data-scientist_"
    "indice-pression-esu-regions_v1.csv"
)
ANALYSE = RACINE / "04_analyse" / (
    "SCO-RISKBurkina_04-analyse_D1_data-analyst_"
    "croisement-risque-pression-esu-2025-2026_v1.csv"
)
INTERPRETATION = RACINE / "05_interpretation" / (
    "SCO-RISKBurkina_05-interpretation_D1_data-analyst_"
    "priorites-contexte-urgence_v1.csv"
)
PROJECTIONS = RACINE / "04_analyse" / (
    "SCO-RISKBurkina_04-analyse_D1_data-scientist_"
    "projection-2025-2027_v2.csv"
)
REFERENTIEL = RACINE / "config" / "referentiel_administratif_2025.json"
RAPPORT_QUALITE = RACINE / "rapports_prives" / "10_qualite_contexte_esu.json"

DATE_REFERENCE = "2026-02-28"
SOURCE_TITRE = "Rapport statistique mensuel ESU, février 2026"
SOURCE_INSTITUTION = "MENAPLN/DGESS - Secrétariat technique de l'Education en Situation d'Urgence"
SOURCE_FICHIER = SOURCE.name

REGIONS_SOURCE = {
    "BANKUI": "Bankui",
    "DJR": "Djoro",
    "DJORO": "Djoro",
    "GOULMOU": "Goulmou",
    "GUIRIKO": "Guiriko",
    "KADIOGO": "Kadiogo",
    "KOULS": "Koulse",
    "KOULSE": "Koulse",
    "LIPTAKO": "Liptako",
    "NAKAMB": "Nakambe",
    "NAKAMBE": "Nakambe",
    "NANDO": "Nando",
    "NAZINON": "Nazinon",
    "OUBRI": "Oubri",
    "SIRBA": "Sirba",
    "SOUM": "Soum",
    "SOUROU": "Sourou",
    "TANNOUNYAN": "Tannounyan",
    "TAPOA": "Tapoa",
    "YAADGA": "Yaadga",
}


def entier(valeur: object) -> int:
    texte = re.sub(r"\D", "", str(valeur or ""))
    return int(texte) if texte else 0


def cle_region(valeur: object) -> str:
    texte = unicodedata.normalize("NFKD", str(valeur or ""))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"[^A-Z]", "", texte.upper())


def nom_region(valeur: object) -> str:
    cle = cle_region(valeur)
    if cle not in REGIONS_SOURCE:
        raise ValueError(f"Région ESU non reconnue : {valeur!r} (clé {cle!r})")
    return REGIONS_SOURCE[cle]


def extraire_table(
    brut: pd.DataFrame,
    page: int,
    debut: int,
    fin: int,
    colonne_region: str,
    colonnes: dict[str, str],
) -> pd.DataFrame:
    lignes = brut[
        (brut["page"].astype(int) == page)
        & brut["ligne"].astype(int).between(debut, fin)
    ].copy()
    lignes["region_2025"] = lignes[colonne_region].map(nom_region)
    resultat = lignes[["region_2025"]].copy()
    for sortie, source in colonnes.items():
        resultat[sortie] = lignes[source].map(entier)
    return resultat


def categorie_pression(score: float) -> str:
    if score >= 75:
        return "Très élevée"
    if score >= 55:
        return "Élevée"
    if score >= 35:
        return "Modérée"
    return "Faible"


def action_contextuelle(ligne: pd.Series) -> str:
    if ligne["double_alerte"]:
        return (
            "Vérifier rapidement la situation sur le terrain avec la DGESS et l'ESU, "
            "puis déployer un plan conjoint de continuité, de suivi des absences et de retour à l'école."
        )
    if ligne["indice_pression_esu"] >= 55:
        return (
            "Renforcer les capacités d'accueil, les dispositifs temporaires ou à distance "
            "et le suivi des élèves déplacés, après validation locale."
        )
    if ligne["score_risque_projete_region"] >= 55:
        return (
            "Examiner en priorité les facteurs scolaires du risque et organiser le suivi "
            "précoce des absences, sans attribuer automatiquement la situation au contexte sécuritaire."
        )
    return "Maintenir la veille conjointe des indicateurs scolaires et du contexte d'urgence."


def construire() -> dict:
    brut = pd.read_csv(SOURCE, sep=";", dtype=str)
    # La colonne de remarque est une métadonnée de collecte, pas une donnée statistique.
    brut = brut.drop(columns=["remarque_collecte"], errors="ignore")

    rouvertes = extraire_table(
        brut, 8, 20, 34, "c1", {"structures_rouvertes_primaire": "c3"}
    )
    delocalisees = extraire_table(
        brut, 11, 20, 30, "c1", {"structures_delocalisees_primaire": "c3"}
    )
    edi = extraire_table(
        brut,
        14,
        6,
        22,
        "c1",
        {
            "edi_primaire_garcons": "c5",
            "edi_primaire_filles": "c6",
            "edi_primaire_total": "c7",
        },
    )

    referentiel = json.loads(REFERENTIEL.read_text(encoding="utf-8"))
    regions = pd.DataFrame(
        {"region_2025": [r["region"] for r in referentiel["regions"]]}
    )
    propre = (
        regions.merge(rouvertes, on="region_2025", how="left", validate="one_to_one")
        .merge(delocalisees, on="region_2025", how="left", validate="one_to_one")
        .merge(edi, on="region_2025", how="left", validate="one_to_one")
    )
    colonnes_numeriques = [
        "structures_rouvertes_primaire",
        "structures_delocalisees_primaire",
        "edi_primaire_garcons",
        "edi_primaire_filles",
        "edi_primaire_total",
    ]
    propre[colonnes_numeriques] = propre[colonnes_numeriques].fillna(0).astype(int)
    propre.insert(1, "date_reference", DATE_REFERENCE)
    propre["source_document"] = SOURCE_TITRE
    propre["source_institution"] = SOURCE_INSTITUTION
    propre["source_fichier"] = SOURCE_FICHIER
    propre["niveau_geographique"] = "Région (découpage administratif 2025)"
    propre["limite_interpretation"] = (
        "Effectifs et nombres de structures, non rapportés à la population scolaire; "
        "aucune causalité avec le décrochage n'est déduite."
    )

    controles = {
        "regions": int(propre["region_2025"].nunique()),
        "rouvertes_primaire": int(propre["structures_rouvertes_primaire"].sum()),
        "delocalisees_primaire": int(propre["structures_delocalisees_primaire"].sum()),
        "edi_primaire": int(propre["edi_primaire_total"].sum()),
        "edi_coherence_sexe": bool(
            (
                propre["edi_primaire_garcons"] + propre["edi_primaire_filles"]
                == propre["edi_primaire_total"]
            ).all()
        ),
    }
    attendus = {
        "regions": 17,
        "rouvertes_primaire": 1840,
        "delocalisees_primaire": 492,
        "edi_primaire": 436683,
        "edi_coherence_sexe": True,
    }
    if controles != attendus:
        raise RuntimeError(f"Contrôles ESU non conformes : {controles} != {attendus}")

    NETTOYE.parent.mkdir(parents=True, exist_ok=True)
    propre.to_csv(NETTOYE, index=False, encoding="utf-8-sig")

    transforme = propre.copy()
    transforme["rang_edi"] = transforme["edi_primaire_total"].rank(pct=True) * 100
    transforme["rang_delocalisation"] = (
        transforme["structures_delocalisees_primaire"].rank(pct=True) * 100
    )
    transforme["indice_pression_esu"] = (
        0.60 * transforme["rang_edi"] + 0.40 * transforme["rang_delocalisation"]
    ).round(2)
    transforme["niveau_pression_esu"] = transforme["indice_pression_esu"].map(
        categorie_pression
    )
    transforme["formule_indice"] = "60% rang EDI primaire + 40% rang structures primaires délocalisées"
    transforme.to_csv(TRANSFORME, index=False, encoding="utf-8-sig")

    projections = pd.read_csv(PROJECTIONS)
    projections = projections[projections["annee_cible"] == "2025-2026"].copy()
    risque_regions = (
        projections.groupby("region_2025", as_index=False)["score_prevu"]
        .median()
        .rename(columns={"score_prevu": "score_risque_projete_region"})
    )
    croisement = transforme.merge(
        risque_regions, on="region_2025", how="left", validate="one_to_one"
    )
    if croisement["score_risque_projete_region"].isna().any():
        manquantes = croisement.loc[
            croisement["score_risque_projete_region"].isna(), "region_2025"
        ].tolist()
        raise RuntimeError(f"Régions sans projection SCO-RISK : {manquantes}")
    croisement["score_risque_projete_region"] = croisement[
        "score_risque_projete_region"
    ].round(2)
    croisement["double_alerte"] = (
        (croisement["score_risque_projete_region"] >= 55)
        & (croisement["indice_pression_esu"] >= 55)
    )
    croisement["regle_double_alerte"] = (
        "score SCO-RISK régional médian >=55 et indice de pression ESU >=55"
    )
    croisement["prudence"] = (
        "Croisement descriptif d'aide au ciblage; association et causalité ne sont pas établies."
    )
    croisement.to_csv(ANALYSE, index=False, encoding="utf-8-sig")

    interpretation = croisement[
        [
            "region_2025",
            "score_risque_projete_region",
            "indice_pression_esu",
            "niveau_pression_esu",
            "double_alerte",
            "edi_primaire_total",
            "structures_delocalisees_primaire",
            "structures_rouvertes_primaire",
        ]
    ].copy()
    interpretation["action_proposee"] = interpretation.apply(
        action_contextuelle, axis=1
    )
    interpretation["validation_requise"] = (
        "Oui - confronter aux informations locales les plus récentes avant toute décision."
    )
    interpretation = interpretation.sort_values(
        ["double_alerte", "indice_pression_esu", "score_risque_projete_region"],
        ascending=False,
    )
    interpretation.to_csv(INTERPRETATION, index=False, encoding="utf-8-sig")

    rapport = {
        "rapport": "qualite_contexte_esu",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE.relative_to(RACINE)),
        "controles": controles,
        "fichiers_produits": [
            str(p.relative_to(RACINE))
            for p in (NETTOYE, TRANSFORME, ANALYSE, INTERPRETATION)
        ],
        "principe": (
            "Le contexte ESU est analysé séparément de l'indice SCO-RISK et ne prouve "
            "pas une relation causale avec le décrochage."
        ),
    }
    RAPPORT_QUALITE.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT_QUALITE.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rapport


if __name__ == "__main__":
    resultat = construire()
    print("Contexte ESU intégré et contrôlé.")
    print(json.dumps(resultat["controles"], ensure_ascii=False))
