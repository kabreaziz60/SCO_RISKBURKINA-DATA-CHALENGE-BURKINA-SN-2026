# Matrice de conformité — SCO-RISK Burkina

Cette grille reprend le guide officiel et les précisions données pendant la réunion de cadrage. Elle sert de contrôle avant le dépôt final.

## Réponse au défi 1

| Attente | État | Preuve ou action restante |
|---|---|---|
| Répondre à « où le risque de décrochage est-il le plus fort, par région, et comment l'anticiper ? » | Fait | Carte provinciale, navigation région-provinces, indice, projection, priorités et recommandations dans la fiche décideur. |
| Utiliser les données principales DGESS 2016-2025 | Fait | Le classeur principal fournit notamment l'achèvement primaire régional. |
| Exploiter l'historique | Fait | Huit années scolaires observées, 2017-2018 à 2024-2025. L'application s'ouvre maintenant sur 2024-2025 et permet de consulter chaque année. |
| Commencer par un indice simple | Fait | Score transparent : abandon, redoublement et non-achèvement ; deux pondérations alternatives testées. |
| Tester une anticipation | Fait | Deux modèles directs à horizons d'un et deux ans, test final 2024-2025, projections séparées 2025-2026 et 2026-2027. |
| Produire une carte d'alerte par province | Fait | Carte interactive à 45 provinces pour les observations et 47 provinces pour les projections, avec sélection région-provinces. |
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
| Documentation de 15 pages maximum | Fait | Rapport final LaTeX contrôlé : 14 pages PDF. |
| Dépôts nommés selon le modèle | Fait | Préfixe `SCO-RISKBurkina`, étape, défi, rôle, description et version. |
| Un fichier LISEZ-MOI par dépôt | Présent dans les dossiers principaux | Vérifier et actualiser avant emballage. |
| Sources citées et totaux contrôlés | Sources tracées ; certains contrôles de totaux restent à formaliser | Haute. |
| Données sensibles non transmises à une IA | Respecté | Les traitements ont été exécutés localement. |

## Bonus présentés pendant la réunion

| Bonus | État | Décision |
|---|---|---|
| Sources facultatives utiles | Partiellement fait | Les annuaires CNS et la cartographie publique sont utilisés. Ne pas multiplier les sources sans utilité. |
| Carte ou tableau de bord interactif | Fait | SCO-RISK permet année, région, province et seuil d'alerte. |
| Modèle prédictif avec fiabilité | Fait | Le modèle est un bonus ; il reste séparé de l'analyse observée. |
| Dépôts à chaque étape et par rôle | Fait | Dossiers `01_collecte` à `05_interpretation`, fichiers nommés et LISEZ-MOI. |
| Fiche d'une page pour un décideur | Fait | `05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_fiche-decideur-2024-2025_v1.pdf`. |
| Code relançable de bout en bout | Fait | Lanceur unique et 16 tests automatisés. |

## Pièges explicitement contrôlés

- 13 régions historiques et 17 régions actuelles ne sont pas confondues.
- Les 45 provinces historiques ne sont pas transformées artificiellement en 47 séries historiques.
- Les variantes de noms de province sont normalisées sans écraser les libellés sources.
- L'année scolaire reste au format `AAAA-AAAA`.
- L'achèvement régional est étiqueté comme régional, même lorsqu'il sert de contexte à une province.
- Le préscolaire, le post-primaire et le secondaire ne sont pas mélangés au score primaire actuel.

## Critères du jury rendus visibles

| Critère | Preuve principale |
|---|---|
| Caractère innovant | Double projection à un et deux ans, carte à double référentiel et recommandations temporelles. |
| Pertinence et rigueur | Test temporel, comparaison à une référence naïve, MAE, RMSE, rangs et top 10. |
| Visualisation et expérience utilisateur | Carte interactive, filtres hiérarchiques, détails, tendances et réinitialisation. |
| Impact possible | Priorités territoriales, actions 0-3 mois, 3-12 mois et suivi annuel. |
| Faisabilité technique et opérationnelle | Application Streamlit légère, données agrégées, déploiement GitHub. |
| Reproductibilité et documentation | Pipeline local, notebooks, dictionnaire, journaux, 16 tests et rapport de 14 pages. |

## Ordre de travail restant

1. Déployer le dashboard et inscrire son URL dans le README et le PDF.
2. Effectuer le dernier contrôle visuel de la version déployée.
3. Déposer les cinq dossiers, le rapport et les deux liens dans l'espace challenge.
