# Application SCO-RISK Burkina

Cette application locale fournit une carte provinciale d'alerte, une lecture des facteurs de risque, une évolution temporelle et une liste de priorités pour le décideur.

La navigation suit la hiérarchie administrative : l'utilisateur peut sélectionner une région et mettre en évidence toutes les provinces qui lui sont rattachées. La synthèse régionale, le classement interne et les tendances provinciales sont alors recalculés dans cette vue.

L'écran principal adopte une organisation de poste de décision : grande carte du Burkina à gauche, détail de la province à droite, puis historique et classement en dessous. Le cadrage cartographique est volontairement fixe ; le zoom, le déplacement et la barre d'outils sont désactivés. L'exploration se fait avec les sélecteurs d'année, de région et de province.

L'application change de référentiel selon l'année choisie. Les observations de 2017-2018 à 2024-2025 utilisent les 13 régions et 45 provinces présentes dans les sources DGESS. La projection 2025-2026 utilise les 17 régions et 47 provinces du découpage actuel. Djelgodji/Karo-Peli et Dyamongou/Gobnangou sont séparées visuellement, mais chaque paire partage encore sa série historique source ; l'application le signale et évite leur double comptage dans les agrégats.

## Identité visuelle

- logo Semaine du Numérique : site officiel `semainedunumerique.bf` ;
- armoiries du Burkina Faso 2025-présent : fichier SVG Wikimedia Commons fourni par l'équipe.

Les fichiers sont conservés localement dans `application/assets` pour que l'application reste relançable sans connexion internet.

## Lancer l'application

Depuis la racine du projet :

```powershell
streamlit run .\application\app.py
```

ou :

```powershell
.\scripts\lancer_application.ps1
```

## Données et projection

L'application lit automatiquement `03_transformation/SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv`. Si `04_analyse/SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2026_v1.csv` est présent, l'année 2025-2026 apparaît dans le sélecteur avec un avertissement explicite. Le score y est prédit ; les facteurs détaillés restent les derniers taux observés en 2024-2025.

Tant que le fichier d'indicateurs n'existe pas, l'interface affiche des données entièrement fictives. Un bandeau orange le signale. Ces valeurs ne doivent jamais être utilisées dans le rapport ou dans une décision.

## Contrat du fichier réel

Le fichier réel doit contenir au minimum :

```text
province
annee_scolaire
taux_abandon
taux_redoublement
taux_achevement
score_risque
```

Colonnes recommandées : `fiabilite`, `niveau_alerte`, `province_code`, `completude_donnees`.

Les taux et le score sont numériques. Le score est compris entre 0 et 100. Les noms des provinces doivent correspondre au référentiel cartographique ou être normalisés dans le pipeline de transformation.

## Cartes

- observations jusqu'en 2024-2025 : 45 provinces et 13 régions historiques, cohérentes avec les annuaires DGESS ;
- projection 2025-2026 : 47 provinces et 17 régions, limites COD-AB valides en août 2025 ;
- les observations historiques ne sont jamais réécrites selon les nouvelles limites.

