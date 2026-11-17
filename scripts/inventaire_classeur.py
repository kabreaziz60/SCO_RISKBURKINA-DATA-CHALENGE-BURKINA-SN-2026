from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook

from outils_excel import ecrire_json, empreinte_sha256, trouver_classeur, type_valeur


def analyser(classeur: Path, inclure_noms: bool = False) -> dict:
    livre = load_workbook(
        classeur,
        read_only=True,
        data_only=False,
        keep_links=False,
    )
    feuilles = []
    try:
        for index, feuille in enumerate(livre.worksheets, start=1):
            types = Counter()
            cellules_non_vides = 0
            lignes_non_vides = 0
            largeur_observee = 0

            for ligne in feuille.iter_rows(values_only=True):
                valeurs = list(ligne)
                non_vides = [v for v in valeurs if v not in (None, "")]
                if non_vides:
                    lignes_non_vides += 1
                    dernier = max(i for i, v in enumerate(valeurs, start=1) if v not in (None, ""))
                    largeur_observee = max(largeur_observee, dernier)
                for valeur in non_vides:
                    cellules_non_vides += 1
                    types[type_valeur(valeur)] += 1

            feuilles.append(
                {
                    "numero": index,
                    "identifiant": f"F{index:02d}",
                    **({"nom": feuille.title} if inclure_noms else {}),
                    "lignes_max_declarees": feuille.max_row,
                    "colonnes_max_declarees": feuille.max_column,
                    "lignes_non_vides": lignes_non_vides,
                    "colonnes_utilisees_observees": largeur_observee,
                    "cellules_non_vides": cellules_non_vides,
                    "types_cellules_non_vides": dict(sorted(types.items())),
                }
            )
    finally:
        livre.close()

    return {
        "rapport": "inventaire_classeur",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "confidentialite": (
            "Rapport local. Aucune valeur de cellule ni ligne exemple n'est exportée. "
            "Ne pas transmettre sans vérification humaine."
        ),
        "fichier": {
            "identifiant": "classeur_source",
            **({"nom": classeur.name} if inclure_noms else {}),
            "taille_octets": classeur.stat().st_size,
            "sha256": empreinte_sha256(classeur),
        },
        "nombre_feuilles": len(feuilles),
        "feuilles": feuilles,
    }


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Inventorie localement un classeur sans exporter ses valeurs."
    )
    parseur.add_argument("--classeur", help="Chemin du fichier .xlsx ou .xlsm")
    parseur.add_argument(
        "--sortie",
        default="rapports_prives/01_inventaire_classeur.json",
        help="Chemin du rapport JSON",
    )
    parseur.add_argument(
        "--inclure-noms",
        action="store_true",
        help="Inclut les noms du fichier et des feuilles. Rapport strictement local.",
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]
    try:
        classeur = trouver_classeur(racine, args.classeur)
        sortie = Path(args.sortie)
        if not sortie.is_absolute():
            sortie = racine / sortie
        rapport = analyser(classeur, inclure_noms=args.inclure_noms)
        ecrire_json(sortie, rapport)
    except Exception as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1

    print(f"Inventaire terminé : {sortie.name}")
    print("Aucune valeur de cellule n'a été affichée ni exportée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

