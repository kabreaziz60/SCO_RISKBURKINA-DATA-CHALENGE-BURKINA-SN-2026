# 01_collecte

Contenu attendu : données brutes référencées et preuves de provenance.

- Ne modifiez jamais le fichier source original.
- Notez le producteur, la publication, la période couverte et la date de récupération.
- Conservez une empreinte SHA-256 de chaque source.
- Le classeur principal reste actuellement à la racine du projet pour éviter une copie inutile.
- `DataPack_DCB_2026.zip` est l'archive publique complète. Ne l'extrayez pas entièrement.
- Lancez `python scripts/preparer_data_pack.py` pour créer `data_pack_selection/` avec les seules sources utiles au défi 1.
- `data_pack_selection/inventaire_selection.json` conserve les tailles et empreintes des fichiers retenus sans exposer leurs valeurs.
- Lancez ensuite `python scripts/reperer_tableaux_defi1.py` pour identifier les publications et pages qui parlent d'abandon, de redoublement, d'achèvement, de promotion ou de transition.

