from __future__ import annotations

import csv
import json
from pathlib import Path


RACINE = Path(__file__).resolve().parents[1]
ENTREE = RACINE / "config" / "referentiel_provinces_historiques.json"
SORTIE = RACINE / "03_transformation" / "SCO-RISKBurkina_03-transformation_D1_architect_correspondance-45-provinces-17-regions_v1.csv"


def commentaire(province: str) -> str:
    if province == "Soum":
        return "La série historique inclut le territoire de Karo-Peli ; aucune ventilation artificielle."
    if province == "Tapoa":
        return "La série historique inclut le territoire de Dyamongou ; aucune ventilation artificielle."
    return "Correspondance directe de la province historique vers la région 2025."


def main() -> None:
    contenu = json.loads(ENTREE.read_text(encoding="utf-8"))
    lignes = []
    for item in contenu["provinces"]:
        lignes.append(
            {
                "province_historique": item["province"],
                "ancienne_region_13": item["region_historique"],
                "nouvelle_region_17": item["region_2025"],
                "methode": "Regroupement territorial au niveau province",
                "statut": "Reconstitué",
                "commentaire": commentaire(item["province"]),
            }
        )

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", newline="", encoding="utf-8-sig") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
        writer.writeheader()
        writer.writerows(lignes)

    regions = {ligne["nouvelle_region_17"] for ligne in lignes}
    if len(lignes) != 45 or len(regions) != 17:
        raise ValueError(f"Correspondance invalide : {len(lignes)} provinces, {len(regions)} régions.")
    print(f"Correspondance exportée : {len(lignes)} provinces historiques vers {len(regions)} régions.")


if __name__ == "__main__":
    main()
