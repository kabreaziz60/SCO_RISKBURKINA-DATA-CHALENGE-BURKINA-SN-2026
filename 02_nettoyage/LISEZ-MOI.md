# 02_nettoyage

Le notebook `01_nettoyage_donnees_decrochage.ipynb` construit localement le fichier unique :

`SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv`

Ce CSV contient les indicateurs provinciaux d'abandon et de redoublement issus des annuaires CNS, ainsi que l'achèvement au niveau régional provenant du classeur principal.

Commande équivalente sans notebook :

```powershell
python scripts\construire_fichier_decrochage.py
```

Le rapport de contrôle agrégé est écrit dans `rapports_prives/05_qualite_fichier_decrochage.json`.

Contenu attendu : données propres, règles appliquées et journal de nettoyage.

Aucune suppression ou correction ne doit être automatique sans examen. Documentez notamment les doublons, valeurs manquantes, lignes de total, variantes de provinces et changements de découpage régional.

