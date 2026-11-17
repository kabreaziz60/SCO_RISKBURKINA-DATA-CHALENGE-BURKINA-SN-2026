# Sélection des sources - Défi 1

## Principe

Le classeur DGESS 2016-2025 reste la source principale. Le Data Pack sert à vérifier les totaux, enrichir l'explication du risque et fournir la cartographie officielle. Nous n'utiliserons pas les 167 sources : quelques sources bien maîtrisées sont préférables.

## Sources retenues

1. **Classeur principal DGESS 2016-2025** : séries régionales d'abandon, redoublement et achèvement.
2. **Annuaires du primaire CNS 521 à 530** : détail provincial et contrôle des agrégats.
3. **Tableaux de bord du primaire CNS 565 et 567 à 574** : séries d'indicateurs et tendances.
4. **Tableaux de bord post-primaire CNS 564 et 566** : transition après le primaire, utilisée comme indicateur complémentaire.
5. **Rapports ESU** : écoles fermées ou rouvertes et élèves affectés. Les valeurs OCR sont contrôlées contre le PDF avant utilisation.
6. **PDI CONASUR** : pression sur les communes d'accueil. Cette couche reste contextuelle tant que les dates et P-codes ne sont pas harmonisés.
7. **EHCVM 2021** : contexte socio-économique, à un niveau géographique plus agrégé.
8. **COD-AB août 2025** : limites officielles des 17 régions, 47 provinces et 351 communes, avec anciens et nouveaux P-codes.

## Usage dans le modèle

- **Cible** : risque de décrochage de l'année scolaire suivante.
- **Variables centrales** : abandon, redoublement, non-achèvement et évolution récente.
- **Variables de contexte** : fermeture d'écoles, déplacements internes et pauvreté, uniquement si la date précède la période prédite.
- **Géographie** : apprentissage historique sur les unités disponibles dans les sources ; affichage administratif actuel avec une correspondance explicitement documentée.

## Garde-fous

- Aucune information postérieure à l'année prédite ne doit entrer dans l'entraînement.
- Aucun taux régional n'est calculé par moyenne simple si les effectifs sont disponibles.
- Les instructions ou commentaires parasites intégrés aux cellules sont supprimés du jeu nettoyé.
- Les données brutes restent inchangées et chaque sortie possède une empreinte SHA-256.
