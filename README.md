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

## Structure du projet

```text
depot_prive/01_collecte/  classeur original, uniquement en local et dans le dépôt sécurisé
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
| `01_collecte` privé | Classeur Excel original à 14 feuilles | Constitue la donnée réellement collectée. Il est préparé localement dans `depot_prive/01_collecte` et reste hors de GitHub. |
| `02_nettoyage` | Table province-année nettoyée et notebook | Harmonise les noms, traite les valeurs manquantes et conserve la trace des anomalies. |
| `03_transformation` | Indicateurs, correspondances territoriales et sensibilité | Construit l'indice de risque et organise les référentiels 13/17 régions et 45/47 provinces. |
| `04_analyse` | Backtests, notebook, modèles, coefficients et projections | Évalue les horizons un et deux ans et produit 2025-2026 et 2026-2027. |
| `05_interpretation` | Priorités, synthèse régionale et fiche décideur | Traduit les résultats en alertes et en actions opérationnelles. |

### Pourquoi les données brutes ne figurent pas dans `01_collecte` sur GitHub

Le fichier principal collecté est le classeur Excel DGESS 2016-2025 à 14 feuilles. Il est conservé localement dans `depot_prive/01_collecte` pour la remise sécurisée. Son manifeste est placé dans `documentation`, tandis que GitHub contient uniquement le code et les données agrégées nécessaires au fonctionnement. Cette séparation évite de republier le classeur du challenge sans autorisation. Le Data Pack complet, beaucoup plus volumineux et facultatif, n'est pas dupliqué dans le dépôt final.

## Installation locale

Prérequis : Python 3.11 ou version compatible et PowerShell sous Windows.

```powershell
git clone https://github.com/kabreaziz60/SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026.git
cd SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Les fichiers sources du challenge ne sont pas publiés. Le dépôt contient uniquement les tables agrégées et dérivées indispensables au fonctionnement du dashboard et à la reproductibilité des résultats.

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

Le pipeline reconstruit les données dérivées, contrôle la cohérence, recalcule l'indice, évalue le modèle, produit les priorités et exécute les tests. Dans le dépôt public, il repart de la table nettoyée publiée puisque le classeur brut est volontairement exclu ; dans l'environnement autorisé du challenge, la présence d'un unique classeur à la racine relance aussi l'étape de nettoyage.

Pour lancer uniquement les tests :

```powershell
python -m unittest discover -s tests -v
```

## Confidentialité et publication

Le dépôt public ne doit pas contenir :

- le classeur original du challenge ;
- les données brutes ou les tables détaillées non nécessaires au fonctionnement public ;
- le dossier `rapports_prives` ;
- les fichiers temporaires, caches et journaux locaux ;
- des informations personnelles ou des secrets d'accès.

Les traitements sont réalisés localement. Les données sources ne sont pas envoyées vers un service d'intelligence artificielle.

## Limites

- les taux provinciaux sont des moyennes non pondérées faute de dénominateurs compatibles ;
- l'achèvement est disponible au niveau régional ;
- deux nouvelles provinces n'ont pas de série historique autonome dans les sources exploitées ;
- la projection sert à organiser les vérifications, pas à automatiser une décision publique.

## Documentation

Le rapport méthodologique LaTeX et sa version PDF sont disponibles dans le dossier `documentation` et dans `output/pdf`.

## Sources et technologies

- **Données éducatives :** DGESS / MEBAPLN, statistiques et annuaires du primaire 2016-2025 ;
- **Cartographie :** limites historiques cohérentes avec les annuaires et COD-AB / OCHA, version d'août 2025 ;
- **Cadre du projet :** document et Data Pack du Data Challenge Burkina 2026 ;
- **Application :** Python, Streamlit, Pandas, NumPy et Plotly ;
- **Modélisation :** scikit-learn, modèle Ridge et évaluation temporelle ;
- **Formats :** CSV, JSON et GeoJSON.

## Équipe

Projet présenté par l'équipe **SCO-RISKBurkina** dans le cadre du Data Challenge Burkina 2026, organisé par le MTDPCE et Africa Data Entry.
