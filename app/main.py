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

        .analysis-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
            border-left: 5px solid #2c7fb8;
            margin-bottom: 15px;
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
                errors="coerce",
            ).fillna(0)

    return df


@st.cache_data
def charger_prefectures():
    """Charge les limites administratives des préfectures."""
    gdf = gpd.read_file(PREFECTURES_PATH)

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

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
    df["niveau_priorite"]
    .astype(str)
    .isin(niveaux_selectionnes)
].copy()


st.sidebar.markdown("---")

st.sidebar.caption(
    "📌 Population : WorldPop 2020."
)

st.sidebar.caption(
    "📌 Antennes : OpenCelliD, source collaborative."
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
# CLASSEMENT
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
    La carte permet d'identifier les préfectures présentant le plus
    fort niveau de priorité selon le score territorial.
    """
)


m = folium.Map(
    location=[8.6, 1.2],
    zoom_start=7,
    tiles="CartoDB positron",
)


def couleur_priorite(niveau):
    if niveau == "Forte":
        return "#d73027"
    elif niveau == "Moyenne":
        return "#fc8d59"
    elif niveau == "Faible":
        return "#91cf60"

    return "#cccccc"


for _, row in df_carte.iterrows():

    niveau = row["niveau_priorite"]

    popup_html = f"""
    <div style="width: 260px;">
        <h4>{row['prefecture']}</h4>
        <b>Niveau :</b> {niveau}<br>
        <b>Score :</b> {row['score_priorite']:.3f}<br>
        <b>Population :</b> {row['population_worldpop']:,.0f}<br>
        <b>Agents Mobile Money :</b> {row['agents_mobile_money']:,.0f}<br>
        <b>Antennes recensées :</b> {row['antennes_opencellid']:,.0f}
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


st.markdown(
    """
    **Légende :**

    🔴 **Forte priorité**

    🟠 **Priorité moyenne**

    🟢 **Faible priorité**
    """
)


# ============================================================
# ANALYSE DÉTAILLÉE D'UNE PRÉFECTURE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🔎 Analyse détaillée d’une préfecture</div>',
    unsafe_allow_html=True,
)

prefectures_disponibles = sorted(
    df_filtre["prefecture"].unique()
)

prefecture_selectionnee = st.selectbox(
    "Sélectionnez une préfecture",
    prefectures_disponibles,
)

territoire = df_filtre[
    df_filtre["prefecture"] == prefecture_selectionnee
].iloc[0]


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Population",
        f"{territoire['population_worldpop']:,.0f}",
    )

with col2:
    st.metric(
        "💰 Agents Mobile Money",
        f"{territoire['agents_mobile_money']:,.0f}",
    )

with col3:
    st.metric(
        "📡 Antennes recensées",
        f"{territoire['antennes_opencellid']:,.0f}",
    )

with col4:
    st.metric(
        "🎯 Score priorité",
        f"{territoire['score_priorite']:.3f}",
    )


st.markdown(
    f"""
    <div class="analysis-box">

    <h4>📌 Interprétation : {prefecture_selectionnee}</h4>

    <p>
    <b>{prefecture_selectionnee}</b> est classée au rang
    <b>{int(territoire['rang_priorite'])}</b> sur les
    <b>{len(df)}</b> préfectures analysées.
    Son niveau de priorité est :
    <b>{territoire['niveau_priorite']}</b>.
    </p>

    <p>
    La population estimée est de
    <b>{territoire['population_worldpop']:,.0f}</b> habitants.
    Le territoire compte
    <b>{territoire['agents_mobile_money']:,.0f}</b> agents Mobile Money,
    soit environ
    <b>{territoire['agents_mm_pour_10000_hab']:.2f}</b>
    agents pour 10 000 habitants.
    </p>

    <p>
    La source OpenCelliD recense
    <b>{int(territoire['antennes_opencellid'])}</b>
    antenne(s) dans cette préfecture.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RECOMMANDATION AUTOMATIQUE
# ============================================================

score = territoire["score_priorite"]
ratio_mm = territoire["agents_mm_pour_10000_hab"]
antennes_territoire = territoire["antennes_opencellid"]
population_territoire = territoire["population_worldpop"]


if score >= 0.66:

    recommandation = (
        f"Le territoire de {prefecture_selectionnee} doit être "
        "considéré comme une zone d'intervention prioritaire. "
        "Il est recommandé d'étudier en priorité l'extension des "
        "services numériques, le renforcement du réseau Mobile Money "
        "et la disponibilité réelle des infrastructures mobiles."
    )

elif score >= 0.33:

    recommandation = (
        f"{prefecture_selectionnee} présente un niveau de priorité "
        "intermédiaire. Une surveillance des besoins et un "
        "renforcement ciblé des services numériques pourraient "
        "être envisagés."
    )

else:

    recommandation = (
        f"{prefecture_selectionnee} présente un niveau de priorité "
        "relativement faible selon les indicateurs utilisés. "
        "Les investissements peuvent davantage être orientés vers "
        "les territoires présentant un déficit plus important."
    )


st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>🎯 Recommandation pour {prefecture_selectionnee}</h4>

    <p>
    {recommandation}
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONCLUSIONS GÉNÉRALES
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🎯 Conclusions générales</div>',
    unsafe_allow_html=True,
)


top1 = (
    df.sort_values("rang_priorite")
    .iloc[0]
)

top5 = (
    df.sort_values("rang_priorite")
    .head(5)["prefecture"]
    .tolist()
)

top5_text = ", ".join(top5)


st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>1. Priorité territoriale</h4>

    <p>
    <b>{top1['prefecture']}</b> arrive en première position du
    classement avec un score de
    <b>{top1['score_priorite']:.3f}</b>.
    </p>

    <p>
    Les cinq premières préfectures sont :
    <b>{top5_text}</b>.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


pref_mm_faible = (
    df.sort_values("agents_mm_pour_10000_hab")
    .iloc[0]
)


st.markdown(
    f"""
    <div class="conclusion-box">

    <h4>2. Déficit relatif de Mobile Money</h4>

    <p>
    <b>{pref_mm_faible['prefecture']}</b> présente le plus faible
    ratio d'agents Mobile Money, avec environ
    <b>{pref_mm_faible['agents_mm_pour_10000_hab']:.2f}</b>
    agents pour 10 000 habitants.
    </p>

    <p>
    Le renforcement de la couverture en agents peut constituer un
    levier important pour améliorer l'accès aux services financiers
    numériques dans les territoires moins bien desservis.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="conclusion-box">

    <h4>3. Concentration des services</h4>

    <p>
    Les données montrent une forte concentration des agents
    Mobile Money et des agences télécom dans les principaux pôles
    urbains, notamment <b>Lome Commune</b> et <b>Golfe</b>.
    </p>

    <p>
    Cette concentration souligne l'intérêt d'une stratégie de
    rattrapage territorial visant les zones moins bien équipées.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="conclusion-box">

    <h4>4. Stratégie d'investissement recommandée</h4>

    <p>
    Les investissements devraient prioritairement cibler les
    territoires combinant :
    </p>

    <ul>
        <li>une population importante ;</li>
        <li>un faible nombre d'agents Mobile Money par habitant ;</li>
        <li>une faible présence d'infrastructures recensées ;</li>
        <li>un score de priorité élevé.</li>
    </ul>

    <p>
    Cette approche permettrait de concentrer les ressources sur les
    territoires où l'amélioration de l'accès numérique pourrait avoir
    le plus fort impact.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LIMITES MÉTHODOLOGIQUES
# ============================================================

st.markdown(
    """
    <div class="warning-box">

    <h4>⚠️ Limites méthodologiques</h4>

    <p>
    Les données de population proviennent de WorldPop 2020 et
    constituent une estimation spatiale de la population.
    </p>

    <p>
    Les antennes proviennent d'OpenCelliD, une base collaborative.
    Un nombre nul d'antennes recensées ne signifie donc pas
    nécessairement une absence réelle de couverture mobile.
    </p>

    <p>
    Le score de priorité doit être considéré comme un
    <b>outil d'aide à la décision</b> permettant de comparer les
    territoires, et non comme une mesure absolue de la fracture
    numérique.
    </p>

    <p>
    Un croisement avec les données officielles des opérateurs et,
    lorsque cela est possible, des données de couverture réseau
    permettrait de renforcer le diagnostic.
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
    "Togo Digital Access — Diagnostic territorial | "
    "Projet Économie numérique"
)