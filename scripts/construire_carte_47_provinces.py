from __future__ import annotations

import json
import csv
import zipfile
from math import hypot
from pathlib import Path


RACINE = Path(__file__).resolve().parents[1]
ARCHIVE = RACINE / "tmp" / "datapack" / "carto" / "bfa_admin_boundaries.geojson.zip"
SORTIE = RACINE / "application" / "data" / "provinces_47_2025.geojson"
SORTIE_CORRESPONDANCE = RACINE / "03_transformation" / "SCO-RISKBurkina_03-transformation_D1_architect_correspondance-47-provinces-45-series_v1.csv"

SOURCES_HISTORIQUES = {
    "Bassitenga": "Oubritenga",
    "Djelgodji": "Soum",
    "Dyamongou": "Tapoa",
    "Gobnangou": "Tapoa",
    "Karo-Peli": "Soum",
    "Koosin": "Kossi",
    "Kourittenga": "Kouritenga",
    "Lorum": "Loroum",
    "Sandbondtenga": "Sanmatenga",
}

NOMS_OFFICIELS = {
    "Komandjari": "Komondjari",
    "Kossin": "Koosin",
}

PROVINCES_SCINDEES = {"Djelgodji", "Karo-Peli", "Dyamongou", "Gobnangou"}


def distance_au_segment(point: list[float], debut: list[float], fin: list[float]) -> float:
    x, y = point[:2]
    x1, y1 = debut[:2]
    x2, y2 = fin[:2]
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def simplifier_ligne(points: list[list[float]], tolerance: float) -> list[list[float]]:
    if len(points) <= 2:
        return points
    distances = [distance_au_segment(p, points[0], points[-1]) for p in points[1:-1]]
    maximum = max(distances, default=0.0)
    if maximum <= tolerance:
        return [points[0], points[-1]]
    index = distances.index(maximum) + 1
    gauche = simplifier_ligne(points[: index + 1], tolerance)
    droite = simplifier_ligne(points[index:], tolerance)
    return gauche[:-1] + droite


def simplifier_anneau(anneau: list[list[float]], tolerance: float = 0.003) -> list[list[float]]:
    points = anneau[:-1] if anneau and anneau[0][:2] == anneau[-1][:2] else anneau[:]
    if len(points) <= 5:
        return anneau
    ancre_a = min(range(len(points)), key=lambda i: (points[i][0], points[i][1]))
    points = points[ancre_a:] + points[:ancre_a]
    ancre_b = max(
        range(1, len(points)),
        key=lambda i: (points[i][0] - points[0][0]) ** 2 + (points[i][1] - points[0][1]) ** 2,
    )
    partie_a = simplifier_ligne(points[: ancre_b + 1], tolerance)
    partie_b = simplifier_ligne(points[ancre_b:] + [points[0]], tolerance)
    resultat = partie_a[:-1] + partie_b[:-1]
    if len(resultat) < 3:
        resultat = points[:3]
    resultat = [[round(p[0], 5), round(p[1], 5)] for p in resultat]
    return resultat + [resultat[0]]


def simplifier_geometrie(geometrie: dict) -> dict:
    polygones = (
        [geometrie["coordinates"]]
        if geometrie["type"] == "Polygon"
        else geometrie["coordinates"]
    )
    simplifies = [
        [simplifier_anneau(anneau) for anneau in polygone]
        for polygone in polygones
    ]
    return {
        "type": geometrie["type"],
        "coordinates": simplifies[0] if geometrie["type"] == "Polygon" else simplifies,
    }


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        carte = json.loads(archive.read("bfa_admin2.geojson"))

    for feature in carte["features"]:
        proprietes = feature["properties"]
        province = NOMS_OFFICIELS.get(proprietes["adm2_name"], proprietes["adm2_name"])
        proprietes["shapeName"] = province
        proprietes["region_2025"] = proprietes["adm1_name"]
        proprietes["province_source"] = SOURCES_HISTORIQUES.get(province, province)
        proprietes["statut_statistique"] = (
            "Valeur héritée de l'ancienne province source ; non désagrégée"
            if province in PROVINCES_SCINDEES
            else "Série historique directement rattachée"
        )
        feature["geometry"] = simplifier_geometrie(feature["geometry"])

    provinces = {f["properties"]["shapeName"] for f in carte["features"]}
    regions = {f["properties"]["region_2025"] for f in carte["features"]}
    sources = {f["properties"]["province_source"] for f in carte["features"]}
    if (len(provinces), len(regions), len(sources)) != (47, 17, 45):
        raise ValueError(
            f"Carte invalide : {len(provinces)} provinces, {len(regions)} régions, "
            f"{len(sources)} séries sources."
        )

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(carte, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    with SORTIE_CORRESPONDANCE.open("w", newline="", encoding="utf-8-sig") as fichier:
        colonnes = ["province_2025", "region_2025", "province_source_historique", "statut_statistique"]
        writer = csv.DictWriter(fichier, fieldnames=colonnes)
        writer.writeheader()
        for feature in sorted(carte["features"], key=lambda f: f["properties"]["shapeName"]):
            proprietes = feature["properties"]
            writer.writerow(
                {
                    "province_2025": proprietes["shapeName"],
                    "region_2025": proprietes["region_2025"],
                    "province_source_historique": proprietes["province_source"],
                    "statut_statistique": proprietes["statut_statistique"],
                }
            )
    print("Carte 2025 construite : 47 provinces, 17 régions, 45 séries historiques.")


if __name__ == "__main__":
    main()
