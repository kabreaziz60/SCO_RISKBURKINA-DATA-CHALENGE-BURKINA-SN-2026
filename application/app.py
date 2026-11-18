from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scorisk.core import (
    calculer_cadrage_geojson,
    categorie_risque,
    charger_geojson,
    charger_referentiel_provinces_historiques,
    charger_referentiel_territorial,
    correspondance_carte_sources,
    construire_contours_regions,
    construire_hierarchie_historique,
    construire_hierarchie_par_champ,
    generer_donnees_demo,
    preparer_jointure,
    provinces_geojson,
    projeter_donnees_sur_carte,
    recommandations,
    valider_donnees,
)


DOSSIER_APP = Path(__file__).resolve().parent
RACINE = DOSSIER_APP.parent
CARTE_HISTORIQUE = DOSSIER_APP / "data" / "provinces_45_2017.geojson"
CARTE_2025 = DOSSIER_APP / "data" / "provinces_47_2025.geojson"
REFERENTIEL = RACINE / "config" / "referentiel_administratif_2025.json"
REFERENTIEL_HISTORIQUE = RACINE / "config" / "referentiel_provinces_historiques.json"
DONNEES_REELLES = RACINE / "03_transformation" / "SCO-RISKBurkina_03-transformation_D1_engineer_indicateurs-province-annee_v1.csv"
PREVISIONS_FUTURES = RACINE / "04_analyse" / "SCO-RISKBurkina_04-analyse_D1_data-scientist_projection-2025-2027_v2.csv"
PRIORITES_DECIDEUR = RACINE / "05_interpretation" / "SCO-RISKBurkina_05-interpretation_D1_analyst_priorites-2024-2025_v1.csv"
CONTEXTE_ESU = RACINE / "05_interpretation" / "SCO-RISKBurkina_05-interpretation_D1_data-analyst_priorites-contexte-urgence_v1.csv"
LOGO_SN = DOSSIER_APP / "assets" / "logo_semaine_numerique.png"
LOGO_ADE = DOSSIER_APP / "assets" / "logo_africa_data_entry.jpg"
ARMOIRIES = DOSSIER_APP / "assets" / "armoiries_burkina_faso_2025.svg"


def image_data_uri(chemin: Path) -> str:
    contenu = base64.b64encode(chemin.read_bytes()).decode("ascii")
    type_mime = {
        ".svg": "image/svg+xml",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }.get(chemin.suffix.casefold(), "application/octet-stream")
    return f"data:{type_mime};base64,{contenu}"


def reinitialiser_filtres() -> None:
    # Affecter explicitement les valeurs de départ évite qu'un ancien choix
    # reste affiché dans un widget pendant que la carte est déjà réinitialisée.
    st.session_state["filtre_annee"] = "2024-2025"
    st.session_state["filtre_region"] = "Toutes les régions"
    st.session_state["filtre_province"] = "Oudalan"
    st.session_state["filtre_seuil"] = 55

st.set_page_config(
    page_title="SCO-RISK Burkina",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --ink:#102a43; --muted:#52667a; --blue:#075985; --navy:#082f49; --cyan:#0891b2; --orange:#d97706; --surface:#ffffff; --line:#d8e5ee; }
    html, body, [class*="css"] { font-family:"Segoe UI", Arial, sans-serif; }
    .stApp { background:radial-gradient(circle at 76% 0%,#e8f7fb 0,transparent 24rem),linear-gradient(180deg,#f7fbfd 0,#f2f6f9 100%); color:var(--ink); }
    .block-container { width:100% !important; max-width:none !important; margin:0 !important; padding:1.85rem 1.35rem 3rem 1.2rem !important; }
    [data-testid="stMainBlockContainer"] { width:100% !important; max-width:none !important; margin-left:0 !important; margin-right:0 !important; }
    .block-container p, .block-container li { font-size:1rem; line-height:1.55; }
    .block-container h2 { color:var(--navy); font-size:1.55rem !important; letter-spacing:-.02em; margin-top:1.4rem; }
    .block-container h3 { color:var(--navy); font-size:1.25rem !important; letter-spacing:-.01em; }
    [data-testid="stCaptionContainer"] { color:#465f72 !important; opacity:1 !important; }
    [data-testid="stCaptionContainer"] p { color:#465f72 !important; opacity:1 !important; font-size:.94rem !important; line-height:1.5 !important; }
    [data-testid="stMetric"] { min-height:130px; background:linear-gradient(145deg,#ffffff,#f8fcfe); border:1px solid var(--line); border-radius:18px; padding:18px 18px 15px; box-shadow:0 10px 30px rgba(15,42,67,.08); position:relative; overflow:hidden; }
    [data-testid="stMetric"]::before { content:""; position:absolute; inset:0 auto 0 0; width:5px; background:linear-gradient(180deg,#0891b2,#075985); }
    [data-testid="stMetricLabel"] p { color:#425c70 !important; font-size:.88rem !important; font-weight:800 !important; letter-spacing:.02em; text-transform:uppercase; }
    [data-testid="stMetricValue"] { color:#082f49 !important; font-size:2rem !important; font-weight:800 !important; letter-spacing:-.04em; }
    [data-testid="stMetricDelta"] { color:#52667a !important; font-size:.82rem !important; white-space:normal !important; overflow:visible !important; }
    [data-testid="stMetricDelta"] > div { white-space:normal !important; overflow:visible !important; text-overflow:clip !important; line-height:1.25 !important; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#e9f7fb 0,#f5fafc 55%,#ffffff 100%); border-right:1px solid #cfe0ea; width:310px !important; min-width:310px !important; max-width:310px !important; transform:none !important; visibility:visible !important; box-shadow:8px 0 30px rgba(8,47,73,.06); }
    [data-testid="stSidebar"] > div:first-child { width:310px !important; padding:1.25rem 1.1rem 1.5rem !important; }
    [data-testid="stSidebar"] label p { color:#0b344d !important; font-size:1rem !important; font-weight:750 !important; margin-bottom:.35rem !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background:white !important; border:1px solid #adc9d8 !important; min-height:48px; border-radius:11px !important; box-shadow:0 3px 10px rgba(15,42,67,.04); }
    [data-testid="stSidebar"] [data-baseweb="select"] span { color:#16384c !important; font-size:.98rem !important; font-weight:600 !important; }
    [data-testid="stSidebar"] .stSelectbox { margin-bottom:.5rem !important; }
    [data-testid="stSidebar"] .stSlider { margin-top:.65rem !important; }
    [data-testid="stSidebar"] .stSlider p { font-size:.98rem !important; }
    [data-testid="stSidebar"] button { min-height:48px; border:1px solid #90b6c9; border-radius:11px; color:#073b58; font-weight:800; font-size:.96rem; background:white; box-shadow:0 4px 12px rgba(15,42,67,.05); }
    [data-testid="stSidebar"] button:hover { color:white; background:#075985; border-color:#075985; }
    [data-testid="stSidebar"] hr { margin:.45rem 0 !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] { position:sticky; bottom:.65rem; z-index:20; padding:.45rem 0 .2rem; background:linear-gradient(180deg,rgba(245,250,252,.72),#f5fafc 34%); }
    [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:none !important; visibility:hidden !important; }
    [data-testid="stAppViewContainer"] { margin-left:0 !important; }
    [data-testid="stPlotlyChart"] { border:1px solid var(--line); border-radius:20px; overflow:hidden; background:white; box-shadow:0 14px 35px rgba(15,42,67,.09); }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:16px; overflow:hidden; box-shadow:0 8px 24px rgba(15,42,67,.06); }
    [data-testid="stExpander"] { background:white; border:1px solid var(--line); border-radius:14px; box-shadow:0 5px 18px rgba(15,42,67,.05); }
    [data-testid="stExpander"] summary p { font-size:1rem !important; font-weight:750 !important; color:#0b3a55 !important; }
    [data-testid="stAlert"] { border-radius:14px; font-size:.98rem; box-shadow:0 4px 16px rgba(15,42,67,.05); }
    .hero { display:flex; align-items:center; gap:24px; min-height:132px; padding:20px 28px; border-radius:22px; background:linear-gradient(118deg,#06283d 0%,#075985 58%,#0e7490 100%); color:white; margin-bottom:14px; box-shadow:0 18px 42px rgba(8,47,73,.23); border:1px solid rgba(255,255,255,.12); }
    .hero-copy { flex:1; min-width:0; text-align:center; }
    .hero h1 { margin:3px 0 7px; font-size:2.5rem; line-height:1.05; letter-spacing:-.04em; font-weight:850; color:white; }
    .hero p { margin:0 auto; max-width:780px; color:#e4f7ff; font-size:1.08rem; font-weight:500; line-height:1.45; }
    .hero-kicker { color:#fbbf24; font-size:.88rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; }
    .hero-logo-card { display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,.98); border-radius:15px; padding:10px 13px; min-height:86px; box-shadow:0 8px 22px rgba(0,0,0,.18); }
    .hero-logo-armoiries { width:72px; height:82px; object-fit:contain; }
    .hero-partners { gap:12px; }
    .hero-logo-ade { width:108px; height:66px; object-fit:contain; padding-right:12px; border-right:1px solid #d8e5ee; }
    .hero-logo-sn { width:158px; height:72px; object-fit:contain; }
    .status-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:0 0 17px; }
    .status-chip { background:rgba(255,255,255,.88); border:1px solid var(--line); border-radius:12px; padding:10px 14px; color:#27485b; font-size:.92rem; font-weight:650; text-align:center; box-shadow:0 5px 16px rgba(15,42,67,.04); }
    .status-chip strong { color:#075985; }
    .demo { background:#fff7ed; border:1px solid #fdba74; color:#9a3412; padding:13px 16px; border-radius:13px; margin-bottom:14px; font-size:1rem; }
    .decision { border:1px solid #fed7aa; border-left:6px solid #d97706; background:linear-gradient(135deg,#fffaf0,#fff7ed); padding:18px 18px; border-radius:15px; box-shadow:0 8px 22px rgba(217,119,6,.10); margin-bottom:.85rem; font-size:1.02rem; line-height:1.55; }
    .decision strong { display:block; color:#7c2d12; font-size:1.45rem; line-height:1.2; margin-bottom:4px; }
    .map-note { color:#4c6475; font-size:.94rem; margin:-.2rem 0 .65rem; font-weight:550; }
    .filters-title { color:#06496c; font-weight:850; font-size:1.22rem; margin:.2rem 0 .2rem; }
    .filters-subtitle { color:#587183; font-size:.88rem; line-height:1.4; margin-bottom:1rem; }
    .section-title { display:flex; align-items:center; gap:11px; margin:1.2rem 0 .75rem; color:#082f49; font-size:1.28rem; font-weight:850; letter-spacing:-.015em; }
    .section-title span { display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; flex:0 0 34px; border-radius:10px; background:linear-gradient(135deg,#075985,#0e7490); color:white; font-size:.82rem; box-shadow:0 6px 14px rgba(7,89,133,.2); }
    .section-title small { display:block; color:#607789; font-size:.84rem; font-weight:550; letter-spacing:0; margin-top:2px; }
    .app-footer { margin:2rem 0 0; padding:1.35rem 1.5rem 1.15rem; border-radius:18px; background:linear-gradient(135deg,#06283d,#075985); color:#eaf8ff; box-shadow:0 14px 34px rgba(8,47,73,.18); }
    .app-footer h3 { margin:0 0 .75rem !important; color:white !important; font-size:1.15rem !important; }
    .footer-grid { display:grid; grid-template-columns:1.45fr 1fr; gap:1.6rem; }
    .footer-label { color:#fbbf24; font-size:.8rem; font-weight:850; letter-spacing:.07em; text-transform:uppercase; margin-bottom:.35rem; }
    .footer-list { margin:0; padding-left:1.05rem; color:#eaf8ff; }
    .footer-list li { margin:.18rem 0; font-size:.88rem !important; line-height:1.4 !important; }
    .app-footer a { color:#b9efff; text-decoration:none; font-weight:700; }
    .app-footer a:hover { color:white; text-decoration:underline; }
    .tech-tags { display:flex; flex-wrap:wrap; gap:.42rem; margin-top:.35rem; }
    .tech-tag { display:inline-flex; padding:.35rem .62rem; border:1px solid rgba(255,255,255,.24); border-radius:999px; background:rgba(255,255,255,.1); color:white; font-size:.8rem; font-weight:700; }
    .footer-note { margin-top:1rem; padding-top:.75rem; border-top:1px solid rgba(255,255,255,.18); color:#ccebf5; font-size:.8rem; text-align:center; }
    @media (max-width:1000px) { .hero-logo-ade { width:82px; } .hero-logo-sn { width:118px; } .hero { gap:12px; padding:18px; } .hero h1 { font-size:2.1rem; } .status-row { grid-template-columns:1fr; } }
    @media (max-width:760px) { .footer-grid { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def charger_carte(chemin: str, version_carte: str) -> dict:
    # La version est incluse dans la clé de cache afin qu'un nouveau GeoJSON
    # remplace immédiatement l'ancienne carte conservée par Streamlit.
    return charger_geojson(Path(chemin))


@st.cache_data
def charger_indicateurs(provinces: tuple[str, ...]) -> tuple[pd.DataFrame, bool]:
    if DONNEES_REELLES.exists():
        cadre = pd.read_csv(DONNEES_REELLES)
        cadre["type_donnee"] = "Observé"
        cadre["annee_indicateurs"] = cadre["annee_scolaire"].astype(str)
        if PREVISIONS_FUTURES.exists():
            previsions = pd.read_csv(PREVISIONS_FUTURES)
            derniere_observation = cadre[
                cadre["annee_scolaire"].astype(str) == "2024-2025"
            ].copy()
            projections = []
            for annee_cible, groupe in previsions.groupby("annee_cible", sort=True):
                projection = derniere_observation.copy()
                index_province = groupe.set_index("province")
                projection["score_risque"] = projection["province"].map(
                    index_province["score_prevu"]
                )
                projection["variation_prevue"] = projection["province"].map(
                    index_province["variation_prevue"]
                )
                projection["annee_scolaire"] = str(annee_cible)
                projection["annee_indicateurs"] = "2024-2025"
                projection["type_donnee"] = "Prévision"
                projection["horizon_ans"] = int(groupe["horizon_ans"].iloc[0])
                projection["mae_test"] = float(groupe["mae_test"].iloc[0])
                projection["fiabilite"] = max(
                    0.0, float(groupe["correlation_rangs_test"].iloc[0])
                )
                projections.append(projection)
            if projections:
                cadre = pd.concat([cadre, *projections], ignore_index=True)
        return cadre, False
    return generer_donnees_demo(list(provinces)), True


@st.cache_data
def charger_priorites() -> pd.DataFrame:
    if PRIORITES_DECIDEUR.exists():
        return pd.read_csv(PRIORITES_DECIDEUR)
    return pd.DataFrame()


@st.cache_data
def charger_contexte_esu() -> pd.DataFrame:
    if CONTEXTE_ESU.exists():
        return pd.read_csv(CONTEXTE_ESU)
    return pd.DataFrame()


version_historique = f"{CARTE_HISTORIQUE.stat().st_mtime_ns}-{CARTE_HISTORIQUE.stat().st_size}"
version_2025 = f"{CARTE_2025.stat().st_mtime_ns}-{CARTE_2025.stat().st_size}"
geojson_historique = charger_carte(str(CARTE_HISTORIQUE), version_historique)
geojson_2025 = charger_carte(str(CARTE_2025), version_2025)
provinces_historiques = provinces_geojson(geojson_historique)
provinces_2025 = provinces_geojson(geojson_2025)
referentiel_historique = charger_referentiel_provinces_historiques(
    REFERENTIEL_HISTORIQUE
)
hierarchie_historique = construire_hierarchie_par_champ(
    referentiel_historique, provinces_historiques, "region_historique"
)
hierarchie_2025 = {
    feature["properties"]["shapeName"]: feature["properties"]["region_2025"]
    for feature in geojson_2025["features"]
}
donnees_source, mode_demo = charger_indicateurs(tuple(provinces_historiques))
priorites_decideur = charger_priorites()
contexte_esu = charger_contexte_esu()
if "type_donnee" not in donnees_source:
    donnees_source["type_donnee"] = "Démonstration" if mode_demo else "Observé"
if "annee_indicateurs" not in donnees_source:
    donnees_source["annee_indicateurs"] = donnees_source["annee_scolaire"].astype(str)
erreurs = valider_donnees(donnees_source, provinces_historiques)

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-logo-card"><img class="hero-logo-armoiries" src="{image_data_uri(ARMOIRIES)}" alt="Armoiries du Burkina Faso"></div>
      <div class="hero-copy">
        <div class="hero-kicker">Data Challenge Burkina · Édition Éducation 2026 · Défi 1</div>
        <h1>SCO-RISK Burkina</h1>
        <p>Carte d’alerte et aide à la décision pour anticiper le risque de décrochage scolaire au primaire</p>
      </div>
      <div class="hero-logo-card hero-partners">
        <img class="hero-logo-ade" src="{image_data_uri(LOGO_ADE)}" alt="Africa Data Entry">
        <img class="hero-logo-sn" src="{image_data_uri(LOGO_SN)}" alt="Semaine du Numérique">
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="status-row">
      <div class="status-chip"><strong>8 années</strong> scolaires observées</div>
      <div class="status-chip"><strong>45 provinces</strong> dans l'historique</div>
      <div class="status-chip"><strong>2 années</strong> de projection évaluée</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if mode_demo:
    st.markdown(
        "<div class='demo'><strong>Mode démonstration.</strong> Les valeurs affichées sont entièrement fictives. "
        "L’interface basculera automatiquement vers les indicateurs réels lorsque le fichier nettoyé sera produit.</div>",
        unsafe_allow_html=True,
    )

if erreurs:
    st.error("Le fichier d'indicateurs ne respecte pas le contrat attendu.")
    for erreur in erreurs:
        st.write("-", erreur)
    st.stop()

observations_source = donnees_source[donnees_source["type_donnee"] != "Prévision"].copy()
donnees_historiques = preparer_jointure(observations_source, provinces_historiques)
donnees_historiques["niveau_alerte"] = donnees_historiques["score_risque"].map(categorie_risque)
donnees_historiques["region_affichage"] = donnees_historiques["province_geo"].map(
    hierarchie_historique
)
donnees_historiques["province_source"] = donnees_historiques["province"]
donnees_historiques["statut_statistique"] = "Observation provinciale"
donnees_historiques["referentiel_geo"] = "13 régions / 45 provinces historiques"

projection_source = donnees_source[donnees_source["type_donnee"] == "Prévision"].copy()
if projection_source.empty:
    donnees_projection = pd.DataFrame()
else:
    donnees_projection = projeter_donnees_sur_carte(projection_source, geojson_2025)
    donnees_projection["niveau_alerte"] = donnees_projection["score_risque"].map(categorie_risque)
    donnees_projection["region_affichage"] = donnees_projection["region_2025"]
    donnees_projection["referentiel_geo"] = "17 régions / 47 provinces actuelles"

donnees = pd.concat(
    [donnees_historiques, donnees_projection], ignore_index=True, sort=False
)
annees = sorted(donnees["annee_scolaire"].astype(str).unique())
annees_observees = [
    valeur
    for valeur in annees
    if not (donnees.loc[donnees["annee_scolaire"].astype(str) == valeur, "type_donnee"] == "Prévision").all()
]
annee_defaut = "2024-2025" if "2024-2025" in annees else annees[-1]
st.session_state.setdefault("filtre_annee", annee_defaut)
st.session_state.setdefault("filtre_region", "Toutes les régions")
st.session_state.setdefault("filtre_seuil", 55)

with st.sidebar:
    st.markdown(
        "<div class='filters-title'>Explorer le territoire</div>"
        "<div class='filters-subtitle'>Choisissez une période, puis une région et une province pour actualiser toute l'analyse.</div>",
        unsafe_allow_html=True,
    )
    annee = st.selectbox(
        "Année scolaire",
        annees,
        help="Les années 2017-2018 à 2024-2025 sont observées. 2025-2026 et 2026-2027 sont des projections.",
        key="filtre_annee",
    )
vue_nouveau_decoupage = annee in {"2025-2026", "2026-2027"}
colonne_region = "region_affichage"
libelle_referentiel = (
    "Projection sur le découpage actuel : 17 régions et 47 provinces"
    if vue_nouveau_decoupage
    else "Découpage statistique historique : 13 régions et 45 provinces"
)
geojson = geojson_2025 if vue_nouveau_decoupage else geojson_historique
hierarchie = hierarchie_2025 if vue_nouveau_decoupage else hierarchie_historique
regions = sorted(
    donnees.loc[
        donnees["annee_scolaire"].astype(str) == annee, colonne_region
    ].dropna().unique()
)
if st.session_state.get("filtre_region") not in ["Toutes les régions"] + regions:
    st.session_state["filtre_region"] = "Toutes les régions"
with st.sidebar:
    region_choisie = st.selectbox(
        "Région à examiner", ["Toutes les régions"] + regions,
        key="filtre_region",
    )
    emplacement_province = st.empty()
    emplacement_seuil = st.empty()

if annees_observees:
    st.caption(
        f"Historique analysé : **{annees_observees[0]} à {annees_observees[-1]}** "
        f"({len(annees_observees)} années scolaires observées). "
        "Les projections 2025-2026 et 2026-2027 sont disponibles séparément dans le sélecteur."
    )

vue = donnees[donnees["annee_scolaire"].astype(str) == annee].copy()
if annee == "2024-2025" and not priorites_decideur.empty:
    colonnes_interpretation = [
        "province",
        "rang_national",
        "priorite_decision",
        "tendance_score_3_ans",
        "tendance_recente",
        "annees_risque_eleve",
        "facteur_dominant",
        "recommandation",
    ]
    vue = vue.merge(
        priorites_decideur[colonnes_interpretation], on="province", how="left"
    )
vue = vue.dropna(subset=["province_geo"])
vue = vue.sort_values("score_risque", ascending=False)
if region_choisie == "Toutes les régions":
    vue_focus = vue.copy()
else:
    vue_focus = vue[vue[colonne_region] == region_choisie].copy()

if vue_focus.empty:
    st.error("Aucune province cartographiée pour cette région.")
    st.stop()

options_provinces = vue_focus["province"].tolist()
st.session_state.setdefault("filtre_province", options_provinces[0])
if st.session_state.get("filtre_province") not in options_provinces:
    st.session_state["filtre_province"] = options_provinces[0]
with emplacement_province.container():
    province_choisie = st.selectbox(
        "Province à examiner",
        options_provinces,
        help="La liste est automatiquement limitée à la région sélectionnée.",
        key="filtre_province",
    )
with emplacement_seuil.container():
    seuil = st.slider(
        "Seuil d’affichage des provinces prioritaires",
        40,
        85,
        step=5,
        key="filtre_seuil",
        help="Les provinces dont le score est supérieur ou égal à ce seuil sont comptées comme prioritaires.",
    )
with st.sidebar:
    st.divider()
    st.button(
        "↺ Réinitialiser les filtres",
        use_container_width=True,
        on_click=reinitialiser_filtres,
    )

st.caption(
    f"{libelle_referentiel}."
)
if vue_nouveau_decoupage:
    st.caption(
        "La projection est reportée sur les limites administratives 2025. "
        "Djelgodji et Karo-Peli héritent de la série historique du Soum ; "
        "Dyamongou et Gobnangou de celle de la Tapoa. Aucune valeur n'est inventée."
    )
else:
    st.caption(
        "Les observations 2017-2018 à 2024-2025 restent dans le découpage "
        "des sources DGESS. Elles ne sont pas mélangées au référentiel 2025."
    )

est_prevision = bool((vue_focus["type_donnee"] == "Prévision").all())
if est_prevision:
    st.warning(
        f"**Projection {annee}.** La couleur représente un score prévu par le modèle "
        f"à horizon {int(vue_focus['horizon_ans'].iloc[0])} an(s). "
        "Les taux affichés comme facteurs sont les derniers taux observés (2024-2025), "
        "pas des taux futurs mesurés."
    )

vue_focus_analyse = (
    vue_focus.drop_duplicates(subset=["province_source"])
    if vue_nouveau_decoupage
    else vue_focus
)
nb_prioritaires = int((vue_focus["score_risque"] >= seuil).sum())
score_median = float(vue_focus_analyse["score_risque"].median())
province_max = str(vue_focus.iloc[0]["province"])
score_max = float(vue_focus.iloc[0]["score_risque"])
fiabilite = float(vue_focus_analyse["fiabilite"].mean()) if vue_focus_analyse["fiabilite"].notna().any() else float("nan")

st.markdown(
    "<div class='section-title'><span>01</span><div>Vue d’ensemble<small>Les principaux signaux du territoire sélectionné</small></div></div>",
    unsafe_allow_html=True,
)
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Provinces prioritaires",
    nb_prioritaires,
    f"sur {len(vue_focus)} provinces affichées – seuil ≥ {seuil}/100",
)
c2.metric("Risque médian", f"{score_median:.1f}/100")
c3.metric("Risque le plus élevé", f"{score_max:.1f}/100", province_max)
c4.metric(
    "Corrélation de rang (test)" if est_prevision else "Fiabilité moyenne",
    "À valider" if pd.isna(fiabilite) else f"{fiabilite:.0%}",
)

if region_choisie != "Toutes les régions":
    abandon_moyen = float(vue_focus_analyse["taux_abandon"].mean())
    redoublement_moyen = float(vue_focus_analyse["taux_redoublement"].mean())
    score_median = float(vue_focus_analyse["score_risque"].median())
    st.info(
        f"**Synthèse – {region_choisie} :** {len(vue_focus)} provinces · "
        f"score médian {score_median:.1f}/100 · "
        f"abandon moyen {abandon_moyen:.1f} % · "
        f"redoublement moyen {redoublement_moyen:.1f} %."
    )
    st.caption(
        "Ces moyennes provinciales sont descriptives et non pondérées ; elles ne "
        "remplacent pas des taux régionaux officiels recalculés sur les effectifs."
    )
    if vue_nouveau_decoupage and len(vue_focus_analyse) != len(vue_focus):
        st.caption(
            f"Agrégats calculés sur {len(vue_focus_analyse)} série(s) source(s) "
            "indépendante(s), sans double comptage des provinces issues d'une scission."
        )

carte = go.Figure()
carte.add_trace(
    go.Choroplethmap(
        geojson=geojson,
        locations=vue["province_geo"],
        featureidkey="properties.shapeName",
        z=[0] * len(vue),
        colorscale=[[0, "#e2e8f0"], [1, "#e2e8f0"]],
        showscale=False,
        marker={"opacity": 0.55, "line": {"color": "#94a3b8", "width": 0.7}},
        customdata=vue[["province", colonne_region]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
        name="Contexte national",
    )
)
carte.add_trace(
    go.Choroplethmap(
        geojson=geojson,
        locations=vue_focus["province_geo"],
        featureidkey="properties.shapeName",
        z=vue_focus["score_risque"],
        zmin=0,
        zmax=100,
        colorscale=[
            [0.00, "#0e7490"],
            [0.35, "#22c55e"],
            [0.55, "#facc15"],
            [0.75, "#f97316"],
            [1.00, "#b91c1c"],
        ],
        colorbar={
            "title": "Risque",
            "ticksuffix": "/100",
            "len": 0.62,
            "thickness": 14,
            "x": 0.965,
            "y": 0.5,
        },
        marker={"opacity": 0.9, "line": {"color": "#334155", "width": 1}},
        customdata=vue_focus[
            [
                "province",
                colonne_region,
                "niveau_alerte",
                "taux_abandon",
                "taux_redoublement",
                "taux_achevement",
            ]
        ],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>Région : %{customdata[1]}"
            "<br>Score : %{z:.1f}/100<br>Alerte : %{customdata[2]}"
            "<br>Abandon : %{customdata[3]:.1f}%"
            "<br>Redoublement : %{customdata[4]:.1f}%"
            "<br>Achèvement régional : %{customdata[5]:.1f}%<extra></extra>"
        ),
        name="Provinces sélectionnées",
    )
)
rattachement_carte = hierarchie
contours_regions = construire_contours_regions(geojson, rattachement_carte)
for nom_region, (longitudes, latitudes) in contours_regions.items():
    selectionnee = region_choisie == nom_region
    carte.add_trace(
        go.Scattermap(
            lon=longitudes,
            lat=latitudes,
            mode="lines",
            line={
                "color": "#f59e0b" if selectionnee else "#0f172a",
                "width": 4 if selectionnee else 2,
            },
            hoverinfo="skip",
            showlegend=False,
            name=f"Limite régionale {nom_region}",
        )
    )
province_selectionnee = vue_focus[vue_focus["province"] == province_choisie]
carte.add_trace(
    go.Choroplethmap(
        geojson=geojson,
        locations=province_selectionnee["province_geo"],
        featureidkey="properties.shapeName",
        z=[1] * len(province_selectionnee),
        colorscale=[[0, "rgba(255,255,255,0.08)"], [1, "rgba(255,255,255,0.08)"]],
        showscale=False,
        marker={"opacity": 1, "line": {"color": "#ffffff", "width": 4}},
        hoverinfo="skip",
        name="Province examinée",
    )
)
titre_carte = (
    f"Carte d’alerte provinciale – {annee}"
    if region_choisie == "Toutes les régions"
    else f"Région {region_choisie} – provinces rattachées – {annee}"
)
if region_choisie == "Toutes les régions":
    centre_carte = {"lat": 12.35, "lon": -1.60}
    zoom_carte = 5.95
else:
    centre_carte, zoom_carte = calculer_cadrage_geojson(
        geojson, vue_focus["province_geo"].tolist()
    )
carte.update_layout(
    height=720,
    margin=dict(l=8, r=62, t=62, b=8),
    map={
        "style": "white-bg",
        "center": centre_carte,
        "zoom": zoom_carte,
        "domain": {"x": [0, 0.91], "y": [0, 1]},
    },
    title=titre_carte,
    showlegend=False,
    dragmode=False,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font={"family": "Segoe UI, Arial, sans-serif", "color": "#102a43", "size": 14},
    title_font={"size": 21, "color": "#082f49", "family": "Segoe UI Semibold, Arial"},
)

st.markdown(
    "<div class='section-title'><span>02</span><div>Carte d’alerte territoriale<small>Sélectionnez une région puis une province pour approfondir l’analyse</small></div></div>",
    unsafe_allow_html=True,
)
gauche, droite = st.columns([2.05, 1], gap="large")
with gauche:
    st.markdown(
        "<div class='map-note'>Le cadrage s’adapte automatiquement à la région choisie. Le zoom manuel reste bloqué.</div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        carte,
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "showTips": False,
        },
    )
    if region_choisie != "Toutes les régions":
        provinces_region = ", ".join(sorted(vue_focus["province"].astype(str)))
        st.caption(f"Provinces mises en évidence : {provinces_region}.")
        if vue_nouveau_decoupage and region_choisie in {"Soum", "Tapoa"}:
            st.warning(
                "Les limites des deux provinces sont bien distinctes sur la carte, "
                "mais leurs scores proviennent encore d'une même série historique source."
            )

with droite:
    st.markdown("### Détail du territoire")
    ligne = vue_focus[vue_focus["province"] == province_choisie].iloc[0]
    st.markdown(
        f"<div class='decision'><strong>{province_choisie}</strong><br>"
        f"Alerte {ligne['niveau_alerte'].lower()} – score {ligne['score_risque']:.1f}/100</div>",
        unsafe_allow_html=True,
    )
    if vue_nouveau_decoupage and "Valeur héritée" in str(ligne["statut_statistique"]):
        st.warning(
            f"**Projection non désagrégée :** {province_choisie} reprend la "
            f"projection de l'ancienne province {ligne['province_source']}. "
            "Elle ne peut pas encore être comparée séparément à l'autre province issue de la scission."
        )
    if annee == "2024-2025" and pd.notna(ligne.get("priorite_decision")):
        st.write(f"**Décision :** {ligne['priorite_decision']}")
        st.write(
            f"**Tendance récente :** {ligne['tendance_recente']} "
            f"({float(ligne['tendance_score_3_ans']):+.1f} point(s)/an)"
        )
        st.write(f"**Contribution dominante :** {ligne['facteur_dominant']}")
        st.caption(
            "La contribution dominante aide à lire le score ; elle ne démontre pas une cause."
        )
    if est_prevision:
        variation = float(ligne.get("variation_prevue", 0))
        st.caption(
            f"Prévision {annee} · variation estimée : {variation:+.1f} point(s) · "
            f"MAE de test : {float(ligne.get('mae_test', float('nan'))):.1f} · "
            "facteurs observés en 2024-2025."
        )
    facteurs = pd.DataFrame(
        {
            "Indicateur": ["Abandon", "Redoublement", "Non-achèvement régional"],
            "Valeur": [
                float(ligne["taux_abandon"]),
                float(ligne["taux_redoublement"]),
                100 - float(ligne["taux_achevement"]),
            ],
        }
    )
    barres = px.bar(
        facteurs,
        x="Valeur",
        y="Indicateur",
        orientation="h",
        color="Valeur",
        color_continuous_scale=["#bae6fd", "#f97316", "#b91c1c"],
        labels={"Valeur": "Taux (%)"},
    )
    barres.update_traces(marker_line_color="rgba(255,255,255,.9)", marker_line_width=1.2)
    barres.update_layout(
        height=280,
        margin=dict(l=0, r=8, t=22, b=8),
        coloraxis_showscale=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Segoe UI, Arial", "size": 13, "color": "#233f52"},
        xaxis={"gridcolor": "#e7eef3", "title_font": {"size": 13}},
        yaxis={"title": None, "tickfont": {"size": 13}},
    )
    st.plotly_chart(barres, width="stretch", config={"displayModeBar": False})
    st.write("**Actions suggérées**")
    if annee == "2024-2025" and pd.notna(ligne.get("recommandation")):
        st.write("-", ligne["recommandation"])
    else:
        for action in recommandations(ligne):
            st.write("-", action)

if not contexte_esu.empty:
    st.markdown(
        "<div class='section-title'><span>ESU</span><div>Contexte sécuritaire et urgence éducative"
        "<small>Éclairage complémentaire au 28 février 2026, séparé du score SCO-RISK</small></div></div>",
        unsafe_allow_html=True,
    )
    contexte_focus = (
        contexte_esu
        if region_choisie == "Toutes les régions"
        else contexte_esu[contexte_esu["region_2025"] == region_choisie]
    )

    if region_choisie == "Toutes les régions":
        region_pression = contexte_esu.sort_values(
            "indice_pression_esu", ascending=False
        ).iloc[0]
        e1, e2, e3, e4 = st.columns(4)
        e1.metric(
            "Élèves déplacés internes – primaire",
            f"{int(contexte_esu['edi_primaire_total'].sum()):,}".replace(",", " "),
            "effectif national déclaré",
        )
        e2.metric(
            "Structures primaires délocalisées",
            f"{int(contexte_esu['structures_delocalisees_primaire'].sum()):,}".replace(",", " "),
        )
        e3.metric(
            "Structures primaires rouvertes",
            f"{int(contexte_esu['structures_rouvertes_primaire'].sum()):,}".replace(",", " "),
            "indicateur de réponse, pas de risque",
        )
        e4.metric(
            "Pression contextuelle la plus élevée",
            str(region_pression["region_2025"]),
            f"indice descriptif {float(region_pression['indice_pression_esu']):.1f}/100",
        )
    elif not contexte_focus.empty:
        contexte_ligne = contexte_focus.iloc[0]
        e1, e2, e3, e4 = st.columns(4)
        e1.metric(
            "EDI au primaire",
            f"{int(contexte_ligne['edi_primaire_total']):,}".replace(",", " "),
        )
        e2.metric(
            "Structures délocalisées",
            int(contexte_ligne["structures_delocalisees_primaire"]),
        )
        e3.metric(
            "Structures rouvertes",
            int(contexte_ligne["structures_rouvertes_primaire"]),
            "capacité de réponse",
        )
        e4.metric(
            "Indice de pression ESU",
            f"{float(contexte_ligne['indice_pression_esu']):.1f}/100",
            str(contexte_ligne["niveau_pression_esu"]),
        )
        if annee == "2025-2026" and bool(contexte_ligne["double_alerte"]):
            st.warning(
                f"**Double signal à vérifier – {region_choisie}.** Le risque scolaire "
                "projeté et la pression ESU dépassent chacun 55/100. "
                f"{contexte_ligne['action_proposee']}"
            )
        else:
            st.info(f"**Piste d'action :** {contexte_ligne['action_proposee']}")

    st.caption(
        "Source : MENAPLN/DGESS, Rapport statistique mensuel ESU, février 2026. "
        "Les valeurs sont des effectifs et non des taux. L'indice de pression (60 % rang des EDI "
        "+ 40 % rang des structures délocalisées) sert au ciblage descriptif : il n'entre pas "
        "dans le score SCO-RISK et ne démontre aucune causalité avec le décrochage. "
        "Toute décision exige une validation locale avec des informations actualisées."
    )

st.markdown(
    "<div class='section-title'><span>03</span><div>Évolution historique du risque<small>Huit années scolaires pour distinguer tendance et signal ponctuel</small></div></div>",
    unsafe_allow_html=True,
)
source_selectionnee = str(ligne.get("province_source", province_choisie))
historique = donnees[
    (donnees["province_source"] == source_selectionnee)
    & (
        (donnees["type_donnee"] != "Prévision")
        | (donnees["province"] == province_choisie)
    )
].sort_values("annee_scolaire")
historique_province = historique[["annee_scolaire", "score_risque"]].copy()
historique_province["Série"] = (
    f"{province_choisie} (historique : {source_selectionnee})"
    if province_choisie != source_selectionnee
    else province_choisie
)
series = [historique_province]
if region_choisie != "Toutes les régions" and not vue_nouveau_decoupage:
    historique_region = (
        donnees[donnees[colonne_region] == region_choisie]
        .groupby("annee_scolaire", as_index=False)["score_risque"]
        .mean()
    )
    historique_region["Série"] = f"Moyenne région {region_choisie}"
    series.append(historique_region)
historique_courbe = pd.concat(series, ignore_index=True)
courbe = px.line(
    historique_courbe,
    x="annee_scolaire",
    y="score_risque",
    color="Série",
    markers=True,
    range_y=(0, 100),
    labels={"annee_scolaire": "Année scolaire", "score_risque": "Score de risque"},
)
courbe.add_hline(y=seuil, line_dash="dash", line_color="#d97706", annotation_text="Seuil prioritaire")
courbe.update_traces(line={"width": 3}, marker={"size": 8, "line": {"width": 1.5, "color": "white"}})
courbe.update_layout(
    height=370,
    margin=dict(l=12, r=20, t=30, b=12),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font={"family": "Segoe UI, Arial", "size": 13, "color": "#233f52"},
    legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
    xaxis={"gridcolor": "#edf2f6", "title_font": {"size": 13}},
    yaxis={"gridcolor": "#e4edf3", "title_font": {"size": 13}},
)
st.plotly_chart(courbe, width="stretch", config={"displayModeBar": False})

historique_table = historique[
    historique["type_donnee"] != "Prévision"
][
    [
        "annee_scolaire",
        "score_risque",
        "taux_abandon",
        "taux_redoublement",
        "taux_achevement",
    ]
].rename(
    columns={
        "annee_scolaire": "Année scolaire",
        "score_risque": "Score",
        "taux_abandon": "Abandon (%)",
        "taux_redoublement": "Redoublement (%)",
        "taux_achevement": "Achèvement régional (%)",
    }
)
with st.expander(f"Voir les 8 années observées pour {province_choisie}"):
    st.dataframe(historique_table, hide_index=True, width="stretch")

st.markdown(
    f"<div class='section-title'><span>04</span><div>Provinces à prioriser<small>Classement détaillé pour l’année scolaire {annee}</small></div></div>",
    unsafe_allow_html=True,
)
colonnes_tableau = [
    "province",
    "score_risque",
    "niveau_alerte",
]
if annee == "2024-2025" and "priorite_decision" in vue_focus:
    colonnes_tableau += ["priorite_decision", "tendance_recente", "facteur_dominant"]
colonnes_tableau += [
    "taux_abandon",
    "taux_redoublement",
    "taux_achevement",
    "fiabilite",
]
if vue_nouveau_decoupage:
    colonnes_tableau += ["province_source", "statut_statistique"]
tableau = vue_focus[colonnes_tableau].rename(
    columns={
        "province": "Province",
        "score_risque": "Score",
        "niveau_alerte": "Alerte",
        "priorite_decision": "Décision",
        "tendance_recente": "Tendance récente",
        "facteur_dominant": "Contribution dominante",
        "taux_abandon": "Abandon (%)",
        "taux_redoublement": "Redoublement (%)",
        "taux_achevement": "Achèvement régional (%)",
        "fiabilite": "Fiabilité",
        "province_source": "Série historique source",
        "statut_statistique": "Statut de la projection",
    }
)
if vue_nouveau_decoupage:
    colonnes_affichees = [
        "Province",
        "Score",
        "Alerte",
        "Fiabilité",
        "Série historique source",
        "Statut de la projection",
    ]
else:
    colonnes_affichees = [
        "Province",
        "Score",
        "Alerte",
        "Décision",
        "Tendance récente",
        "Abandon (%)",
    ]
st.caption(
    "Le classement conserve les colonnes essentielles à l'écran. "
    "Les autres indicateurs sont visibles dans le détail du territoire."
)
st.dataframe(
    tableau,
    hide_index=True,
    width="stretch",
    height=410,
    column_order=colonnes_affichees,
    column_config={
        "Province": st.column_config.TextColumn(width="medium"),
        "Score": st.column_config.NumberColumn(format="%.1f", width="small"),
        "Alerte": st.column_config.TextColumn(width="small"),
        "Décision": st.column_config.TextColumn(width="medium"),
        "Tendance récente": st.column_config.TextColumn(width="medium"),
        "Contribution dominante": st.column_config.TextColumn(width="medium"),
        "Abandon (%)": st.column_config.NumberColumn(format="%.1f", width="small"),
        "Fiabilité": st.column_config.NumberColumn(format="%.0f%%", width="small"),
        "Série historique source": st.column_config.TextColumn(width="medium"),
        "Statut de la projection": st.column_config.TextColumn(width="large"),
    },
)

with st.expander("Méthode, limites et reproductibilité"):
    st.markdown(
        """
        - **Unité de décision :** province et année scolaire.
        - **Score transparent :** 50 % abandon provincial, 30 % redoublement provincial et 20 % non-achèvement régional. La stabilité a été testée avec deux autres pondérations.
        - **Évaluation temporelle :** apprentissage jusqu'à 2023-2024 et test final sur 2024-2025. Le modèle Ridge obtient une MAE de 9,55 contre 13,97 pour la référence naïve, et retrouve 6 provinces sur 10 du groupe prioritaire.
        - **Projections 2025-2026 et 2026-2027 :** deux modèles directs Ridge, à horizons d'un et deux ans, sont testés sur la cible 2024-2025 puis réentraînés sur toutes les transitions disponibles. Les prévisions servent à prioriser une revue humaine, jamais à décider automatiquement.
        - **Observations :** les années 2017-2018 à 2024-2025 utilisent les 13 régions et 45 provinces présentes dans les sources DGESS.
        - **Projections futures :** elles utilisent la carte actuelle à 17 régions et 47 provinces. Les scissions Soum et Tapoa sont visibles, mais leurs valeurs restent héritées des 45 séries sources et sont dédupliquées dans les agrégats.
        - **Limite :** les données provinciales d'abandon et de redoublement proviennent des annuaires, tandis que l'achèvement n'est disponible qu'au niveau régional.
        """
    )
    st.caption(
        "Sources cartographiques : limites historiques cohérentes avec les annuaires DGESS ; "
        "COD-AB août 2025 pour les projections 2025-2026 et 2026-2027."
    )

st.markdown(
    """
    <footer class="app-footer">
      <h3>Sources, technologies et reproductibilité</h3>
      <div class="footer-grid">
        <div>
          <div class="footer-label">Sources des données</div>
          <ul class="footer-list">
            <li><a href="https://www.education.gov.bf/fileadmin/user_upload/storages/annuaire_statistique_du_primaire_2024-2025_vf.pdf" target="_blank">DGESS / MEBAPLN</a> — statistiques et annuaires du primaire 2016-2025.</li>
            <li><a href="https://humanitarian.atlassian.net/wiki/spaces/imtoolbox/pages/2557378679" target="_blank">COD-AB / OCHA</a> — limites administratives du Burkina Faso, version d'août 2025.</li>
            <li>Data Challenge Burkina 2026 — document du challenge, Data Pack et référentiels fournis aux équipes.</li>
          </ul>
        </div>
        <div>
          <div class="footer-label">Technologies utilisées</div>
          <div class="tech-tags">
            <a class="tech-tag" href="https://www.python.org/" target="_blank">Python</a>
            <a class="tech-tag" href="https://docs.streamlit.io/" target="_blank">Streamlit</a>
            <a class="tech-tag" href="https://pandas.pydata.org/docs/" target="_blank">Pandas</a>
            <a class="tech-tag" href="https://numpy.org/doc/" target="_blank">NumPy</a>
            <a class="tech-tag" href="https://plotly.com/python/" target="_blank">Plotly</a>
            <a class="tech-tag" href="https://scikit-learn.org/stable/" target="_blank">scikit-learn</a>
            <span class="tech-tag">GeoJSON</span>
          </div>
        </div>
      </div>
      <div class="footer-note">
        SCO-RISKBurkina • Défi 1 — Décrochage scolaire •
        <a href="https://github.com/kabreaziz60/SCO_RISKBURKINA-DATA-CHALENGE-BURKINA-SN-2026" target="_blank">Code source et méthode sur GitHub</a>
      </div>
    </footer>
    """,
    unsafe_allow_html=True,
)

