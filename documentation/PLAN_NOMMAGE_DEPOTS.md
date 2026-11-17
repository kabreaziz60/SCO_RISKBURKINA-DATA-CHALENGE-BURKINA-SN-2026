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

`EQUIPE` est un emplacement provisoire à remplacer par l'identifiant officiel.

| Étape | Rôle | Nom proposé pour le dépôt |
|---|---|---|
| Collecte | engineer | `EQUIPE_01-collecte_D1_engineer_sources-defi1-referencees_v1.zip` |
| Collecte | architect | `EQUIPE_01-collecte_D1_architect_inventaire-sources_v1.json` |
| Nettoyage | engineer | `EQUIPE_02-nettoyage_D1_engineer_decrochage-province-annee-propre_v1.csv` |
| Nettoyage | engineer | `EQUIPE_02-nettoyage_D1_engineer_journal-nettoyage_v1.csv` |
| Nettoyage | architect | `EQUIPE_02-nettoyage_D1_architect_dictionnaire-variables_v1.csv` |
| Transformation | architect | `EQUIPE_03-transformation_D1_architect_indicateurs-province-annee_v1.csv` |
| Transformation | analyst | `EQUIPE_03-transformation_D1_analyst_indice-risque-sensibilite_v1.csv` |
| Analyse | scientist | `EQUIPE_04-analyse_D1_scientist_evaluation-prevision_v1.csv` |
| Analyse | scientist | `EQUIPE_04-analyse_D1_scientist_modele-ridge_v1.joblib` |
| Interprétation | analyst | `EQUIPE_05-interpretation_D1_analyst_carte-alerte-scorisk_v1.zip` |
| Interprétation | analyst | `EQUIPE_05-interpretation_D1_analyst_fiche-decideur_v1.pdf` |
| Documentation | équipe | `EQUIPE_D1_documentation-scorisk_v1.pdf` |

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
