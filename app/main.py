import pandas as pd
import streamlit as st
import folium
import geopandas as gpd

from streamlit_folium import st_folium


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Togo Digital Access",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


DATA_PATH = "data/processed/priorites_prefectures.csv"
PREFECTURES_PATH = "data/processed/prefectures_adm2.geojson"


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 0;
        }

        .subtitle {
            font-size: 19px;
            color: #666;
            margin-top: 0;
        }

        .section-title {
            font-size: 28px;
            font-weight: 650;
            margin-top: 20px;
        }

        .conclusion-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f5f7fa;
            border-left: 5px solid #1f77b4;
            margin-bottom: 15px;
        }

        .warning-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #fff8e1;
            border-left: 5px solid #f0ad4e;
            margin-top: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def charger_donnees():
    """Charge les indicateurs territoriaux."""
    df = pd.read_csv(DATA_PATH)

    # Sécurité : convertir les colonnes numériques
    colonnes_numeriques = [
        "population_worldpop",
        "superficie_km2",
        "densite_worldpop_moyenne",
        "densite_calculee",
        "agents_mobile_money",
        "agents_mm_pour_10000_hab",
        "agences_moov",
        "agences_togocom",
        "agences_telecom",
        "agences_canal",
        "agences_telecom_total",
        "datacenters",
        "antennes_opencellid",
        "antennes_pour_10000_hab",
        "score_population",
        "score_deficit_mobile_money",
        "score_deficit_antennes",
        "score_priorite",
        "rang_priorite",
    ]

    for colonne in colonnes_numeriques:
        if colonne in df.columns:
            df[colonne] = pd.to_numeric(
                df[colonne],
                errors="coerce"
            ).fillna(0)

    return df


@st.cache_data
def charger_prefectures():
    """Charge les limites administratives des préfectures."""
    gdf = gpd.read_file(PREFECTURES_PATH)

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    # Le GeoJSON utilise shapeName comme nom de préfecture
    gdf = gdf.rename(
        columns={"shapeName": "prefecture"}
    )

    return gdf


df = charger_donnees()
prefectures = charger_prefectures()


# ============================================================
# PRÉPARATION DE LA CARTE
# ============================================================

df_carte = prefectures.merge(
    df[
        [
            "prefecture",
            "population_worldpop",
            "agents_mobile_money",
            "antennes_opencellid",
            "score_priorite",
            "niveau_priorite",
        ]
    ],
    on="prefecture",
    how="left",
)

df_carte["population_worldpop"] = (
    df_carte["population_worldpop"].fillna(0)
)

df_carte["agents_mobile_money"] = (
    df_carte["agents_mobile_money"].fillna(0)
)

df_carte["antennes_opencellid"] = (
    df_carte["antennes_opencellid"].fillna(0)
)

df_carte["score_priorite"] = (
    df_carte["score_priorite"].fillna(0)
)

df_carte["niveau_priorite"] = (
    df_carte["niveau_priorite"]
    .fillna("Non classé")
)


# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="main-title">📡 Togo Digital Access</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Diagnostic territorial de l'accès aux services numériques au Togo"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    Ce tableau de bord analyse la répartition territoriale de la
    population, des agents Mobile Money, des agences télécom et des
    antennes mobiles recensées afin d'identifier les territoires
    nécessitant une attention prioritaire.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Filtres")

niveaux = sorted(
    df["niveau_priorite"]
    .dropna()
    .astype(str)
    .unique()
)

niveaux_selectionnes = st.sidebar.multiselect(
    "Niveau de priorité",
    options=niveaux,
    default=niveaux,
)

df_filtre = df[
    df["niveau_priorite"].astype(str).isin(
        niveaux_selectionnes
    )
].copy()


st.sidebar.markdown("---")

st.sidebar.caption(
    "📌 Les indicateurs de population sont issus de WorldPop 2020."
)

st.sidebar.caption(
    "📌 Les antennes proviennent d'OpenCelliD, une source "
    "collaborative. Elles constituent donc un proxy de "
    "l'infrastructure observée."
)


# ============================================================
# KPI
# ============================================================

population = df_filtre["population_worldpop"].sum()
agents_mm = df_filtre["agents_mobile_money"].sum()
agences = df_filtre["agences_telecom_total"].sum()
antennes = df_filtre["antennes_opencellid"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Population estimée",
        f"{population:,.0f}",
    )

with col2:
    st.metric(
        "💰 Agents Mobile Money",
        f"{agents_mm:,.0f}",
    )

with col3:
    st.metric(
        "🏢 Agences télécom",
        f"{agences:,.0f}",
    )

with col4:
    st.metric(
        "📡 Antennes OpenCelliD",
        f"{antennes:,.0f}",
    )


st.divider()


# ============================================================
# CLASSEMENT DES PRIORITÉS
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Préfectures prioritaires</div>',
    unsafe_allow_html=True,
)

top = (
    df_filtre[
        [
            "rang_priorite",
            "prefecture",
            "population_worldpop",
            "agents_mobile_money",
            "agents_mm_pour_10000_hab",
            "antennes_opencellid",
            "score_priorite",
            "niveau_priorite",
        ]
    ]
    .sort_values("rang_priorite")
    .head(10)
    .copy()
)

top_affichage = top.rename(
    columns={
        "rang_priorite": "Rang",
        "prefecture": "Préfecture",
        "population_worldpop": "Population",
        "agents_mobile_money": "Agents Mobile Money",
        "agents_mm_pour_10000_hab": "Agents / 10 000 hab.",
        "antennes_opencellid": "Antennes recensées",
        "score_priorite": "Score",
        "niveau_priorite": "Niveau",
    }
)

st.dataframe(
    top_affichage,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Population": st.column_config.NumberColumn(
            format="%,.0f"
        ),
        "Agents / 10 000 hab.": st.column_config.NumberColumn(
            format="%.2f"
        ),
        "Score": st.column_config.NumberColumn(
            format="%.3f"
        ),
    },
)


# ============================================================
# GRAPHIQUE
# ============================================================

st.markdown(
    '<div class="section-title">📊 Score de priorité</div>',
    unsafe_allow_html=True,
)

graphique = (
    df_filtre[
        ["prefecture", "score_priorite"]
    ]
    .sort_values("score_priorite", ascending=True)
    .tail(10)
)

st.bar_chart(
    graphique.set_index("prefecture")["score_priorite"],
    horizontal=True,
)


# ============================================================
# CARTE INTERACTIVE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🗺️ Carte de priorité territoriale</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    La carte permet d'identifier visuellement les préfectures
    présentant le plus fort niveau de priorité selon notre score
    territorial.
    """
)


# Création de la carte
m = folium.Map(
    location=[8.6, 1.2],
    zoom_start=7,
    tiles="CartoDB positron",
)


# Fonction de couleur
def couleur_priorite(niveau):
    if niveau == "Forte":
        return "#d73027"
    elif niveau == "Moyenne":
        return "#fc8d59"
    elif niveau == "Faible":
        return "#91cf60"
    return "#cccccc"


# Ajout des préfectures
for _, row in df_carte.iterrows():

    niveau = row["niveau_priorite"]

    population_row = row["population_worldpop"]
    agents_row = row["agents_mobile_money"]
    antennes_row = row["antennes_opencellid"]
    score_row = row["score_priorite"]

    popup_html = f"""
    <div style="width: 260px;">
        <h4>{row['prefecture']}</h4>

        <b>Niveau :</b> {niveau}<br>
        <b>Score de priorité :</b> {score_row:.3f}<br>
        <b>Population :</b> {population_row:,.0f}<br>
        <b>Agents Mobile Money :</b> {agents_row:,.0f}<br>
        <b>Antennes recensées :</b> {antennes_row:,.0f}
    </div>
    """

    folium.GeoJson(
        row["geometry"],
        style_function=lambda feature, niveau=niveau: {
            "fillColor": couleur_priorite(niveau),
            "color": "#555555",
            "weight": 1,
            "fillOpacity": 0.65,
        },
        highlight_function=lambda feature: {
            "weight": 3,
            "fillOpacity": 0.85,
        },
        tooltip=folium.Tooltip(
            f"{row['prefecture']} — {niveau}"
        ),
        popup=folium.Popup(
            popup_html,
            max_width=300,
        ),
    ).add_to(m)


st_folium(
    m,
    width=None,
    height=600,
)


# ============================================================
# LÉGENDE
# ============================================================

st.markdown(
    """
    **Légende :**

    🔴 **Forte priorité** — territoire nécessitant une attention
    prioritaire.

    🟠 **Priorité moyenne** — territoire présentant un besoin
    intermédiaire.

    🟢 **Faible priorité** — territoire relativement mieux doté
    selon les indicateurs utilisés.
    """
)


# ============================================================
# CONCLUSIONS
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🎯 Conclusions et recommandations</div>',
    unsafe_allow_html=True,
)


# Préfecture n°1
top1 = (
    df.sort_values("rang_priorite")
    .iloc[0]
)

nom_top1 = top1["prefecture"]
pop_top1 = top1["population_worldpop"]
mm_top1 = top1["agents_mobile_money"]
mm_ratio_top1 = top1["agents_mm_pour_10000_hab"]
antenne_top1 = top1["antennes_opencellid"]
score_top1 = top1["score_priorite"]


st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>1. Territoires à traiter en priorité</h4>

    <p>
    <b>{nom_top1}</b> ressort comme la préfecture la plus prioritaire
    selon le score construit. Elle combine une population importante
    ({pop_top1:,.0f} habitants estimés), une faible disponibilité
    relative des agents Mobile Money ({mm_ratio_top1:.2f} agents
    pour 10 000 habitants) et aucune antenne OpenCelliD recensée
    dans cette source.
    </p>

    <p>
    Son score de priorité est de <b>{score_top1:.3f}</b>.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# Top 5
top5 = (
    df.sort_values("rang_priorite")
    .head(5)["prefecture"]
    .tolist()
)

top5_text = ", ".join(top5)


st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>2. Plusieurs territoires présentent un besoin significatif</h4>

    <p>
    Les cinq premières préfectures du classement sont :
    <b>{top5_text}</b>.
    </p>

    <p>
    Cela montre que la stratégie de développement numérique ne doit
    pas se limiter aux grands centres urbains. Les territoires
    présentant simultanément une population significative et une
    faible densité de services doivent être considérés dans la
    planification des investissements.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# Mobile Money
pref_mm_faible = (
    df.sort_values("agents_mm_pour_10000_hab")
    .iloc[0]
)

st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>3. Le Mobile Money constitue un levier important</h4>

    <p>
    La préfecture de <b>{pref_mm_faible['prefecture']}</b> présente
    le plus faible ratio d'agents Mobile Money avec environ
    <b>{pref_mm_faible['agents_mm_pour_10000_hab']:.2f}</b> agents
    pour 10 000 habitants.
    </p>

    <p>
    Une extension du réseau d'agents dans les territoires les moins
    bien desservis pourrait améliorer l'accès aux services financiers
    numériques et renforcer l'inclusion numérique.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# Concentration urbaine
st.markdown(
    """
    <div class="conclusion-box">

    <h4>4. Une forte concentration des infrastructures dans les zones urbaines</h4>

    <p>
    Les données montrent une concentration importante des agents
    Mobile Money et des agences télécom dans les principaux pôles
    urbains, notamment autour de <b>Lome Commune</b> et du
    <b>Golfe</b>.
    </p>

    <p>
    Cette concentration peut traduire une meilleure disponibilité
    des services dans les zones urbaines, mais elle met également
    en évidence un potentiel de rattrapage dans plusieurs territoires
    ruraux et périphériques.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# Recommandation stratégique
st.markdown(
    """
    <div class="conclusion-box">

    <h4>5. Recommandation stratégique</h4>

    <p>
    Les investissements futurs devraient prioritairement cibler les
    territoires combinant :
    </p>

    <ul>
        <li>une population importante ;</li>
        <li>une faible densité d'agents Mobile Money ;</li>
        <li>une faible présence d'infrastructures mobiles recensées ;</li>
        <li>et un score territorial de priorité élevé.</li>
    </ul>

    <p>
    Cette approche permettrait de maximiser l'impact territorial des
    investissements plutôt que de renforcer uniquement les zones
    déjà relativement bien équipées.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AVERTISSEMENT MÉTHODOLOGIQUE
# ============================================================

st.markdown(
    """
    <div class="warning-box">

    <h4>⚠️ Limite méthodologique importante</h4>

    <p>
    Le nombre d'antennes utilisé dans l'analyse provient d'OpenCelliD,
    une base collaborative. L'absence d'une antenne dans les données
    ne signifie donc pas nécessairement une absence réelle de
    couverture mobile.
    </p>

    <p>
    Les résultats doivent être interprétés comme un <b>outil d'aide
    à la décision et de priorisation territoriale</b>, et non comme
    une mesure exhaustive de la couverture réseau réelle.
    </p>

    <p>
    Une validation terrain ou un croisement avec les données
    officielles des opérateurs permettrait de renforcer la fiabilité
    du diagnostic.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PIED DE PAGE
# ============================================================

st.divider()

st.caption(
    "Togo Digital Access — Analyse territoriale | "
    "Projet Économie numérique"
)