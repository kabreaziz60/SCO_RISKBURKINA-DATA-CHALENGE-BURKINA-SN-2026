# Plan de nommage des dépôts

## Règle officielle

Format :

`EQUIPE_ETAPE_DEFI_ROLE_description_vN.extension`

Exemple du guide :

`E07_02-nettoyage_D1_engineer_effectifs-primaire-propres_v2.csv`

Règles à respecter :

- utiliser uniquement l'identifiant officiel de l'équipe, jamais les noms personnels ;
- ne mettre ni espace ni accent ;
- indiquer l'étape, le défi `D1`, le rôle, une description courte et la version ;
- un fichier correspond à une seule étape ;
- centraliser l'explication du parcours dans le README principal pour éviter les fichiers répétitifs ;
- conserver les fichiers sources originaux dans le projet local et créer des copies nommées pour le dépôt final.

## Proposition pour SCO-RISK

L'identifiant d'équipe retenu est `SCO-RISKBurkina`.

| Étape | Rôle | Nom proposé pour le dépôt |
|---|---|---|
| Collecte | source originale | `DONNEES_STATISTQUES_ PRESCOLAIRE ET PRIMAIRE_2016_2025_DCB.xlsx` |
| Nettoyage | engineer | `SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv` |
| Transformation | engineer | `SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_backtest-horizons-1-2_v2.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_modeles-h1-h2_v2.joblib` |
| Interprétation | analyst | `SCO-RISKBurkina_05-interpretation_D1_analyst_priorites-2024-2025_v1.csv` |
| Interprétation | analyst | `SCO-RISKBurkina_05-interpretation_D1_analyst_fiche-decideur-2024-2025_v1.pdf` |
| Documentation | équipe | `SCO-RISKBurkina_D1_documentation-solution_v2.pdf` |

## Documentation centrale

Le README principal précise ce que contient chaque dossier, les sources, les scripts producteurs, les contrôles, les limites et l'ordre de reproduction. Les cinq dossiers d'étape restent ainsi réservés à leurs livrables.

## Décision de sécurité

Le classeur original n'est jamais modifié ni renommé. Les noms normalisés s'appliquent aux livrables produits aux étapes 02 à 05. Le Data Pack complet n'est pas dupliqué ; chaque source complémentaire effectivement utilisée sera ajoutée séparément avec son nom d'origine.
