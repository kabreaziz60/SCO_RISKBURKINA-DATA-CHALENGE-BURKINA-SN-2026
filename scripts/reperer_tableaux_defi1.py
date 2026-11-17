from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


MOTS_CLES = {
    "abandon": ("abandon",),
    "redoublement": ("redoubl",),
    "achevement": ("achevement",),
    "promotion": ("promotion",),
    "transition": ("transition",),
}


def normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte.casefold() if not unicodedata.combining(c))


def reperer_fichier(chemin: Path) -> dict | None:
    pages: dict[str, set[str]] = defaultdict(set)
    comptes: dict[str, int] = defaultdict(int)
    with chemin.open("r", encoding="utf-8-sig", errors="replace", newline="") as flux:
        lecteur = csv.DictReader(flux, delimiter=";")
        for ligne in lecteur:
            texte = normaliser(" ".join(str(v or "") for v in ligne.values()))
            page = str(ligne.get("page") or "page_non_renseignee").strip()
            for indicateur, motifs in MOTS_CLES.items():
                if any(motif in texte for motif in motifs):
                    pages[indicateur].add(page)
                    comptes[indicateur] += 1
    if not comptes:
        return None
    return {
        "fichier": chemin.name,
        "repertoire": chemin.parent.name,
        "indicateurs": {
            indicateur: {
                "pages": sorted(pages[indicateur], key=lambda x: (not x.isdigit(), x)),
                "lignes_reperees": comptes[indicateur],
            }
            for indicateur in sorted(comptes)
        },
    }


def analyser(racine_selection: Path) -> dict:
    base = racine_selection / "data" / "01_Education_MENAPLN_DGESS"
    fichiers = []
    for chemin in sorted(base.rglob("CNS*.csv")):
        resultat = reperer_fichier(chemin)
        if resultat:
            fichiers.append(resultat)
    return {
        "rapport": "reperage_tableaux_defi_1",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "confidentialite": "Métadonnées locales : aucun contenu de ligne n'est restitué.",
        "nombre_fichiers_avec_correspondance": len(fichiers),
        "fichiers": fichiers,
    }


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Repère les pages utiles au défi 1 sans exporter les lignes de données."
    )
    parseur.add_argument(
        "--selection",
        default="01_collecte/data_pack_selection",
        help="Dossier créé par preparer_data_pack.py.",
    )
    parseur.add_argument(
        "--sortie",
        default="rapports_prives/04_reperage_tableaux_defi1.json",
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]
    selection = Path(args.selection)
    sortie = Path(args.sortie)
    if not selection.is_absolute():
        selection = racine / selection
    if not sortie.is_absolute():
        sortie = racine / sortie
    rapport = analyser(selection)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Repérage terminé : "
        f"{rapport['nombre_fichiers_avec_correspondance']} fichiers contiennent des tableaux utiles."
    )
    print("Aucune ligne de données n'a été affichée ni exportée dans le rapport.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
