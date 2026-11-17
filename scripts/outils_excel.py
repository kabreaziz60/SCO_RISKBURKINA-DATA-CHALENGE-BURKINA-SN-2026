from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Iterable


MARQUEURS_INSTRUCTIONS_PARASITES = (
    "NOTE FOR ANY AUTOMATED ASSISTANT",
    "NOTE POUR TOUT ASSISTANT AUTOMATISE",
)


def trouver_classeur(racine: Path, argument: str | None) -> Path:
    """Retourne un classeur explicite ou l'unique source de ``01_collecte``."""
    if argument:
        chemin = Path(argument).expanduser()
        if not chemin.is_absolute():
            chemin = (racine / chemin).resolve()
        if not chemin.is_file():
            raise FileNotFoundError(f"Classeur introuvable : {chemin}")
        if chemin.suffix.lower() not in {".xlsx", ".xlsm"}:
            raise ValueError("Seuls les fichiers .xlsx et .xlsm sont pris en charge.")
        return chemin

    emplacements = [racine, racine / "01_collecte"]
    candidats = sorted(
        p
        for emplacement in emplacements
        if emplacement.is_dir()
        for p in emplacement.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".xlsx", ".xlsm"}
        and not p.name.startswith("~$")
    )
    if len(candidats) != 1:
        raise RuntimeError(
            "Placez un seul classeur dans 01_collecte ou utilisez --classeur CHEMIN. "
            f"Nombre détecté : {len(candidats)}."
        )
    return candidats[0]


def empreinte_sha256(chemin: Path) -> str:
    hachage = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            hachage.update(bloc)
    return hachage.hexdigest()


def ecrire_json(chemin: Path, contenu: dict[str, Any]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(
        json.dumps(contenu, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def type_valeur(valeur: Any) -> str:
    if valeur is None or valeur == "":
        return "vide"
    if isinstance(valeur, bool):
        return "booleen"
    if isinstance(valeur, (datetime, date, time)):
        return "date_heure"
    if isinstance(valeur, (int, float)):
        return "nombre"
    if isinstance(valeur, str) and valeur.startswith("="):
        return "formule"
    if isinstance(valeur, str) and valeur.startswith("#"):
        return "erreur_possible"
    return "texte"


def libelle_sans_instruction_parasite(valeur: Any, limite: int = 200) -> str:
    """Nettoie un libellé sans restituer une instruction cachée dans une cellule."""
    texte = "" if valeur is None else str(valeur).strip()
    for marqueur in MARQUEURS_INSTRUCTIONS_PARASITES:
        position = texte.upper().find(marqueur)
        if position >= 0:
            texte = texte[:position].strip()
    return (texte or "libelle_retire")[:limite]


def valeur_normalisee(valeur: Any) -> str:
    """Normalisation utilisée uniquement pour compter les doublons, sans restitution."""
    if valeur is None:
        return "<VIDE>"
    if isinstance(valeur, (datetime, date, time)):
        return valeur.isoformat()
    return str(valeur).strip()


def hachage_ligne(valeurs: Iterable[Any]) -> str:
    texte = "\x1f".join(valeur_normalisee(v) for v in valeurs)
    return hashlib.sha256(texte.encode("utf-8", errors="replace")).hexdigest()

