from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from outils_excel import (
    ecrire_json,
    hachage_ligne,
    libelle_sans_instruction_parasite,
    trouver_classeur,
    type_valeur,
)


MOTS_TOTAL = {"total", "totaux", "ensemble", "sous-total", "sous total"}


def choisir_entete(premieres_lignes: list[tuple[Any, ...]]) -> tuple[int | None, float]:
    meilleur_numero = None
    meilleur_score = -1.0
    for numero, ligne in enumerate(premieres_lignes, start=1):
        valeurs = [v for v in ligne if v not in (None, "")]
        if len(valeurs) < 2:
            continue
        textes = sum(isinstance(v, str) and not v.startswith("=") for v in valeurs)
        unicite = len({str(v).strip().casefold() for v in valeurs}) / len(valeurs)
        score = len(valeurs) + 0.5 * textes + unicite
        if score > meilleur_score:
            meilleur_score = score
            meilleur_numero = numero
    confiance = 0.0 if meilleur_numero is None else min(1.0, meilleur_score / 12.0)
    return meilleur_numero, round(confiance, 2)


def nom_colonne(valeur: Any, numero: int) -> str:
    if valeur in (None, ""):
        return f"colonne_sans_nom_{numero}"
    return libelle_sans_instruction_parasite(valeur)


def analyser_feuille(feuille, numero_feuille: int, seuil_manquants: float, inclure_noms: bool) -> dict:
    identifiant_feuille = f"F{numero_feuille:02d}"
    premieres_lignes = []
    for numero, ligne in enumerate(feuille.iter_rows(values_only=True), start=1):
        premieres_lignes.append(tuple(ligne))
        if numero >= 25:
            break

    entete, confiance = choisir_entete(premieres_lignes)
    if entete is None:
        return {
            "identifiant": identifiant_feuille,
            **({"nom": feuille.title} if inclure_noms else {}),
            "statut": "a_examiner",
            "problemes": ["Aucune ligne d'en-tête probable détectée."],
        }

    ligne_entete = premieres_lignes[entete - 1]
    derniere_colonne = max(
        (i for i, v in enumerate(ligne_entete, start=1) if v not in (None, "")),
        default=0,
    )
    entetes = [nom_colonne(v, i) for i, v in enumerate(ligne_entete[:derniere_colonne], start=1)]
    entetes_norm = [e.casefold() for e in entetes]
    doublons_entetes_reels = sorted(
        {entetes[i] for i, e in enumerate(entetes_norm) if entetes_norm.count(e) > 1}
    )
    numeros_entetes_dupliquees = sorted(
        i + 1 for i, e in enumerate(entetes_norm) if entetes_norm.count(e) > 1
    )

    compteurs = [Counter() for _ in entetes]
    manquants = [0 for _ in entetes]
    presents = [0 for _ in entetes]
    lignes_donnees = 0
    lignes_vides = 0
    lignes_total_probables = 0
    doublons_lignes = 0
    empreintes_vues: set[str] = set()

    for numero, ligne in enumerate(feuille.iter_rows(values_only=True), start=1):
        if numero <= entete:
            continue
        valeurs = list(ligne[: len(entetes)])
        valeurs += [None] * (len(entetes) - len(valeurs))
        if all(v in (None, "") for v in valeurs):
            lignes_vides += 1
            continue

        lignes_donnees += 1
        empreinte = hachage_ligne(valeurs)
        if empreinte in empreintes_vues:
            doublons_lignes += 1
        else:
            empreintes_vues.add(empreinte)

        premiers_textes = {
            str(v).strip().casefold()
            for v in valeurs[: min(3, len(valeurs))]
            if isinstance(v, str)
        }
        if premiers_textes & MOTS_TOTAL:
            lignes_total_probables += 1

        for i, valeur in enumerate(valeurs):
            categorie = type_valeur(valeur)
            compteurs[i][categorie] += 1
            if categorie == "vide":
                manquants[i] += 1
            else:
                presents[i] += 1

    colonnes = []
    problemes = []
    if confiance < 0.5:
        problemes.append("Ligne d'en-tête probable à confirmer manuellement.")
    if doublons_entetes_reels:
        problemes.append("Noms de colonnes dupliqués.")
    if doublons_lignes:
        problemes.append("Lignes strictement dupliquées détectées ; ne pas supprimer sans examen.")
    if lignes_total_probables:
        problemes.append("Lignes de total probables détectées ; confirmer leur rôle avant analyse.")

    for i, entete_colonne in enumerate(entetes):
        identifiant_colonne = f"C{i + 1:02d}"
        total = manquants[i] + presents[i]
        taux = (manquants[i] / total) if total else 0.0
        if total and taux >= seuil_manquants:
            problemes.append(
                f"Valeurs manquantes élevées dans la colonne {identifiant_colonne} ({taux:.1%})."
            )
        colonnes.append(
            {
                "numero": i + 1,
                "identifiant": identifiant_colonne,
                **({"nom": entete_colonne} if inclure_noms else {}),
                "valeurs_presentes": presents[i],
                "valeurs_manquantes": manquants[i],
                "taux_manquant": round(taux, 4),
                "types": dict(sorted(compteurs[i].items())),
            }
        )

    return {
        "identifiant": identifiant_feuille,
        **({"nom": feuille.title} if inclure_noms else {}),
        "statut": "a_examiner" if problemes else "aucune_alerte_technique",
        "ligne_entete_probable": entete,
        "confiance_entete": confiance,
        "nombre_colonnes_analysees": len(entetes),
        "lignes_de_donnees_non_vides": lignes_donnees,
        "lignes_vides_apres_entete": lignes_vides,
        "lignes_strictement_dupliquees": doublons_lignes,
        "lignes_total_probables": lignes_total_probables,
        "colonnes_avec_entete_dupliquee": numeros_entetes_dupliquees,
        **({"entetes_dupliquees": doublons_entetes_reels} if inclure_noms else {}),
        "colonnes": colonnes,
        "problemes": problemes,
    }


def analyser(classeur: Path, seuil_manquants: float, inclure_noms: bool = False) -> dict:
    livre = load_workbook(
        classeur,
        read_only=True,
        data_only=False,
        keep_links=False,
    )
    try:
        feuilles = [
            analyser_feuille(f, i, seuil_manquants, inclure_noms)
            for i, f in enumerate(livre.worksheets, start=1)
        ]
    finally:
        livre.close()

    return {
        "rapport": "controles_qualite",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "confidentialite": (
            "Rapport agrégé sans valeur de cellule ni ligne exemple. Les noms sont masqués "
            "par défaut. Ne pas transmettre un rapport créé avec --inclure-noms."
        ),
        "fichier": "classeur_source",
        "seuil_alerte_valeurs_manquantes": seuil_manquants,
        "regle": "Aucune correction ou suppression automatique n'est effectuée.",
        "feuilles": feuilles,
    }


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Contrôles de qualité locaux sans exporter les valeurs du classeur."
    )
    parseur.add_argument("--classeur", help="Chemin du fichier .xlsx ou .xlsm")
    parseur.add_argument(
        "--sortie",
        default="rapports_prives/02_controles_qualite.json",
        help="Chemin du rapport JSON",
    )
    parseur.add_argument(
        "--seuil-manquants",
        type=float,
        default=0.20,
        help="Taux à partir duquel une colonne est signalée (défaut : 0.20)",
    )
    parseur.add_argument(
        "--inclure-noms",
        action="store_true",
        help="Inclut les noms de feuilles et colonnes. Rapport strictement local.",
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    if not 0 <= args.seuil_manquants <= 1:
        print("ERREUR : --seuil-manquants doit être compris entre 0 et 1.", file=sys.stderr)
        return 2

    racine = Path(__file__).resolve().parents[1]
    try:
        classeur = trouver_classeur(racine, args.classeur)
        sortie = Path(args.sortie)
        if not sortie.is_absolute():
            sortie = racine / sortie
        rapport = analyser(
            classeur,
            args.seuil_manquants,
            inclure_noms=args.inclure_noms,
        )
        ecrire_json(sortie, rapport)
    except Exception as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1

    print(f"Contrôles terminés : {sortie.name}")
    print("Aucune donnée n'a été corrigée, supprimée ou envoyée en ligne.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

