from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from outils_excel import empreinte_sha256


NIVEAUX = ("cp1", "cp2", "ce1", "ce2", "cm1")


def valider(entree: Path, sortie: Path, tolerance: float = 0.25) -> dict:
    donnees = pd.read_csv(entree)
    controles = []
    valeurs_hors_plage = 0
    triplets_incomplets = 0

    for niveau in NIVEAUX:
        colonnes = [
            f"taux_promotion_{niveau}",
            f"taux_redoublement_{niveau}",
            f"taux_abandon_{niveau}",
        ]
        absentes = [colonne for colonne in colonnes if colonne not in donnees]
        if absentes:
            raise ValueError("Colonnes absentes : " + ", ".join(absentes))
        valeurs = donnees[colonnes].apply(pd.to_numeric, errors="coerce")
        triplets_incomplets += int(valeurs.isna().any(axis=1).sum())
        hors_plage = ((valeurs < 0) | (valeurs > 100)).any(axis=1)
        valeurs_hors_plage += int(hors_plage.sum())
        sommes = valeurs.sum(axis=1, min_count=3)
        ecarts = (sommes - 100).abs()
        incoherents = (~hors_plage) & ecarts.gt(tolerance)
        controles.append(
            {
                "niveau": niveau.upper(),
                "triplets_testes": int(sommes.notna().sum()),
                "triplets_hors_plage": int(hors_plage.sum()),
                "sommes_incoherentes_hors_anomalies": int(incoherents.sum()),
                "ecart_max_hors_anomalies": round(
                    float(ecarts[~hors_plage].max()), 4
                ),
            }
        )

    couverture = (
        donnees.groupby("annee_scolaire")["province"].nunique().sort_index().to_dict()
    )
    doublons = int(
        donnees.duplicated(subset=["province", "annee_scolaire"]).sum()
    )
    sommes_incoherentes = sum(
        controle["sommes_incoherentes_hors_anomalies"] for controle in controles
    )
    rapport = {
        "rapport": "validation_coherence_indicateurs_primaires",
        "cree_le_utc": datetime.now(timezone.utc).isoformat(),
        "confidentialite": "Rapport agrégé ; aucune valeur provinciale n'est restituée.",
        "regle": (
            "Pour CP1 à CM1, promotion + redoublement + abandon doit être égal "
            f"à 100 %, avec une tolérance de {tolerance} point due aux arrondis."
        ),
        "nombre_lignes": int(len(donnees)),
        "nombre_provinces": int(donnees["province"].nunique()),
        "couverture_par_annee": {str(k): int(v) for k, v in couverture.items()},
        "doublons_province_annee": doublons,
        "triplets_attendus": int(len(donnees) * len(NIVEAUX)),
        "triplets_incomplets": triplets_incomplets,
        "triplets_avec_valeur_hors_plage": valeurs_hors_plage,
        "sommes_incoherentes_hors_anomalies": sommes_incoherentes,
        "controle_par_niveau": controles,
        "lignes_deja_signalees_source": int(
            (donnees["statut_qualite"] != "ok").sum()
        ),
        "empreinte_entree": empreinte_sha256(entree),
        "statut_global": (
            "coherent_avec_anomalie_source_signalee"
            if sommes_incoherentes == 0 and doublons == 0 and triplets_incomplets == 0
            else "a_revoir"
        ),
        "limite": (
            "Ce contrôle vérifie la cohérence arithmétique des taux publiés. Il ne "
            "prouve pas encore que les effectifs disponibles constituent les bons poids."
        ),
    }
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rapport


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(
        description="Contrôle la cohérence arithmétique des indicateurs primaires."
    )
    parseur.add_argument(
        "--entree", default="02_nettoyage/SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv"
    )
    parseur.add_argument(
        "--sortie", default="rapports_prives/08_validation_coherence_indicateurs.json"
    )
    parseur.add_argument("--tolerance", type=float, default=0.25)
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]

    def chemin(valeur: str) -> Path:
        p = Path(valeur)
        return p if p.is_absolute() else racine / p

    rapport = valider(chemin(args.entree), chemin(args.sortie), args.tolerance)
    print(
        "Validation terminée : "
        f"{rapport['triplets_attendus']} triplets attendus, "
        f"statut = {rapport['statut_global']}."
    )
    print("Aucune valeur provinciale n'a été affichée ni envoyée en ligne.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
