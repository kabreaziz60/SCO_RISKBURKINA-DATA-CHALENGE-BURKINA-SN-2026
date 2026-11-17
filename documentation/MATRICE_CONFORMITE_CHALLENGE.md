# Matrice de conformité — SCO-RISK Burkina

Cette grille reprend le guide officiel et les précisions données pendant la réunion de cadrage. Elle sert de contrôle avant le dépôt final.

## Réponse au défi 1

| Attente | État | Preuve ou action restante |
|---|---|---|
| Répondre à « où le risque de décrochage est-il le plus fort, par région, et comment l'anticiper ? » | Fait | Carte provinciale, navigation région-provinces, indice, projection, priorités et recommandations dans la fiche décideur. |
| Utiliser les données principales DGESS 2016-2025 | Fait | Le classeur principal fournit notamment l'achèvement primaire régional. |
| Exploiter l'historique | Fait | Huit années scolaires observées, 2017-2018 à 2024-2025. L'application s'ouvre maintenant sur 2024-2025 et permet de consulter chaque année. |
| Commencer par un indice simple | Fait | Score transparent : abandon, redoublement et non-achèvement ; deux pondérations alternatives testées. |
| Tester une anticipation | Fait | Entraînement temporel antérieur, test final 2024-2025, projection séparée 2025-2026. |
| Produire une carte d'alerte par province | Fait | Carte interactive à 45 provinces pour les observations et 47 provinces pour la projection 2025-2026, avec sélection région-provinces. |
| Mesurer la fiabilité du modèle | Fait | Comparaison à une référence naïve, MAE, RMSE, corrélation de rang et recouvrement du top 10. |

## Parcours obligatoire en cinq étapes

| Étape | État | Livrables |
|---|---|---|
| `01_collecte` | Fait | Classeur principal référencé, Data Pack conservé, sélection documentée des sources utiles. |
| `02_nettoyage` | Fait | Notebook de nettoyage, fichier unique province-année, rapport qualité et journal. |
| `03_transformation` | Fait | Indicateurs et indice de risque, analyse de sensibilité. |
| `04_analyse` | Fait avec limite documentée | Évaluation temporelle, prévisions et mesure de fiabilité. Les taux restent des moyennes non pondérées faute de dénominateurs provinciaux compatibles. |
| `05_interpretation` | Fait | Carte finale, priorités provinciales et régionales, fiche d'une page pour décideur, recommandations et limites. |

## Indispensables pour le dépôt

| Exigence | État | Priorité |
|---|---|---|
| Solution utilisable et relançable | Fait | `scripts/executer_pipeline.ps1` relance toute la chaîne et les tests. |
| Données principales correctement nettoyées | Fait avec une anomalie source signalée | Conserver la trace de l'anomalie et le contrôle des totaux. |
| Documentation de 15 pages maximum | Fait | Rapport final contrôlé dans Word : 13 pages. |
| Dépôts nommés selon le modèle | Structure prête, noms finaux manquants | Très haute ; nécessite le numéro ou nom officiel de l'équipe. |
| Un fichier LISEZ-MOI par dépôt | Présent dans les dossiers principaux | Vérifier et actualiser avant emballage. |
| Sources citées et totaux contrôlés | Sources tracées ; certains contrôles de totaux restent à formaliser | Haute. |
| Données sensibles non transmises à une IA | Respecté | Les traitements ont été exécutés localement. |

## Bonus présentés pendant la réunion

| Bonus | État | Décision |
|---|---|---|
| Sources facultatives utiles | Partiellement fait | Les annuaires CNS et la cartographie publique sont utilisés. Ne pas multiplier les sources sans utilité. |
| Carte ou tableau de bord interactif | Fait | SCO-RISK permet année, région, province et seuil d'alerte. |
| Modèle prédictif avec fiabilité | Fait | Le modèle est un bonus ; il reste séparé de l'analyse observée. |
| Dépôts à chaque étape et par rôle | Partiel | Préparer les fichiers finaux après obtention de l'identifiant d'équipe. |
| Fiche d'une page pour un décideur | Fait | `05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_fiche-decideur-2024-2025_v1.pdf`. |
| Code relançable de bout en bout | Fait | Lanceur unique et 14 tests automatisés. |

## Pièges explicitement contrôlés

- 13 régions historiques et 17 régions actuelles ne sont pas confondues.
- Les 45 provinces historiques ne sont pas transformées artificiellement en 47 séries historiques.
- Les variantes de noms de province sont normalisées sans écraser les libellés sources.
- L'année scolaire reste au format `AAAA-AAAA`.
- L'achèvement régional est étiqueté comme régional, même lorsqu'il sert de contexte à une province.
- Le préscolaire, le post-primaire et le secondaire ne sont pas mélangés au score primaire actuel.

## Ordre de travail restant

1. Conserver explicitement la limite des taux non pondérés dans le rapport et la fiche.
2. Renommer et emballer les dépôts selon l'identifiant officiel de l'équipe.
3. Effectuer le dernier contrôle des noms et des versions du paquet remis.
