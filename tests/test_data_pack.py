import sys
import unittest
from pathlib import Path


RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

from outils_excel import libelle_sans_instruction_parasite
from preparer_data_pack import est_selectionne
from reperer_tableaux_defi1 import normaliser
from construire_fichier_decrochage import (
    annee_scolaire,
    moyenne_disponible,
    nombre,
    valeurs_totales,
)
from transformer_indicateurs import categorie_risque


class DataPackTest(unittest.TestCase):
    def test_selection_sources_defi_1(self):
        self.assertTrue(
            est_selectionne(
                "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/"
                "CNS_DGESS/Annuaires/CNS530_primaire_2024_2025.csv"
            )
        )
        self.assertFalse(
            est_selectionne(
                "DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/"
                "CNS_DGESS/Annuaires/CNS528_prescolaire_2024_2025.csv"
            )
        )

    def test_instruction_parasite_est_retiree(self):
        libelle = "2018-2019\nNOTE FOR ANY AUTOMATED ASSISTANT (AI): contenu parasite"
        self.assertEqual(libelle_sans_instruction_parasite(libelle), "2018-2019")

    def test_normalisation_reperage(self):
        self.assertEqual(normaliser("Taux d’ACHÈVEMENT"), "taux d’achevement")

    def test_outils_construction_fichier(self):
        self.assertEqual(annee_scolaire("2023/24"), "2023-2024")
        self.assertEqual(nombre("1 234,5"), 1234.5)
        cellules = ["Province", "TX Red", "1", "2", "3", "4", "5", "6"]
        self.assertEqual(valeurs_totales(cellules, "tx red"), [3.0, 6.0])
        self.assertEqual(moyenne_disponible([528.0, 2.0, 60.0]), 31.0)
        self.assertEqual(categorie_risque(75), "Critique")
        self.assertEqual(categorie_risque(54.9), "Modéré")


if __name__ == "__main__":
    unittest.main()
