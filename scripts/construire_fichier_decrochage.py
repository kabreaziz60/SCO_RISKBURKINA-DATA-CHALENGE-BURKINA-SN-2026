from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from outils_excel import empreinte_sha256, libelle_sans_instruction_parasite, trouver_classeur


NIVEAUX_ABANDON = ("cp1", "cp2", "ce1", "ce2", "cm1")
NIVEAUX_REDOUBLEMENT = ("cp1", "cp2", "ce1", "ce2", "cm1", "cm2")


def normaliser(valeur: Any) -> str:
    texte = unicodedata.normalize("NFKD", str(valeur or ""))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return " ".join(
        texte.casefold().replace("-", " ").replace("’", " ").replace("'", " ").split()
    )


def annee_scolaire_depuis_nom(nom: str) -> str:
    correspondance = re.search(r"(20\d{2})_(20\d{2})", nom)
    if not correspondance:
        raise ValueError(f"Année scolaire absente du nom : {nom}")
    return f"{correspondance.group(1)}-{correspondance.group(2)}"


def annee_scolaire(valeur: Any) -> str | None:
    trouve = re.search(r"(20\d{2})\D*(\d{2,4})", str(valeur or ""))
    if not trouve:
        return None
    debut = int(trouve.group(1))
    fin_texte = trouve.group(2)
    fin = int(fin_texte) if len(fin_texte) == 4 else (debut // 100) * 100 + int(fin_texte)
    return f"{debut:04d}-{fin:04d}"


def nombre(valeur: Any) -> float | None:
    texte = str(valeur or "").strip()
    if not texte or texte in {"-", "…", "...", "nd", "n.d."}:
        return None
    texte = texte.replace("\u202f", "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        return float(texte)
    except ValueError:
        return None


def cellules_ligne(ligne: dict[str, str]) -> list[str]:
    def numero_colonne(cle: str) -> int:
        match = re.fullmatch(r"c(\d+)", cle)
        return int(match.group(1)) if match else 10_000

    return [
        str(ligne[cle]).strip()
        for cle in sorted(ligne, key=numero_colonne)
        if re.fullmatch(r"c\d+", cle) and ligne.get(cle) not in (None, "")
    ]


def charger_referentiel(chemin: Path) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    provinces = {normaliser(p["province"]): p for p in contenu["provinces"]}
    aliases = {normaliser(k): v for k, v in contenu.get("aliases", {}).items()}
    for cle, province in aliases.items():
        provinces[cle] = next(p for p in contenu["provinces"] if p["province"] == province)
    return provinces, aliases


def valeurs_totales(cellules: list[str], libelle: str) -> list[float | None]:
    position = next((i for i, valeur in enumerate(cellules) if normaliser(valeur) == libelle), None)
    if position is None:
        return []
    valeurs = [nombre(v) for v in cellules[position + 1 :]]
    return valeurs[2::3]


def moyenne_disponible(valeurs: list[float | None]) -> float | None:
    valides = [v for v in valeurs if v is not None and 0 <= v <= 100]
    return round(statistics.fmean(valides), 4) if valides else None


def compter_hors_plage(valeurs: list[float | None]) -> int:
    return sum(v is not None and not 0 <= v <= 100 for v in valeurs)


def extraire_annuaire(
    chemin: Path, provinces: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    with chemin.open("r", encoding="utf-8-sig", errors="replace", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=";"))
    annee = annee_scolaire_depuis_nom(chemin.name)
    resultat = []
    for index, ligne in enumerate(lignes):
        cellules = cellules_ligne(ligne)
        cle_province = next((normaliser(v) for v in cellules if normaliser(v) in provinces), None)
        if not cle_province or not any(normaliser(v) == "tx red" for v in cellules):
            continue
        precedente = cellules_ligne(lignes[index - 1]) if index > 0 else []
        suivante = cellules_ligne(lignes[index + 1]) if index + 1 < len(lignes) else []
        if not any(normaliser(v) == "tx prom" for v in precedente):
            continue
        if not any(normaliser(v) == "tx aban" for v in suivante):
            continue
        reference = provinces[cle_province]
        abandon = valeurs_totales(suivante, "tx aban")[: len(NIVEAUX_ABANDON)]
        redoublement = valeurs_totales(cellules, "tx red")[: len(NIVEAUX_REDOUBLEMENT)]
        promotion = valeurs_totales(precedente, "tx prom")[: len(NIVEAUX_ABANDON)]
        nb_hors_plage = sum(
            compter_hors_plage(valeurs)
            for valeurs in (abandon, redoublement, promotion)
        )
        ligne_sortie: dict[str, Any] = {
            "province": reference["province"],
            "region_historique": reference["region_historique"],
            "region_2025": reference["region_2025"],
            "annee_scolaire": annee,
            "taux_abandon_moyen_non_pondere": moyenne_disponible(abandon),
            "taux_redoublement_moyen_non_pondere": moyenne_disponible(redoublement),
            "taux_promotion_moyen_non_pondere": moyenne_disponible(promotion),
            "source_indicateurs_province": chemin.name,
            "page_source": ligne.get("page", ""),
            "methode_province": "moyenne_non_ponderee_des_taux_totaux_par_niveau",
            "nb_taux_source_hors_plage": nb_hors_plage,
            "statut_qualite": "a_verifier_source" if nb_hors_plage else "ok",
        }
        ligne_sortie.update(
            {f"taux_abandon_{niveau}": abandon[i] if i < len(abandon) else None for i, niveau in enumerate(NIVEAUX_ABANDON)}
        )
        ligne_sortie.update(
            {f"taux_redoublement_{niveau}": redoublement[i] if i < len(redoublement) else None for i, niveau in enumerate(NIVEAUX_REDOUBLEMENT)}
        )
        ligne_sortie.update(
            {f"taux_promotion_{niveau}": promotion[i] if i < len(promotion) else None for i, niveau in enumerate(NIVEAUX_ABANDON)}
        )
        resultat.append(ligne_sortie)
    return resultat


def extraire_achevement_regional(classeur: Path) -> dict[tuple[str, str], float]:
    livre = load_workbook(classeur, read_only=True, data_only=True, keep_links=False)
    try:
        feuille = None
        for candidate in livre.worksheets:
            titre = normaliser(candidate.cell(1, 1).value)
            if "taux d achevement" in titre and "primaire" in titre:
                feuille = candidate
                break
        if feuille is None:
            raise RuntimeError("La feuille du taux d'achèvement primaire est introuvable.")

        annees_par_colonne: dict[int, str] = {}
        annee_active = None
        for colonne in range(2, feuille.max_column + 1):
            nouvelle_annee = annee_scolaire(feuille.cell(2, colonne).value)
            if nouvelle_annee:
                annee_active = nouvelle_annee
            sexe = normaliser(feuille.cell(3, colonne).value)
            if annee_active and sexe in {"t", "total", "ensemble"}:
                annees_par_colonne[colonne] = annee_active

        valeurs: dict[tuple[str, str], float] = {}
        for ligne in range(4, feuille.max_row + 1):
            region = libelle_sans_instruction_parasite(feuille.cell(ligne, 1).value)
            if not region or region == "libelle_retire":
                continue
            region_norm = normaliser(region)
            if region_norm in {"burkina faso", "total", "ensemble"}:
                continue
            for colonne, annee in annees_par_colonne.items():
                valeur = nombre(feuille.cell(ligne, colonne).value)
                if valeur is not None:
                    valeurs[(region_norm, annee)] = valeur
        return valeurs
    finally:
        livre.close()


def construire(
    classeur: Path,
    dossier_annuaires: Path,
    referentiel: Path,
    sortie_csv: Path,
    sortie_qualite: Path,
) -> dict[str, Any]:
    provinces, _ = charger_referentiel(referentiel)
    lignes: list[dict[str, Any]] = []
    for chemin in sorted(dossier_annuaires.glob("CNS*.csv")):
        if re.search(r"CNS(?:52[1-6]|529|530)_", chemin.name):
            lignes.extend(extraire_annuaire(chemin, provinces))
    if not lignes:
        raise RuntimeError("Aucune ligne provinciale n'a été extraite des annuaires.")

    achevement = extraire_achevement_regional(classeur)
    for ligne in lignes:
        cle = (normaliser(ligne["region_historique"]), ligne["annee_scolaire"])
        taux = achevement.get(cle)
        ligne["taux_achevement_region"] = taux
        ligne["taux_non_achevement_region"] = None if taux is None else round(100 - taux, 4)
        ligne["niveau_geographique_achevement"] = "ancienne_region"
        ligne["source_achevement"] = classeur.name

    lignes.sort(key=lambda x: (x["annee_scolaire"], x["province"]))
    champs = list(lignes[0])
    sortie_csv.parent.mkdir(parents=True, exist_ok=True)
    with sortie_csv.open("w", encoding="utf-8-sig", newline="") as flux:
        ecrivain = csv.DictWriter(flux, fieldnames=champs, extrasaction="ignore")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)

    par_annee = Counter(ligne["annee_scolaire"] for ligne in lignes)
    doublons = len(lignes) - len({(l["province"], l["annee_scolaire"]) for l in lignes})
    manquants = {
        champ: sum(ligne.get(champ) in (None, "") for ligne in lignes)
        for champ in (
            "taux_abandon_moyen_non_pondere",
            "taux_redoublement_moyen_non_pondere",
            "taux_achevement_region",
        )
    }
    lignes_a_verifier = sum(ligne["statut_qualite"] != "ok" for ligne in lignes)
    valeurs_hors_plage = sum(ligne["nb_taux_source_hors_plage"] for ligne in lignes)
    rapport = {
        "rapport": "construction_fichier_decrochage",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "confidentialite": "Rapport agrégé : aucune valeur éducative n'est restituée.",
        "sortie": sortie_csv.name,
        "nombre_lignes": len(lignes),
        "nombre_provinces": len({l["province"] for l in lignes}),
        "annees": dict(sorted(par_annee.items())),
        "doublons_cle_province_annee": doublons,
        "valeurs_manquantes": manquants,
        "lignes_a_verifier_source": lignes_a_verifier,
        "valeurs_source_hors_plage": valeurs_hors_plage,
        "empreinte_classeur_source": empreinte_sha256(classeur),
        "empreinte_sortie": empreinte_sha256(sortie_csv),
        "limite": (
            "Les taux provinciaux moyens sont des moyennes non pondérées des taux totaux "
            "par niveau. Les valeurs hors de [0,100] restent visibles dans les colonnes par "
            "niveau, sont exclues des moyennes et sont signalées. L'achèvement est régional."
        ),
    }
    sortie_qualite.parent.mkdir(parents=True, exist_ok=True)
    sortie_qualite.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Construit localement le fichier unique province-année du défi 1."
    )
    parseur.add_argument("--classeur", help="Classeur principal DGESS")
    parseur.add_argument(
        "--annuaires",
        default=(
            "01_collecte/data_pack_selection/data/01_Education_MENAPLN_DGESS/"
            "CNS_DGESS/Annuaires"
        ),
    )
    parseur.add_argument(
        "--referentiel", default="config/referentiel_provinces_historiques.json"
    )
    parseur.add_argument(
        "--sortie", default="02_nettoyage/SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv"
    )
    parseur.add_argument(
        "--qualite", default="rapports_prives/05_qualite_fichier_decrochage.json"
    )
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]
    classeur = trouver_classeur(racine, args.classeur)

    def chemin(argument: str) -> Path:
        valeur = Path(argument)
        return valeur if valeur.is_absolute() else racine / valeur

    rapport = construire(
        classeur=classeur,
        dossier_annuaires=chemin(args.annuaires),
        referentiel=chemin(args.referentiel),
        sortie_csv=chemin(args.sortie),
        sortie_qualite=chemin(args.qualite),
    )
    print(
        f"Fichier construit : {rapport['nombre_lignes']} lignes, "
        f"{rapport['nombre_provinces']} provinces."
    )
    print("Aucune valeur de donnée n'a été affichée ni envoyée en ligne.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
