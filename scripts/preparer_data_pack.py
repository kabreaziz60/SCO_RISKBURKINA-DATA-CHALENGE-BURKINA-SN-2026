from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


MOTIFS_SELECTION = (
    "DataPack_DCB_2026/LISEZ-MOI.txt",
    "DataPack_DCB_2026/Guide_du_Data_Pack_Data_Challenge_Burkina_2026.pdf",
    "DataPack_DCB_2026/00_Documentation_et_Referentiels/Catalogue_sources_x_defis.xlsx",
    "DataPack_DCB_2026/00_Documentation_et_Referentiels/manifeste_telechargements.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Annuaires/CNS52[1-6]_*.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Annuaires/CNS529_*.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Annuaires/CNS530_*.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Tableaux_de_bord/CNS56[4-9]_*.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Tableaux_de_bord/CNS57[0-4]_*.csv",
    "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/ESU_Rapports_mensuels/*.csv",
    "DataPack_DCB_2026/data/03_Conditions_de_Vie_et_Emploi/INSD_EHCVM_2021_Rapport_General.csv",
    "DataPack_DCB_2026/data/03_Conditions_de_Vie_et_Emploi/PDI_CONASUR/*.csv",
    "DataPack_DCB_2026/04_Cartographie_SIG/COD-AB_limites_administratives/bfa_admin_boundaries.geojson.zip",
    "DataPack_DCB_2026/04_Cartographie_SIG/COD-AB_limites_administratives/bfa_admin_boundaries.xlsx",
    "DataPack_DCB_2026/data/04_Cartographie_SIG/COD-AB_limites_administratives/bfa_admin_boundaries__bfa_admin[1-3].csv",
)


def est_selectionne(nom: str) -> bool:
    return any(fnmatch.fnmatchcase(nom, motif) for motif in MOTIFS_SELECTION)


def sha256(chemin: Path) -> str:
    hachage = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            hachage.update(bloc)
    return hachage.hexdigest()


def trouver_zip(racine: Path, argument: str | None) -> Path:
    if argument:
        chemin = Path(argument).expanduser().resolve()
        if not chemin.is_file():
            raise FileNotFoundError(f"Data Pack introuvable : {chemin}")
        return chemin
    candidats = sorted((racine / "01_collecte").glob("*DataPack*.zip"))
    if len(candidats) != 1:
        raise RuntimeError(
            "Placez un seul DataPack*.zip dans 01_collecte ou utilisez --zip CHEMIN."
        )
    return candidats[0]


def extraire_selection(zip_path: Path, sortie: Path, remplacer: bool = False) -> dict:
    fichiers = []
    with zipfile.ZipFile(zip_path) as archive:
        membres = [m for m in archive.infolist() if not m.is_dir() and est_selectionne(m.filename)]
        if not membres:
            raise RuntimeError("Aucun fichier attendu n'a été trouvé dans le Data Pack.")
        for membre in membres:
            relatif = Path(membre.filename).relative_to("DataPack_DCB_2026")
            destination = sortie / relatif
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and not remplacer:
                statut = "deja_present"
            else:
                with archive.open(membre) as source, destination.open("wb") as cible:
                    while bloc := source.read(1024 * 1024):
                        cible.write(bloc)
                statut = "extrait"
            fichiers.append(
                {
                    "chemin": relatif.as_posix(),
                    "taille_octets": destination.stat().st_size,
                    "sha256": sha256(destination),
                    "statut": statut,
                }
            )
    return {
        "rapport": "selection_data_pack_defi_1",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "source_zip": zip_path.name,
        "source_sha256": sha256(zip_path),
        "nombre_fichiers": len(fichiers),
        "regle": "Sélection minimale pour le défi 1 ; aucune valeur n'est affichée.",
        "fichiers": fichiers,
    }


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Extrait localement les sources publiques utiles au défi 1."
    )
    parseur.add_argument("--zip", help="Chemin du DataPack_DCB_2026.zip")
    parseur.add_argument(
        "--sortie",
        default="01_collecte/data_pack_selection",
        help="Dossier de destination relatif à la racine du projet.",
    )
    parseur.add_argument("--remplacer", action="store_true")
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]
    zip_path = trouver_zip(racine, args.zip)
    sortie = Path(args.sortie)
    if not sortie.is_absolute():
        sortie = racine / sortie
    rapport = extraire_selection(zip_path, sortie, remplacer=args.remplacer)
    rapport_path = sortie / "inventaire_selection.json"
    rapport_path.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sélection terminée : {rapport['nombre_fichiers']} fichiers publics.")
    print(f"Inventaire : {rapport_path}")
    print("Aucune valeur de donnée n'a été affichée ni envoyée en ligne.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
