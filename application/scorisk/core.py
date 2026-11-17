from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


COLONNES_REQUISES = {
    "province",
    "annee_scolaire",
    "taux_abandon",
    "taux_redoublement",
    "taux_achevement",
    "score_risque",
}

ALIASES_PROVINCES_2025_VERS_GEOMETRIE_45 = {
    "sandbondtenga": "sanmatenga",
    "bassitenga": "oubritenga",
    "koosin": "kossi",
    "djelgodji": "soum",
    "karo peli": "soum",
    "dyamongou": "tapoa",
    "gobnangou": "tapoa",
    "lorum": "loroum",
    # Variantes d'orthographe présentes dans la géométrie publique historique.
    "komondjari": "komonjdjari",
    "kourittenga": "kouritenga",
}


def normaliser_libelle(valeur: str) -> str:
    texte = unicodedata.normalize("NFKD", str(valeur))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return " ".join(texte.casefold().replace("-", " ").replace("'", " ").split())


def charger_geojson(chemin: Path) -> dict:
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    if contenu.get("type") != "FeatureCollection":
        raise ValueError("Le fichier cartographique doit être un GeoJSON FeatureCollection.")
    if len(contenu.get("features", [])) not in {45, 47}:
        raise ValueError("Le référentiel cartographique doit contenir 45 ou 47 provinces.")
    return contenu


def provinces_geojson(geojson: dict) -> list[str]:
    return [f["properties"]["shapeName"] for f in geojson["features"]]


def correspondance_carte_sources(geojson: dict) -> pd.DataFrame:
    """Décrit les 47 territoires visibles et leurs 45 séries historiques sources."""
    lignes = []
    for feature in geojson["features"]:
        proprietes = feature["properties"]
        province = proprietes["shapeName"]
        lignes.append(
            {
                "province": province,
                "province_source": proprietes.get("province_source", province),
                "region_2025": proprietes.get("region_2025"),
                "statut_statistique": proprietes.get(
                    "statut_statistique", "Série historique directement rattachée"
                ),
            }
        )
    return pd.DataFrame(lignes)


def projeter_donnees_sur_carte(cadre: pd.DataFrame, geojson: dict) -> pd.DataFrame:
    """Projette les séries historiques sur les territoires 2025 sans les ventiler.

    Une série source peut alimenter deux territoires uniquement pour l'affichage.
    La colonne ``province_source`` permet d'éviter tout double comptage analytique.
    """
    correspondance = correspondance_carte_sources(geojson)
    source = cadre.copy().rename(columns={"province": "province_source"})
    source["cle_source"] = source["province_source"].map(normaliser_libelle)
    correspondance["cle_source"] = correspondance["province_source"].map(
        normaliser_libelle
    )
    resultat = correspondance.merge(source, on="cle_source", how="left", suffixes=("", "_donnee"))
    resultat["province_source"] = resultat["province_source"].fillna(
        resultat["province_source_donnee"]
    )
    resultat["province_geo"] = resultat["province"]
    resultat = resultat.drop(
        columns=["cle_source", "province_source_donnee", "region_2025_donnee"],
        errors="ignore",
    )
    if resultat["annee_scolaire"].isna().any():
        absentes = resultat.loc[resultat["annee_scolaire"].isna(), "province"].unique()
        raise ValueError("Séries sources absentes pour : " + ", ".join(sorted(absentes)))
    if "niveau_alerte" not in resultat:
        resultat["niveau_alerte"] = resultat["score_risque"].map(categorie_risque)
    if "fiabilite" not in resultat:
        resultat["fiabilite"] = np.nan
    return resultat


def charger_referentiel_territorial(chemin: Path) -> dict:
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    if len(contenu.get("regions", [])) != 17:
        raise ValueError("Le référentiel territorial doit contenir 17 régions.")
    return contenu


def charger_referentiel_provinces_historiques(chemin: Path) -> dict:
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    lignes = contenu.get("provinces", [])
    if len(lignes) != 45:
        raise ValueError("Le référentiel historique doit contenir 45 provinces.")
    return contenu


def construire_hierarchie_par_champ(
    referentiel: dict, provinces_carte: list[str], champ_region: str
) -> dict[str, str]:
    """Rattache chaque géométrie provinciale au champ régional demandé."""
    carte_norm = {normaliser_libelle(p): p for p in provinces_carte}
    correspondance: dict[str, str] = {}
    for ligne in referentiel["provinces"]:
        cle = ALIASES_PROVINCES_2025_VERS_GEOMETRIE_45.get(
            normaliser_libelle(ligne["province"]),
            normaliser_libelle(ligne["province"]),
        )
        province_geo = carte_norm.get(cle)
        if province_geo:
            correspondance[province_geo] = ligne[champ_region]
    manquantes = sorted(set(provinces_carte) - set(correspondance))
    if manquantes:
        raise ValueError(
            "Provinces sans rattachement régional : " + ", ".join(manquantes)
        )
    return correspondance


def construire_contours_regions(
    geojson: dict, rattachement: dict[str, str], precision: int = 6
) -> dict[str, tuple[list[float | None], list[float | None]]]:
    """Construit les contours extérieurs régionaux sans dépendance SIG.

    Deux segments provinciaux identiques appartenant à la même région sont
    intérieurs : ils s'annulent. Les segments restants forment la limite de
    la région. Des séparateurs ``None`` permettent un tracé cartographique.
    """
    segments_par_region: dict[str, dict[tuple, tuple]] = {}
    for feature in geojson["features"]:
        province = feature["properties"]["shapeName"]
        region = rattachement[province]
        segments = segments_par_region.setdefault(region, {})
        geometrie = feature["geometry"]
        polygones = (
            [geometrie["coordinates"]]
            if geometrie["type"] == "Polygon"
            else geometrie["coordinates"]
        )
        for polygone in polygones:
            for anneau in polygone:
                for debut, fin in zip(anneau, anneau[1:]):
                    a = tuple(round(float(v), precision) for v in debut)
                    b = tuple(round(float(v), precision) for v in fin)
                    cle = tuple(sorted((a, b)))
                    if cle in segments:
                        del segments[cle]
                    else:
                        segments[cle] = (a, b)

    contours = {}
    for region, segments in segments_par_region.items():
        longitudes: list[float | None] = []
        latitudes: list[float | None] = []
        for debut, fin in segments.values():
            longitudes.extend([debut[0], fin[0], None])
            latitudes.extend([debut[1], fin[1], None])
        contours[region] = (longitudes, latitudes)
    return contours


def calculer_cadrage_geojson(
    geojson: dict, provinces_cibles: list[str]
) -> tuple[dict[str, float], float]:
    """Calcule un centre et un zoom pour remplir la carte avec les provinces visées."""
    cibles = set(provinces_cibles)
    longitudes: list[float] = []
    latitudes: list[float] = []
    for feature in geojson["features"]:
        if feature["properties"]["shapeName"] not in cibles:
            continue
        geometrie = feature["geometry"]
        polygones = (
            [geometrie["coordinates"]]
            if geometrie["type"] == "Polygon"
            else geometrie["coordinates"]
        )
        for polygone in polygones:
            for anneau in polygone:
                for longitude, latitude in anneau:
                    longitudes.append(float(longitude))
                    latitudes.append(float(latitude))
    if not longitudes:
        return {"lat": 12.35, "lon": -1.60}, 5.95

    ouest, est = min(longitudes), max(longitudes)
    sud, nord = min(latitudes), max(latitudes)
    centre = {"lat": (sud + nord) / 2, "lon": (ouest + est) / 2}
    largeur = max(est - ouest, 0.05)
    hauteur = max(nord - sud, 0.05)
    # Approximation adaptée au panneau 2:1 de l'application. La marge évite
    # de couper les contours et l'échelle est bornée pour les petites régions.
    zoom_horizontal = math.log2((360 / largeur) * (820 / 512)) - 0.55
    zoom_vertical = math.log2((360 / hauteur) * (700 / 512)) - 0.55
    zoom = max(6.4, min(8.6, zoom_horizontal, zoom_vertical))
    return centre, round(zoom, 2)


def construire_hierarchie_historique(
    referentiel: dict, provinces_carte: list[str]
) -> dict[str, str]:
    """Associe les 45 géométries historiques aux 17 régions actuelles.

    Les deux provinces créées en 2025 restent incluses dans leur géométrie
    provinciale historique tant que la carte départementale n'est pas reconstruite.
    """
    carte_norm = {normaliser_libelle(p): p for p in provinces_carte}
    correspondance: dict[str, str] = {}
    for region in referentiel["regions"]:
        nom_region = region["region"]
        for province_actuelle in region["provinces"]:
            cle_actuelle = normaliser_libelle(province_actuelle)
            cle_historique = ALIASES_PROVINCES_2025_VERS_GEOMETRIE_45.get(
                cle_actuelle, cle_actuelle
            )
            province_geo = carte_norm.get(cle_historique)
            if province_geo:
                region_precedente = correspondance.get(province_geo)
                if region_precedente and region_precedente != nom_region:
                    raise ValueError(
                        f"La géométrie {province_geo} est rattachée à deux régions."
                    )
                correspondance[province_geo] = nom_region

    manquantes = sorted(set(provinces_carte) - set(correspondance))
    if manquantes:
        raise ValueError(
            "Provinces historiques sans région actuelle : " + ", ".join(manquantes)
        )
    return correspondance


def categorie_risque(score: float) -> str:
    if score >= 75:
        return "Critique"
    if score >= 55:
        return "Élevé"
    if score >= 35:
        return "Modéré"
    return "Faible"


def _graine(province: str, annee: str) -> int:
    cle = f"{province}|{annee}".encode("utf-8")
    return int(hashlib.sha256(cle).hexdigest()[:8], 16)


def generer_donnees_demo(provinces: list[str]) -> pd.DataFrame:
    """Génère des données fictives déterministes, uniquement pour tester l'interface."""
    annees = [
        "2017-2018",
        "2018-2019",
        "2019-2020",
        "2020-2021",
        "2021-2022",
        "2022-2023",
        "2023-2024",
        "2024-2025",
    ]
    lignes = []
    for p_index, province in enumerate(provinces):
        pression = (p_index % 12) / 11
        for a_index, annee in enumerate(annees):
            rng = np.random.default_rng(_graine(province, annee))
            abandon = float(
                np.clip(2.2 + 10.5 * pression + 0.22 * a_index + rng.normal(0, 0.8), 0.5, 18)
            )
            redoublement = float(
                np.clip(3.5 + 12 * pression + rng.normal(0, 0.9), 1, 22)
            )
            achevement = float(
                np.clip(90 - 42 * pression - 0.25 * a_index + rng.normal(0, 2.2), 35, 96)
            )
            score = float(
                np.clip(
                    45 * (abandon / 18)
                    + 25 * (redoublement / 22)
                    + 30 * ((100 - achevement) / 65),
                    0,
                    100,
                )
            )
            lignes.append(
                {
                    "province": province,
                    "annee_scolaire": annee,
                    "taux_abandon": round(abandon, 2),
                    "taux_redoublement": round(redoublement, 2),
                    "taux_achevement": round(achevement, 2),
                    "score_risque": round(score, 1),
                    "fiabilite": round(float(np.clip(0.62 + rng.random() * 0.28, 0, 1)), 2),
                }
            )
    cadre = pd.DataFrame(lignes)
    cadre["niveau_alerte"] = cadre["score_risque"].map(categorie_risque)
    return cadre


def valider_donnees(cadre: pd.DataFrame, provinces_carte: list[str]) -> list[str]:
    erreurs = []
    manquantes = sorted(COLONNES_REQUISES - set(cadre.columns))
    if manquantes:
        erreurs.append("Colonnes absentes : " + ", ".join(manquantes))
        return erreurs

    if cadre.empty:
        erreurs.append("Le fichier d'indicateurs ne contient aucune ligne.")
        return erreurs

    for colonne in ["taux_abandon", "taux_redoublement", "taux_achevement", "score_risque"]:
        valeurs = pd.to_numeric(cadre[colonne], errors="coerce")
        if valeurs.isna().any():
            erreurs.append(f"La colonne {colonne} contient des valeurs non numériques.")
    scores = pd.to_numeric(cadre["score_risque"], errors="coerce")
    if ((scores < 0) | (scores > 100)).any():
        erreurs.append("Le score de risque doit être compris entre 0 et 100.")

    carte_norm = {normaliser_libelle(p) for p in provinces_carte}
    donnees_norm = set()
    for province in cadre["province"].dropna().unique():
        cle = normaliser_libelle(province)
        donnees_norm.add(
            cle
            if cle in carte_norm
            else ALIASES_PROVINCES_2025_VERS_GEOMETRIE_45.get(cle, cle)
        )
    absentes_carte = sorted(donnees_norm - carte_norm)
    if absentes_carte:
        erreurs.append(
            f"{len(absentes_carte)} libellé(s) de province ne correspondent pas à la carte."
        )
    return erreurs


def preparer_jointure(cadre: pd.DataFrame, provinces_carte: list[str]) -> pd.DataFrame:
    correspondance = {normaliser_libelle(p): p for p in provinces_carte}
    resultat = cadre.copy()
    def province_geo(valeur: str) -> str | None:
        cle = normaliser_libelle(valeur)
        return correspondance.get(
            cle if cle in correspondance else ALIASES_PROVINCES_2025_VERS_GEOMETRIE_45.get(cle, cle)
        )

    resultat["province_geo"] = resultat["province"].map(province_geo)
    if "niveau_alerte" not in resultat:
        resultat["niveau_alerte"] = resultat["score_risque"].map(categorie_risque)
    if "fiabilite" not in resultat:
        resultat["fiabilite"] = np.nan
    return resultat


def recommandations(ligne: pd.Series) -> list[str]:
    actions = []
    score = float(ligne.get("score_risque", 0))
    if score >= 75:
        actions.append(
            "0-3 mois : lancer une revue territoriale rapide et confirmer l'alerte avec les services provinciaux."
        )
    if float(ligne["taux_abandon"]) >= 8:
        actions.append(
            "Avant la prochaine rentrée : renforcer le suivi des absences, la recherche des élèves sortis et le retour à l'école."
        )
    if float(ligne.get("rang_redoublement", 0)) >= 75:
        actions.append(
            "3-12 mois : cibler le soutien pédagogique, le rattrapage et les classes où le redoublement est le plus défavorable."
        )
    if float(ligne.get("rang_non_achevement", 0)) >= 75:
        actions.append(
            "6-12 mois : coordonner un plan régional de maintien jusqu'au CM2 et examiner les obstacles à la continuité."
        )
    if not actions:
        actions.append(
            "Suivi annuel : maintenir la surveillance et documenter les pratiques locales efficaces."
        )
    actions.append(
        "Validation : croiser le signal avec les fermetures d'écoles, les déplacements et les retours de terrain avant toute allocation."
    )
    return actions

