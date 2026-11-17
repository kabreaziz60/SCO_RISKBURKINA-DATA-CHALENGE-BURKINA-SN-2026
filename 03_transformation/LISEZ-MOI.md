# 03_transformation

Le notebook `02_construction_indice_risque.ipynb` produit :

- `SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv` : fichier directement utilisable par l'application ;
- `SCO-RISKBurkina_03-transformation_D1_data-scientist_sensibilite-ponderations_v1.csv` : stabilité du classement lorsque les poids changent ;
- `SCO-RISKBurkina_03-transformation_D1_architect_correspondance-45-provinces-17-regions_v1.csv` : passage documenté des 45 provinces historiques vers les 17 régions actuelles ;
- `SCO-RISKBurkina_03-transformation_D1_architect_correspondance-47-provinces-45-series_v1.csv` : lien entre chaque province cartographiée en 2025 et sa série statistique historique source.

L'indice principal combine abandon, redoublement et non-achèvement régional avec des poids de 50 %, 30 % et 20 %.

Les observations utilisent les 13 régions et 45 provinces historiques jusqu'en 2024-2025. Seule la projection 2025-2026 est reportée sur les 17 régions et 47 provinces actuelles. Aucune valeur n'est inventée : Djelgodji et Karo-Peli partagent la série historique Soum ; Dyamongou et Gobnangou partagent la série historique Tapoa. Les agrégats utilisent la source une seule fois afin d'éviter le double comptage.

Contenu attendu : tables harmonisées et variables calculées.

Documentez le grain de chaque table, par exemple province - année scolaire - niveau - sexe, ainsi que chaque formule de taux ou ratio.

