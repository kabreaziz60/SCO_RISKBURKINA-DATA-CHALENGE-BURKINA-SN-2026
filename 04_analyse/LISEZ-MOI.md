# 04_analyse

Le notebook `SCO-RISKBurkina_04-analyse_D1_data-scientist_evaluation-prevision_v2.ipynb` compare une référence naïve à deux modèles Ridge explicables avec un découpage temporel strict.

Sorties :

- `SCO-RISKBurkina_04-analyse_D1_data-scientist_backtest-horizons-1-2_v2.csv` : tests rétrospectifs directs à un et deux ans ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv` : projections 2025-2026 et 2026-2027 ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_importance-modeles-h1-h2_v2.csv` : coefficients des deux horizons ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_modeles-h1-h2_v2.joblib` : modèles Ridge réentraînés ;
- rapport agrégé `rapports_prives/07_evaluation_modele.json`.

Chaque modèle n'est retenu que s'il améliore l'erreur absolue moyenne sur la cible de test 2024-2025. Les horizons un et deux ans sont estimés directement pour éviter de transformer une première prévision en fausse observation.

Contenu attendu : indicateurs, analyses, modèles, mesures de fiabilité et résultats reproductibles.

Séparez clairement exploration, entraînement, évaluation et résultats finaux. Comparez les totaux aux publications d'origine.

