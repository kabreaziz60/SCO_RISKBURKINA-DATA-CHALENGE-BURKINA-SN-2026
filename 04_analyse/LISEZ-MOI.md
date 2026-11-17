# 04_analyse

Le notebook `03_evaluation_prevision.ipynb` compare une référence naïve à un modèle Ridge explicable avec un découpage temporel strict.

Sorties :

- `SCO-RISKBurkina_04-analyse_D1_data-scientist_previsions-2024-2025_v1.csv` ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2026_v1.csv` (projection opérationnelle après validation du modèle) ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_importance-modele_v1.csv` ;
- `SCO-RISKBurkina_04-analyse_D1_data-scientist_modele-ridge_v1.joblib` ;
- rapport agrégé `rapports_prives/07_evaluation_modele.json`.

Le modèle n'est retenu que s'il améliore l'erreur absolue moyenne sur 2024-2025.

Contenu attendu : indicateurs, analyses, modèles, mesures de fiabilité et résultats reproductibles.

Séparez clairement exploration, entraînement, évaluation et résultats finaux. Comparez les totaux aux publications d'origine.

