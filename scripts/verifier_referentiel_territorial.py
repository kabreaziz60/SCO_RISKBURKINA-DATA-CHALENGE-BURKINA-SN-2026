from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    racine = Path(__file__).resolve().parents[1]
    chemin = racine / "config" / "referentiel_administratif_2025.json"
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    regions = contenu.get("regions", [])
    provinces = [p for region in regions for p in region.get("provinces", [])]
    doublons = sorted(p for p, n in Counter(provinces).items() if n > 1)

    erreurs = []
    if len(regions) != 17:
        erreurs.append(f"17 régions attendues, {len(regions)} trouvées.")
    if len(provinces) != 47:
        erreurs.append(f"47 provinces attendues, {len(provinces)} trouvées.")
    if doublons:
        erreurs.append("Provinces rattachées à plusieurs régions : " + ", ".join(doublons))

    nouvelles = contenu["changements_structurants"]["nouvelles_provinces"]
    if {p["province"] for p in nouvelles} != {"Dyamongou", "Karo-Peli"}:
        erreurs.append("La liste des deux nouvelles provinces n'est pas conforme.")

    print(f"Régions : {len(regions)}")
    print(f"Provinces : {len(provinces)}")
    print(f"Provinces uniques : {len(set(provinces))}")

    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR : {erreur}", file=sys.stderr)
        return 1

    print("Référentiel territorial 2025 cohérent. Validation des graphies toujours requise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
