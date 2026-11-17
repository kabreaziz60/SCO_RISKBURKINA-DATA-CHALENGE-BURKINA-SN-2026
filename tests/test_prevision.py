from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

from evaluer_prevision import annee_future, creer_paires  # noqa: E402


class PrevisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.indicateurs = pd.read_csv(
            RACINE
            / "03_transformation"
            / "SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
        )
        cls.projections = pd.read_csv(
            RACINE
            / "04_analyse"
            / "SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv"
        )

    def test_deux_horizons_directs(self) -> None:
        self.assertEqual(annee_future("2024-2025", 1), "2025-2026")
        self.assertEqual(annee_future("2024-2025", 2), "2026-2027")
        paires_h1 = creer_paires(self.indicateurs, horizon=1)
        paires_h2 = creer_paires(self.indicateurs, horizon=2)
        self.assertEqual(set(paires_h1["horizon_ans"]), {1})
        self.assertEqual(set(paires_h2["horizon_ans"]), {2})

    def test_projection_complete_et_sans_doublon(self) -> None:
        self.assertEqual(
            set(self.projections["annee_cible"]), {"2025-2026", "2026-2027"}
        )
        effectifs = self.projections.groupby("annee_cible")["province"].nunique()
        self.assertTrue((effectifs == 45).all())
        self.assertFalse(
            self.projections.duplicated(["annee_cible", "province"]).any()
        )
        self.assertTrue(self.projections["score_prevu"].between(0, 100).all())


if __name__ == "__main__":
    unittest.main()
