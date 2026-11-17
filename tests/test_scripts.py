from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook


RACINE = Path(__file__).resolve().parents[1]
SCRIPTS = RACINE / "scripts"


class ScriptsExcelTest(unittest.TestCase):
    def test_rapports_sur_classeur_fictif(self) -> None:
        with tempfile.TemporaryDirectory(dir=RACINE / "tests") as dossier:
            dossier = Path(dossier)
            classeur = dossier / "fictif.xlsx"
            inventaire = dossier / "inventaire.json"
            qualite = dossier / "qualite.json"

            livre = Workbook()
            feuille = livre.active
            feuille.title = "Donnees fictives"
            feuille.append(["province", "annee_scolaire", "effectif"])
            feuille.append(["Exemple A", "2024-2025", 100])
            feuille.append(["Exemple A", "2024-2025", 100])
            feuille.append(["Exemple B", "2024-2025", None])
            feuille.append(["Total", None, 200])
            livre.save(classeur)

            for script, sortie in [
                ("inventaire_classeur.py", inventaire),
                ("controle_qualite.py", qualite),
            ]:
                resultat = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / script),
                        "--classeur",
                        str(classeur),
                        "--sortie",
                        str(sortie),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(resultat.returncode, 0, resultat.stderr)
                self.assertTrue(sortie.exists())

            contenu_inventaire = json.loads(inventaire.read_text(encoding="utf-8"))
            contenu_qualite = json.loads(qualite.read_text(encoding="utf-8"))
            self.assertEqual(contenu_inventaire["nombre_feuilles"], 1)
            self.assertNotIn("nom", contenu_inventaire["fichier"])
            self.assertNotIn("nom", contenu_inventaire["feuilles"][0])
            feuille_qa = contenu_qualite["feuilles"][0]
            self.assertNotIn("nom", feuille_qa)
            self.assertNotIn("nom", feuille_qa["colonnes"][0])
            self.assertEqual(feuille_qa["ligne_entete_probable"], 1)
            self.assertEqual(feuille_qa["lignes_strictement_dupliquees"], 1)
            self.assertEqual(feuille_qa["lignes_total_probables"], 1)


if __name__ == "__main__":
    unittest.main()
