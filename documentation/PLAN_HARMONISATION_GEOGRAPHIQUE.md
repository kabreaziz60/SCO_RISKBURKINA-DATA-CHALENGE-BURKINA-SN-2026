# Plan d'harmonisation géographique

## Pourquoi cette étape précède le nettoyage

Le découpage administratif a changé en 2025. Le Burkina Faso est passé de 13 à 17 régions et de 45 à 47 provinces. Certaines régions ont seulement changé de nom, tandis que d'autres ont été scindées. Une série 2016-2025 ne peut donc pas être regroupée sous un seul nom de région sans préciser le référentiel territorial.

## Règles de travail

1. Conserver le libellé original dans `region_source` ou `province_source`.
2. Créer un identifiant géographique séparé ; ne jamais écraser la source.
3. Ajouter `referentiel_geo` avec une valeur explicite : `ancien_13`, `nouveau_17` ou `a_confirmer`.
4. Conserver l'année scolaire sous la forme `AAAA-AAAA`. Ne pas la convertir en une seule année civile sans justification.
5. Pour une région renommée sans changement territorial confirmé, conserver la relation un-vers-un et sa source officielle.
6. Pour une région scindée, ne jamais diviser une valeur historique de façon égale ou arbitraire.
7. Reconstruire les nouvelles régions uniquement à partir de données provinciales ou communales dont l'appartenance est vérifiée.
8. Quand une province a elle-même été créée ou scindée, marquer l'historique `non_attribuable` si aucune donnée plus fine n'existe.
9. Additionner les effectifs avant de recalculer les taux. Ne pas calculer une moyenne simple de taux régionaux.
10. Conserver les lignes de total pour contrôler les résultats, mais ne pas les traiter comme des observations territoriales.

## Deux vues à produire

### Vue historique comparable

- Période : 2016-2025 selon la couverture réelle du classeur.
- Référentiel : anciennes 13 régions.
- Objectif : tendances temporelles cohérentes.

### Vue administrative actuelle

- Référentiel : nouvelles 17 régions.
- Objectif : outil d'aide à la décision actuel.
- Condition : reconstitution à partir d'un niveau géographique suffisamment fin et vérifié.

## Reconstruction cartographique 2025

Les départements existants conservent juridiquement leurs limites. La nouvelle carte ne sera donc pas dessinée à la main. Elle sera reconstruite par union des polygones départementaux selon le référentiel officiel.

- `Dyamongou` = Botou + Kantchari ;
- `Karo-Peli` = Arbinda + Koutougou ;
- `Gobnangou` = Diapaga + Logobou + Namounou + Partiaga + Tansarga ;
- `Djelgodji` = Baraboulé + Diguel + Djibo + Kelbo + Nassoumbou + Pobé-Mengao.

Les 47 provinces seront ensuite regroupées en 17 régions selon `config/referentiel_administratif_2025.json`. La carte historique à 45 provinces restera conservée séparément.

Cette reconstruction sera contrôlée sur trois points : couverture complète du territoire, absence de chevauchement et correspondance des 350 départements avec une seule province actuelle.

## Colonnes minimales de la future table géographique

- `geo_id`
- `nom_source`
- `nom_normalise`
- `niveau_geo`
- `ancienne_region_13`
- `nouvelle_region_17`
- `referentiel_geo`
- `date_debut_validite`
- `date_fin_validite`
- `statut_correspondance`
- `source_officielle`
- `commentaire_validation`

## Contrôles humains obligatoires

- confirmer chaque scission avec la carte et le décret officiels ;
- vérifier l'appartenance des provinces et communes ;
- repérer les variantes orthographiques avant de créer les règles de normalisation ;
- examiner séparément l'année scolaire 2024-2025, qui chevauche la réforme de juillet 2025 ;
- documenter toute décision dans le journal de nettoyage.

