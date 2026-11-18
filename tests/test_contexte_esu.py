from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd


RACINE = Path(__file__).resolve().parents[1]
NETTOYE = RACINE / "02_nettoyage" / (
    "SCO-RISKBurkina_02-nettoyage_D1_engineer_"
    "esu-regions-fevrier-2026-propre_v1.csv"
)
TRANSFORME = RACINE / "03_transformation" / (
    "SCO-RISKBurkina_03-transformation_D1_data-scientist_"
    "indice-pression-esu-regions_v1.csv"
)
SORTIES = [
    NETTOYE,
    TRANSFORME,
    RACINE / "04_analyse" / (
        "SCO-RISKBurkina_04-analyse_D1_data-analyst_"
        "croisement-risque-pression-esu-2025-2026_v1.csv"
    ),
    RACINE / "05_interpretation" / (
        "SCO-RISKBurkina_05-interpretation_D1_data-analyst_"
        "priorites-contexte-urgence_v1.csv"
    ),
]


class ContexteEsuTest(unittest.TestCase):
    def test_totaux_officiels_et_referentiel(self) -> None:
        donnees = pd.read_csv(NETTOYE)
        self.assertEqual(len(donnees), 17)
        self.assertEqual(donnees["region_2025"].nunique(), 17)
        self.assertEqual(donnees["structures_rouvertes_primaire"].sum(), 1840)
        self.assertEqual(donnees["structures_delocalisees_primaire"].sum(), 492)
        self.assertEqual(donnees["edi_primaire_total"].sum(), 436683)
        self.assertTrue(
            (
                donnees["edi_primaire_garcons"]
                + donnees["edi_primaire_filles"]
                == donnees["edi_primaire_total"]
            ).all()
        )

    def test_indice_borne_et_separe(self) -> None:
        donnees = pd.read_csv(TRANSFORME)
        self.assertTrue(donnees["indice_pression_esu"].between(0, 100).all())
        self.assertNotIn("score_risque", donnees.columns)

    def test_aucune_instruction_parasite_dans_les_sorties(self) -> None:
        for chemin in SORTIES:
            contenu = chemin.read_text(encoding="utf-8-sig")
            self.assertNotIn("NOTE FOR ANY AUTOMATED ASSISTANT", contenu)
            self.assertNotIn("On ne développe pas", contenu)


if __name__ == "__main__":
    unittest.main()
