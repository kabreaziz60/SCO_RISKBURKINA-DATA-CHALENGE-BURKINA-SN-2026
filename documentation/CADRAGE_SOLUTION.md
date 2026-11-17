# Cadrage de la solution SCO-RISK Burkina

## Décision à soutenir

Permettre aux responsables de l'éducation d'identifier les provinces où le risque de décrochage scolaire est le plus élevé, de comprendre les facteurs associés et de prioriser les actions pour l'année scolaire suivante.

## Chaîne de valeur

1. Indicateurs d'abandon, de redoublement et d'achèvement par province et année scolaire.
2. Score de risque transparent, puis modèle prédictif évalué.
3. Carte d'alerte provinciale.
4. Fiche de lecture : niveau d'alerte, tendance, facteurs et actions suggérées.

## Produit minimal compétitif

- carte interactive des provinces ;
- score de risque de 0 à 100 et quatre niveaux d'alerte ;
- évolution 2017-2025 ;
- classement des provinces prioritaires ;
- explication des facteurs ;
- mesure de fiabilité ou de complétude ;
- recommandations opérationnelles ;
- code relançable de bout en bout ;
- documentation de 15 pages maximum ;
- dépôts aux cinq étapes avec noms normalisés et explication centralisée dans le README principal.

## Méthode proposée

### Indice initial

Construire d'abord un indice explicable à partir de trois dimensions : abandon, redoublement et non-achèvement. Normaliser chaque indicateur sur une échelle commune. Définir et justifier les poids. Tester la sensibilité du classement aux poids.

### Modèle prédictif

Prédire directement le risque à un et deux ans, pour 2025-2026 et 2026-2027. Entraîner uniquement sur le passé et réserver la cible 2024-2025 pour l'évaluation finale. Comparer chaque horizon à une référence naïve qui reconduit le dernier score. Mesurer l'erreur absolue moyenne, la corrélation des rangs et le recouvrement du groupe des dix provinces prioritaires.

### Aide à la décision

Le produit ne doit pas seulement afficher un score. Il doit répondre à quatre questions :

1. Où intervenir en priorité ?
2. Le risque progresse-t-il ?
3. Quel facteur contribue le plus au signal ?
4. Quelle action raisonnable peut être examinée par le décideur ?

## Géographie

Le Data Pack fournit le référentiel officiel COD-AB d'août 2025 : 17 régions, 47 provinces et 351 communes, avec les anciens et nouveaux P-codes. La vue historique reste calculée sur les unités réellement présentes dans les séries DGESS. La vue administrative actuelle utilise COD-AB et signale toute valeur encore agrégée ; aucune donnée historique ne sera répartie arbitrairement entre de nouvelles provinces.

## Garde-fous

- aucune donnée sensible transmise à un service d'intelligence artificielle ;
- aucune correction silencieuse ;
- aucune valeur manquante transformée automatiquement en zéro ;
- aucune ligne de total traitée comme une province ;
- aucune moyenne simple de taux lorsque les effectifs nécessaires sont disponibles ;
- toute limite du modèle est présentée au décideur.

## Plan jusqu'au dépôt

### 16 novembre

- figer le périmètre et l'architecture de la solution ;
- obtenir le Data Pack utile ;
- construire la table province-année-indicateurs ;
- documenter le nettoyage et les correspondances géographiques ;
- valider la première carte avec des données réelles.

### 17 novembre

- calculer l'indice et tester sa sensibilité ;
- entraîner et évaluer un modèle seulement si les données le permettent ;
- finaliser l'application et la fiche décideur ;
- rédiger la documentation et préparer les dépôts.

### 18 novembre

- vérifier les totaux, les sources, les noms et les versions ;
- relancer le projet depuis un environnement propre ;
- effectuer la revue finale et déposer avant la clôture.

