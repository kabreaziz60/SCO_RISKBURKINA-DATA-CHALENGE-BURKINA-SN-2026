from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    racine = Path(__file__).resolve().parents[1]
    chemin = racine / "config" / "correspondance_regions_2025.json"
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    lignes = contenu.get("correspondances", [])

    anciennes = [ligne["ancienne_region"] for ligne in lignes]
    nouvelles = [nom for ligne in lignes for nom in ligne["nouvelles_regions"]]
    doublons_anciennes = sorted(n for n, c in Counter(anciennes).items() if c > 1)
    doublons_nouvelles = sorted(n for n, c in Counter(nouvelles).items() if c > 1)
    types_invalides = sorted(
        {ligne.get("type") for ligne in lignes if ligne.get("type") not in {"renommage", "scission"}}
    )

    problemes = []
    if len(anciennes) != 13:
        problemes.append(f"13 anciennes régions attendues, {len(anciennes)} trouvées.")
    if len(set(nouvelles)) != 17:
        problemes.append(f"17 nouvelles régions attendues, {len(set(nouvelles))} trouvées.")
    if doublons_anciennes:
        problemes.append("Anciennes régions dupliquées dans le référentiel.")
    if doublons_nouvelles:
        problemes.append("Nouvelles régions rattachées plusieurs fois.")
    if types_invalides:
        problemes.append("Types de correspondance invalides.")

    print(f"Anciennes régions : {len(set(anciennes))}")
    print(f"Nouvelles régions : {len(set(nouvelles))}")
    print(f"Scissions : {sum(ligne['type'] == 'scission' for ligne in lignes)}")

    if problemes:
        for probleme in problemes:
            print(f"ERREUR : {probleme}", file=sys.stderr)
        return 1

    print("Référentiel géographique cohérent. Validation cartographique humaine toujours requise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
