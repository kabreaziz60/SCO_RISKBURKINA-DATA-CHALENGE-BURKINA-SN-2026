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
- ajouter un fichier `LISEZ-MOI` à chaque dépôt ;
- conserver les fichiers sources originaux dans le projet local et créer des copies nommées pour le dépôt final.

## Proposition pour SCO-RISK

L'identifiant d'équipe retenu est `SCO-RISKBurkina`.

| Étape | Rôle | Nom proposé pour le dépôt |
|---|---|---|
| Collecte | engineer | `SCO-RISKBurkina_01-collecte_D1_engineer_manifeste-sources_v1.csv` |
| Nettoyage | engineer | `SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv` |
| Transformation | engineer | `SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_backtest-horizons-1-2_v2.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv` |
| Analyse | scientist | `SCO-RISKBurkina_04-analyse_D1_data-scientist_modeles-h1-h2_v2.joblib` |
| Interprétation | analyst | `SCO-RISKBurkina_05-interpretation_D1_analyst_priorites-2024-2025_v1.csv` |
| Interprétation | analyst | `SCO-RISKBurkina_05-interpretation_D1_analyst_fiche-decideur-2024-2025_v1.pdf` |
| Documentation | équipe | `SCO-RISKBurkina_D1_documentation-solution_v2.pdf` |

## Fichiers LISEZ-MOI

Chaque dépôt contiendra un fichier court, par exemple :

`EQUIPE_02-nettoyage_D1_LISEZ-MOI_v1.txt`

Il précisera :

1. ce que contient le dépôt ;
2. la source des données ;
3. le script ou notebook qui l'a produit ;
4. les contrôles effectués ;
5. les limites connues ;
6. l'ordre de reproduction.

## Décision de sécurité

Les fichiers du projet ne seront pas renommés directement. Une arborescence de dépôt séparée sera générée afin de préserver les sources, les notebooks et les chemins utilisés par les scripts.
