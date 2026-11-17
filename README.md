# SCO-RISK Burkina

Carte d'alerte et outil d'aide à la décision pour anticiper le risque de décrochage scolaire au primaire au Burkina Faso.

SCO-RISK répond au **Défi 1 - Décrochage scolaire** du Data Challenge Burkina 2026. La solution transforme les statistiques scolaires disponibles en un indice transparent, une carte interactive, une lecture régionale et une projection prudente pour l'année suivante.

**SCO** signifie *Système de Cartographie et d'Orientation* ; **RISK** désigne le risque de décrochage scolaire.

## Liens

- Dépôt GitHub : [SCO-RISKBurkina](https://github.com/kabreaziz60/SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026)
- Dashboard Streamlit : lien à ajouter après le déploiement

## Ce que permet la solution

- repérer les provinces où les signaux de décrochage sont les plus défavorables ;
- comparer les territoires pour une même année scolaire ;
- suivre l'évolution du risque de 2017-2018 à 2024-2025 ;
- sélectionner une région puis une province pour consulter ses indicateurs ;
- distinguer clairement les observations de la projection 2025-2026 ;
- produire des priorités de vérification et des recommandations pour les décideurs.

## Principes de lecture

| Période | Référentiel affiché | Statut |
|---|---|---|
| 2017-2018 à 2024-2025 | 13 régions et 45 provinces historiques | Données observées |
| 2025-2026 | 17 régions et 47 provinces actuelles | Projection |

Les deux découpages ne sont jamais fusionnés comme s'ils représentaient les mêmes unités. Les nouvelles provinces sans historique propre sont signalées comme des projections héritées de leur ancienne province source.

## Indice de risque

Le score est calculé année par année à partir de rangs percentiles :

- 50 % abandon provincial ;
- 30 % redoublement provincial ;
- 20 % non-achèvement régional.

Les seuils d'affichage sont : faible sous 35, modéré de 35 à 54,9, élevé de 55 à 74,9 et critique à partir de 75. Le score sert à prioriser une revue humaine ; il ne mesure pas une probabilité individuelle de décrochage.

## Structure du projet

```text
01_collecte/          sources référencées et inventaire
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

Le pipeline reconstruit les données dérivées, contrôle la cohérence, recalcule l'indice, évalue le modèle, produit les priorités et exécute les tests.

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

## Équipe

Projet présenté par l'équipe **SCO-RISKBurkina** dans le cadre du Data Challenge Burkina 2026, organisé par le MTDPCE et Africa Data Entry.
