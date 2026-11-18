# SCO-RISK Burkina

Carte d'alerte et outil d'aide à la décision pour anticiper le risque de décrochage scolaire au primaire au Burkina Faso.

SCO-RISK répond au **Défi 1 - Décrochage scolaire** du Data Challenge Burkina 2026. La solution transforme les statistiques scolaires disponibles en un indice transparent, une carte interactive, une lecture régionale et deux projections prudentes à un et deux ans.

**SCO** signifie *Système de Cartographie et d'Orientation* ; **RISK** désigne le risque de décrochage scolaire.

## Liens

- Dépôt GitHub : [SCO-RISKBurkina](https://github.com/kabreaziz60/SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026)
- Dashboard Streamlit : lien à ajouter après le déploiement

## Ce que permet la solution

- repérer les provinces où les signaux de décrochage sont les plus défavorables ;
- comparer les territoires pour une même année scolaire ;
- suivre l'évolution du risque de 2017-2018 à 2024-2025 ;
- sélectionner une région puis une province pour consulter ses indicateurs ;
- distinguer clairement les observations des projections 2025-2026 et 2026-2027 ;
- consulter séparément le contexte d'urgence éducative ESU de février 2026 ;
- produire des priorités de vérification et des recommandations pour les décideurs.

## Principes de lecture

| Période | Référentiel affiché | Statut |
|---|---|---|
| 2017-2018 à 2024-2025 | 13 régions et 45 provinces historiques | Données observées |
| 2025-2026 | 17 régions et 47 provinces actuelles | Projection |
| 2026-2027 | 17 régions et 47 provinces actuelles | Projection à deux ans |

Les deux découpages ne sont jamais fusionnés comme s'ils représentaient les mêmes unités. Les nouvelles provinces sans historique propre sont signalées comme des projections héritées de leur ancienne province source.

## Indice de risque

Le score est calculé année par année à partir de rangs percentiles :

- 50 % abandon provincial ;
- 30 % redoublement provincial ;
- 20 % non-achèvement régional.

Les seuils d'affichage sont : faible sous 35, modéré de 35 à 54,9, élevé de 55 à 74,9 et critique à partir de 75. Le score sert à prioriser une revue humaine ; il ne mesure pas une probabilité individuelle de décrochage.

### Contexte sécuritaire et urgence éducative

Un module complémentaire exploite le rapport statistique mensuel ESU de février 2026 au niveau des 17 régions. Il présente les élèves déplacés internes du primaire, les structures primaires délocalisées et les structures rouvertes. Un indice descriptif de pression combine 60 % du rang des effectifs d'EDI et 40 % du rang des structures délocalisées.

Cet indice reste **séparé du score SCO-RISK** : les valeurs sont des effectifs, non des taux, et ne démontrent aucune causalité avec le décrochage. Le croisement sert uniquement à repérer les territoires où une vérification conjointe DGESS/ESU est prioritaire.

## Structure du projet

```text
01_collecte/          classeur Excel original, conservé sans modification
02_nettoyage/         notebook, table propre et journal de nettoyage
03_transformation/    indicateurs, correspondances et sensibilité
04_analyse/           évaluation temporelle, modèle et prévisions
05_interpretation/    priorités et fiche décideur
application/          application Streamlit et cartes
config/               référentiels administratifs
documentation/        rapport, dictionnaire et méthode
scripts/              chaîne locale reproductible
tests/                tests automatisés
```

Les dossiers d'étape contiennent uniquement leurs livrables. Toute l'explication du parcours est centralisée dans ce README afin d'éviter les fichiers répétitifs. Les fichiers suivent le modèle officiel `EQUIPE_ETAPE_DEFI_ROLE_description_vN`.

| Dossier | Contenu public | Rôle dans le parcours |
|---|---|---|
| `01_collecte` | Classeur Excel et rapport ESU originaux | Conserve les deux sources réellement utilisées strictement inchangées. |
| `02_nettoyage` | Tables scolaires et ESU nettoyées, notebook | Harmonise les noms, traite les valeurs manquantes et conserve la trace des anomalies. |
| `03_transformation` | Indicateurs, correspondances, sensibilité et pression ESU | Construit les indicateurs sans fusionner le contexte ESU avec le score SCO-RISK. |
| `04_analyse` | Backtests, modèles, projections et croisement ESU | Évalue les horizons un et deux ans et repère les doubles signaux à vérifier. |
| `05_interpretation` | Priorités, synthèses et fiche décideur | Traduit les résultats en alertes et en actions opérationnelles prudentes. |

### Conservation de la source originale

Le fichier principal collecté est le classeur Excel DGESS 2016-2025 à 14 feuilles. Le rapport ESU de février 2026 est la seule source complémentaire ajoutée. Ils sont conservés dans `01_collecte` sous leur nom d'origine et ne sont jamais modifiés par les traitements. Le Data Pack complet, beaucoup plus volumineux, n'est pas dupliqué.

## Installation locale

Prérequis : Python 3.11 ou version compatible et PowerShell sous Windows.

```powershell
git clone https://github.com/kabreaziz60/SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026.git
cd SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Le dépôt contient les deux sources du challenge effectivement exploitées, leurs tables dérivées et les éléments indispensables au fonctionnement du dashboard. Le reste du Data Pack n'est pas dupliqué.

## Lancer le tableau de bord

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\lancer_application.ps1
```

Ou directement :

```powershell
python -m streamlit run application\app.py
```

Dans l'interface :

1. choisir l'année scolaire ;
2. choisir une région ;
3. choisir une province ;
4. ajuster le seuil d'alerte ;
5. survoler la carte pour lire le score et les indicateurs ;
6. utiliser **Réinitialiser les filtres** pour revenir à la vue nationale.

## Reproduire toute la chaîne

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\executer_pipeline.ps1
```

Le pipeline contrôle la cohérence, recalcule l'indice, évalue le modèle, intègre le contexte ESU, produit les priorités et exécute les tests. Les deux sources originales sont lues dans `01_collecte`. La reconstruction complète de la table scolaire nettoyée nécessite aussi les annuaires sélectionnés du Data Pack ; lorsqu'ils ne sont pas dupliqués, le pipeline repart de la table nettoyée publiée.

Pour lancer uniquement les tests :

```powershell
python -m unittest discover -s tests -v
```

## Confidentialité et publication

À l'exception du classeur principal et du rapport ESU fournis pour le challenge et conservés dans `01_collecte`, le dépôt public ne doit pas contenir :

- d'autres données brutes ou tables détaillées non nécessaires au fonctionnement public ;
- le dossier `rapports_prives` ;
- les fichiers temporaires, caches et journaux locaux ;
- des informations personnelles ou des secrets d'accès.

Les traitements sont réalisés localement. Les données sources ne sont pas envoyées vers un service d'intelligence artificielle.

## Limites

- les taux provinciaux sont des moyennes non pondérées faute de dénominateurs compatibles ;
- l'achèvement est disponible au niveau régional ;
- deux nouvelles provinces n'ont pas de série historique autonome dans les sources exploitées ;
- la projection sert à organiser les vérifications, pas à automatiser une décision publique.
- le contexte ESU est daté du 28 février 2026, agrégé par région et exprimé en effectifs non rapportés à une population scolaire ;
- le croisement SCO-RISK/ESU est descriptif et ne permet pas d'attribuer causalement le décrochage à la situation sécuritaire.

## Documentation

Le rapport méthodologique LaTeX et sa version PDF sont disponibles dans le dossier `documentation` et dans `output/pdf`.

## Sources et technologies

- **Données éducatives :** DGESS / MEBAPLN, statistiques et annuaires du primaire 2016-2025 ;
- **Urgence éducative :** MENAPLN/DGESS, Rapport statistique mensuel ESU, février 2026 ;
- **Cartographie :** limites historiques cohérentes avec les annuaires et COD-AB / OCHA, version d'août 2025 ;
- **Cadre du projet :** document et Data Pack du Data Challenge Burkina 2026 ;
- **Application :** Python, Streamlit, Pandas, NumPy et Plotly ;
- **Modélisation :** scikit-learn, modèle Ridge et évaluation temporelle ;
- **Formats :** CSV, JSON et GeoJSON.

## Équipe

Projet présenté par l'équipe **SCO-RISKBurkina** dans le cadre du Data Challenge Burkina 2026, organisé par le MTDPCE et Africa Data Entry.
