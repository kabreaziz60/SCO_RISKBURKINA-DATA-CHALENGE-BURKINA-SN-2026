# Validation du périmètre — Défi 1

## Question traitée

Où le risque de décrochage au **primaire** est-il le plus fort, par territoire et par année scolaire, et comment aider les autorités à le repérer suffisamment tôt ?

## Périmètre actuellement confirmé

- Niveau scolaire central : **enseignement primaire**.
- Classes utilisées pour l'abandon : CP1, CP2, CE1, CE2 et CM1.
- Classes utilisées pour le redoublement : CP1 à CM2.
- Achèvement : taux du primaire disponible au niveau de l'ancienne région.
- Période : huit années scolaires, de 2017-2018 à 2024-2025.
- Unité analytique : 45 provinces historiques.
- Référentiel temporel : 13 régions historiques pour les observations.
- Vue d'aide à la décision actuelle : rattachement documenté aux 17 régions de 2025, sans inventer de données pour les deux nouvelles provinces.

Le fichier de travail contient 360 lignes : 45 provinces × 8 années scolaires. Une anomalie présente dans la publication source est conservée, signalée et exclue des moyennes lorsqu'elle sort de l'intervalle 0–100.

Un contrôle arithmétique complémentaire a testé 1 800 triplets de taux, pour CP1 à CM1 : promotion + redoublement + abandon. Avec une tolérance de 0,25 point pour les arrondis, aucune incohérence n'a été trouvée en dehors de l'anomalie source déjà signalée. Aucun triplet n'est incomplet et aucun doublon province-année n'est présent.

## Ce qui n'entre pas encore dans le score

- Préscolaire : non utilisé dans le score actuel.
- Secondaire : hors du périmètre actuel.
- Post-primaire : non utilisé actuellement ; la transition après le primaire reste une extension possible, uniquement si elle apporte une information utile au défi 1.
- Données individuelles d'élèves : absentes et non nécessaires.

## Lecture géographique de la carte

### Observations 2017-2018 à 2024-2025

- 13 régions historiques ;
- 45 provinces historiques ;
- contours régionaux renforcés ;
- sélection d'une région pour afficher ses provinces et leurs indicateurs.

### Projections 2025-2026 et 2026-2027

- 17 régions administratives actuelles ;
- 47 provinces administratives actuelles sur la carte COD-AB ;
- Djelgodji/Karo-Peli et Dyamongou/Gobnangou sont séparées visuellement ;
- chaque paire issue d'une scission partage encore la projection de sa province historique source ;
- les agrégats dédupliquent ces séries afin d'éviter le double comptage.

Deux modèles directs distincts sont utilisés : un horizon d'un an et un horizon de deux ans. La seconde projection n'est donc pas calculée en réutilisant artificiellement la première comme une observation.

## Décisions méthodologiques à conserver

1. Ne jamais confondre année scolaire et année civile.
2. Ne jamais présenter les 17 régions comme si elles existaient sur toute la série historique.
3. Ne pas appeler « taux provincial » l'achèvement régional répété comme facteur de contexte.
4. Ne pas mélanger préscolaire, primaire et secondaire dans un indicateur unique.
5. Présenter la prévision comme une aide à la revue humaine, jamais comme une décision automatique.

## Prochaine validation avant amélioration du modèle

Les huit annuaires contiennent bien des tableaux d'effectifs et de redoublants par niveau et par province. Avant de les utiliser comme poids, il reste à vérifier que leur année et leur population de référence correspondent exactement au dénominateur des taux de promotion, redoublement et abandon. Il ne faut pas appliquer une pondération approximative.

Si cette correspondance est confirmée, les taux provinciaux seront recalculés avec les effectifs appropriés. Sinon, la moyenne non pondérée sera conservée et indiquée clairement comme limite.
