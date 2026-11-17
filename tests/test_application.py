from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "application"))

from scorisk.core import (  # noqa: E402
    calculer_cadrage_geojson,
    categorie_risque,
    charger_geojson,
    charger_referentiel_provinces_historiques,
    charger_referentiel_territorial,
    construire_contours_regions,
    construire_hierarchie_historique,
    construire_hierarchie_par_champ,
    correspondance_carte_sources,
    generer_donnees_demo,
    preparer_jointure,
    provinces_geojson,
    valider_donnees,
)


class ApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.geojson = charger_geojson(RACINE / "application" / "data" / "provinces_45_2017.geojson")
        cls.provinces = provinces_geojson(cls.geojson)

    def test_referentiel_contient_45_provinces(self) -> None:
        self.assertEqual(len(self.provinces), 45)
        self.assertEqual(len(set(self.provinces)), 45)

    def test_donnees_demo_respectent_le_contrat(self) -> None:
        cadre = generer_donnees_demo(self.provinces)
        self.assertEqual(len(cadre), 45 * 8)
        self.assertEqual(valider_donnees(cadre, self.provinces), [])
        jointure = preparer_jointure(cadre, self.provinces)
        self.assertFalse(jointure["province_geo"].isna().any())

    def test_hierarchie_region_provinces(self) -> None:
        referentiel = charger_referentiel_territorial(
            RACINE / "config" / "referentiel_administratif_2025.json"
        )
        hierarchie = construire_hierarchie_historique(referentiel, self.provinces)
        self.assertEqual(len(hierarchie), 45)
        provinces_nando = sorted(p for p, r in hierarchie.items() if r == "Nando")
        self.assertEqual(provinces_nando, ["Boulkiemde", "Sanguie", "Sissili", "Ziro"])

    def test_hierarchie_historique_et_contours(self) -> None:
        referentiel = charger_referentiel_provinces_historiques(
            RACINE / "config" / "referentiel_provinces_historiques.json"
        )
        hierarchie = construire_hierarchie_par_champ(
            referentiel, self.provinces, "region_historique"
        )
        self.assertEqual(len(set(hierarchie.values())), 13)
        self.assertEqual(hierarchie["Boulkiemde"], "Centre-Ouest")
        contours = construire_contours_regions(self.geojson, hierarchie)
        self.assertEqual(len(contours), 13)
        self.assertTrue(all(len(lon) == len(lat) for lon, lat in contours.values()))

    def test_reorganisation_45_provinces_vers_17_regions(self) -> None:
        referentiel = charger_referentiel_provinces_historiques(
            RACINE / "config" / "referentiel_provinces_historiques.json"
        )
        hierarchie = construire_hierarchie_par_champ(
            referentiel, self.provinces, "region_2025"
        )
        self.assertEqual(len(hierarchie), 45)
        self.assertEqual(len(set(hierarchie.values())), 17)
        self.assertEqual(hierarchie["Boulkiemde"], "Nando")
        self.assertEqual(hierarchie["Soum"], "Soum")
        self.assertEqual(hierarchie["Oudalan"], "Liptako")

    def test_carte_2025_contient_47_provinces_et_45_series(self) -> None:
        carte = charger_geojson(
            RACINE / "application" / "data" / "provinces_47_2025.geojson"
        )
        correspondance = correspondance_carte_sources(carte)
        self.assertEqual(correspondance["province"].nunique(), 47)
        self.assertEqual(correspondance["region_2025"].nunique(), 17)
        self.assertEqual(correspondance["province_source"].nunique(), 45)
        soum = set(
            correspondance.loc[
                correspondance["region_2025"] == "Soum", "province"
            ]
        )
        tapoa = set(
            correspondance.loc[
                correspondance["region_2025"] == "Tapoa", "province"
            ]
        )
        self.assertEqual(soum, {"Djelgodji", "Karo-Peli"})
        self.assertEqual(tapoa, {"Dyamongou", "Gobnangou"})

    def test_cadrage_region_est_plus_proche_que_national(self) -> None:
        centre, zoom = calculer_cadrage_geojson(
            self.geojson, ["Boulkiemde", "Sanguie", "Sissili", "Ziro"]
        )
        self.assertGreater(zoom, 7.0)
        self.assertGreater(centre["lat"], 9)
        self.assertLess(centre["lat"], 16)

    def test_seuils_risque(self) -> None:
        self.assertEqual(categorie_risque(20), "Faible")
        self.assertEqual(categorie_risque(35), "Modéré")
        self.assertEqual(categorie_risque(55), "Élevé")
        self.assertEqual(categorie_risque(75), "Critique")

    def test_variante_komondjari_rejoint_la_carte(self) -> None:
        cadre = pd.DataFrame(
            [{
                "province": "Komondjari",
                "annee_scolaire": "2024-2025",
                "taux_abandon": 5.0,
                "taux_redoublement": 6.0,
                "taux_achevement": 70.0,
                "score_risque": 40.0,
            }]
        )
        self.assertEqual(valider_donnees(cadre, self.provinces), [])
        jointure = preparer_jointure(cadre, self.provinces)
        self.assertEqual(jointure.iloc[0]["province_geo"], "Komonjdjari")


if __name__ == "__main__":
    unittest.main()
