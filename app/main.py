import re
import textwrap
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium


_streamlit_markdown = st.markdown


def render_markdown(body, *args, **kwargs):
    """Normalise les blocs HTML avant leur rendu par Streamlit."""
    if kwargs.get("unsafe_allow_html") and "<div" in body:
        html_renderer = getattr(st, "html", None)
        if html_renderer is not None:
            return html_renderer(body)

        body = re.sub(r">\s+<", "><", body)

    return _streamlit_markdown(body, *args, **kwargs)


st.markdown = render_markdown


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Togo Digital Access",
    page_icon="📡",
    layout="wide",
)


# ============================================================
# CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "processed" / "priorites_prefectures.csv"
PREFECTURES_PATH = BASE_DIR / "data" / "processed" / "prefectures_adm2.geojson"
MOBILE_MONEY_PATH = BASE_DIR / "data" / "processed" / "agents_mobile_money.csv"


# ============================================================
# STYLE
# ============================================================

st.markdown(
    textwrap.dedent(
        """
    <style>

    .stApp {
        background:
            linear-gradient(180deg, #f4f7fb 0%, #ffffff 46%, #f8fafc 100%);
        color: #172033;
    }

    .main .block-container {
        max-width: 1380px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    /* HERO */

    .hero {
        padding: 2.5rem 2.8rem;
        border-radius: 8px;
        margin-bottom: 1.25rem;

        background:
            linear-gradient(
                135deg,
                #102a43 0%,
                #0b4f6c 58%,
                #087e8b 100%
            );

        color: white;

        box-shadow:
            0 14px 32px rgba(16, 42, 67, 0.18);
        border-left: 6px solid #f4b942;
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #d8f3f0;
        margin-bottom: 1rem;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.55rem 1rem;
        border-radius: 4px;
        background: rgba(244, 185, 66, 0.16);
        border: 1px solid rgba(244, 185, 66, 0.45);
        color: #fff4d6;
        font-size: 0.9rem;
    }

    /* TITRES */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #102a43;
        margin-top: 1.6rem;
        margin-bottom: 0.35rem;
    }

    .section-description {
        color: #58708a;
        margin-bottom: 1rem;
    }

    /* KPI */

    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.1rem;
        border-radius: 6px;
        border: 1px solid #d9e2ec;
        border-top: 3px solid #0b7285;
        box-shadow: 0 5px 18px rgba(16,42,67,0.06);
    }

    div[data-testid="stMetricLabel"] {
        color: #58708a;
    }

    div[data-testid="stMetricValue"] {
        color: #102a43;
        font-weight: 800;
    }

    /* CARDS */

    .info-card {
        background: white;
        padding: 1.2rem 1.35rem;
        border-radius: 6px;
        border: 1px solid #d9e2ec;
        box-shadow: 0 5px 18px rgba(16,42,67,0.05);
        margin-bottom: 1rem;
    }

    .priority-card {
        background: linear-gradient(
            135deg,
            #fff7ed,
            #ffffff
        );
        padding: 1.15rem 1.3rem;
        border-radius: 6px;
        border: 1px solid #f4d28b;
        border-left: 5px solid #f4b942;
    }

    .warning-card {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-top: 1rem;
        color: #78350f;
    }

    .success-card {
        background: #ecfdf5;
        border-left: 5px solid #10b981;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-top: 1rem;
        color: #065f46;
    }

    .danger-card {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-top: 1rem;
        color: #7f1d1d;
    }

    .executive-summary {
        display: grid;
        grid-template-columns: 1.4fr 1fr 1fr;
        gap: 1px;
        background: #d9e2ec;
        border: 1px solid #d9e2ec;
        border-radius: 6px;
        overflow: hidden;
        margin: 1.15rem 0 1.8rem;
    }

    .executive-summary > div {
        background: #ffffff;
        padding: 1.1rem 1.25rem;
    }

    .executive-label {
        color: #58708a;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .executive-value {
        color: #102a43;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    @media (max-width: 800px) {
        .executive-summary { grid-template-columns: 1fr; }
        .hero-title { font-size: 2.1rem; }
        .hero { padding: 1.8rem 1.25rem; }
    }

    /* TABLE */

    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }

    /* FOOTER */

    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        text-align: center;
        font-size: 0.85rem;
    }

    </style>
    """
    ).strip(),
    unsafe_allow_html=True,
)


# ============================================================
# FONCTIONS
# ============================================================

def format_number(value):
    if pd.isna(value):
        return "—"

    return f"{value:,.0f}".replace(",", " ")


def format_decimal(value, digits=2):
    if pd.isna(value):
        return "—"

    return f"{value:.{digits}f}".replace(".", ",")


def niveau_badge(niveau):

    if niveau == "Forte":
        return (
            '<span style="background:#fee2e2;color:#991b1b;'
            'padding:5px 10px;border-radius:999px;font-weight:700;">'
            "🔴 Forte</span>"
        )

    if niveau == "Moyenne":
        return (
            '<span style="background:#fef3c7;color:#92400e;'
            'padding:5px 10px;border-radius:999px;font-weight:700;">'
            "🟠 Moyenne</span>"
        )

    return (
        '<span style="background:#dcfce7;color:#166534;'
        'padding:5px 10px;border-radius:999px;font-weight:700;">'
        "🟢 Faible</span>"
    )


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    numeric_columns = [
        "population_worldpop",
        "agents_mobile_money",
        "agents_mm_pour_10000_hab",
        "antennes_opencellid",
        "agences_telecom",
        "agences_moov",
        "agences_togocom",
        "agences_canal",
        "score_priorite",
    ]

    for col in numeric_columns:

        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            ).fillna(0)

    return df


@st.cache_data
def load_prefectures():

    gdf = gpd.read_file(PREFECTURES_PATH)

    if "shapeName" in gdf.columns:
        gdf = gdf.rename(
            columns={
                "shapeName": "prefecture"
            }
        )

    return gdf


@st.cache_data
def load_mobile_money():

    if not MOBILE_MONEY_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(MOBILE_MONEY_PATH)


# ============================================================
# CHARGEMENT
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        f"❌ Impossible de charger les données principales.\n\n"
        f"Erreur : {e}"
    )

    st.stop()


try:

    prefectures = load_prefectures()

except Exception as e:

    prefectures = None

    st.warning(
        f"⚠️ Les limites administratives n'ont pas pu être chargées : {e}"
    )


try:

    mobile_money_raw = load_mobile_money()

except Exception:

    mobile_money_raw = pd.DataFrame()


# ============================================================
# NORMALISATION
# ============================================================

df.columns = [
    str(column).strip()
    for column in df.columns
]


if "prefecture" not in df.columns:

    possible_names = [
        "prefecture_nom_bdd",
        "shapeName",
        "nom_prefecture",
    ]

    for name in possible_names:

        if name in df.columns:

            df = df.rename(
                columns={
                    name: "prefecture"
                }
            )

            break


if "prefecture" not in df.columns:

    st.error(
        "❌ La colonne 'prefecture' est absente du fichier "
        "priorites_prefectures.csv."
    )

    st.stop()


# ============================================================
# HERO
# ============================================================

st.markdown(
    textwrap.dedent(
        """
    <div class="hero"><div class="hero-title">📡 Togo Digital Access</div><div class="hero-subtitle">Diagnostic territorial de l'accès aux services numériques au Togo</div><div class="hero-badge">🇹🇬 Économie numérique&nbsp;&nbsp;·&nbsp;&nbsp;Analyse territoriale&nbsp;&nbsp;·&nbsp;&nbsp;Aide à la décision</div></div>
    """
    ).strip(),
    unsafe_allow_html=True,
)


# ============================================================
# INTRODUCTION
# ============================================================

st.markdown(
    textwrap.dedent(
        """
    <div class="info-card"><b>🎯 Objectif du tableau de bord</b><br><br>Identifier les territoires où les besoins en infrastructures et services numériques apparaissent les plus importants, en croisant la population, la disponibilité des agents Mobile Money et la présence d'antennes mobiles.</div>
    """
    ).strip(),
    unsafe_allow_html=True,
)


# ============================================================
# FILTRES
# ============================================================

st.markdown(
    '<div class="section-title">🎛️ Explorer les données</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    "Filtrez les résultats directement depuis la page."
    "</div>",
    unsafe_allow_html=True,
)

filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    niveaux = ["Tous"] + sorted(
        df["niveau_priorite"]
        .dropna()
        .unique()
        .tolist()
    )

    niveau_selection = st.selectbox(
        "🎯 Niveau de priorité",
        niveaux,
    )


with filter_col2:

    prefecture_options = ["Toutes"] + sorted(
        df["prefecture"]
        .dropna()
        .unique()
        .tolist()
    )

    prefecture_selection = st.selectbox(
        "📍 Préfecture",
        prefecture_options,
    )


with filter_col3:

    indicateurs = {
        "Priorité territoriale": "score_priorite",
        "Population": "population_worldpop",
        "Agents Mobile Money / 10 000 hab.": "agents_mm_pour_10000_hab",
        "Antennes OpenCelliD": "antennes_opencellid",
    }

    indicateur_label = st.selectbox(
        "📊 Indicateur",
        list(indicateurs.keys()),
    )

    indicateur = indicateurs[indicateur_label]


# ============================================================
# APPLICATION DES FILTRES
# ============================================================

df_filtre = df.copy()


if niveau_selection != "Tous":

    df_filtre = df_filtre[
        df_filtre["niveau_priorite"]
        == niveau_selection
    ]


if prefecture_selection != "Toutes":

    df_filtre = df_filtre[
        df_filtre["prefecture"]
        == prefecture_selection
    ]


# ============================================================
# KPI
# ============================================================

st.markdown(
    '<div class="section-title">📊 Vue d’ensemble</div>',
    unsafe_allow_html=True,
)


population_total = df["population_worldpop"].sum()

mobile_money_total = df["agents_mobile_money"].sum()

antennes_total = df["antennes_opencellid"].sum()

agences_total = df["agences_telecom"].sum()

nb_prefectures = df["prefecture"].nunique()

nb_priorite_forte = (
    df["niveau_priorite"]
    .eq("Forte")
    .sum()
)


k1, k2, k3, k4, k5 = st.columns(5)


with k1:

    st.metric(
        "👥 Population",
        format_number(population_total),
    )


with k2:

    st.metric(
        "💳 Agents Mobile Money",
        format_number(mobile_money_total),
    )


with k3:

    st.metric(
        "📡 Antennes",
        format_number(antennes_total),
    )


with k4:

    st.metric(
        "🏢 Agences télécom",
        format_number(agences_total),
    )


with k5:

    st.metric(
        "🔴 Priorités fortes",
        format_number(nb_priorite_forte),
    )


top_priority = df.sort_values("score_priorite", ascending=False).iloc[0]

st.markdown(
    f"""
    <div class="executive-summary">
        <div>
            <div class="executive-label">Signal prioritaire</div>
            <div class="executive-value">{top_priority['prefecture']} · score {format_decimal(top_priority['score_priorite'], 3)}</div>
        </div>
        <div>
            <div class="executive-label">Lecture opérationnelle</div>
            <div class="executive-value">{format_number(nb_priorite_forte)} territoires à examiner</div>
        </div>
        <div>
            <div class="executive-label">Cadre d'analyse</div>
            <div class="executive-value">Population 40% · Mobile Money 40% · Antennes 20%</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏠 Vue nationale",
        "🗺️ Carte territoriale",
        "🏆 Priorités",
        "🔎 Diagnostic",
        "🎯 Recommandations",
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">📈 Lecture nationale</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        "Comparaison des principaux indicateurs territoriaux."
        "</div>",
        unsafe_allow_html=True,
    )


    col_left, col_right = st.columns(2)


    # --------------------------------------------------------
    # POPULATION
    # --------------------------------------------------------

    with col_left:

        population_chart = (
            df.sort_values(
                "population_worldpop",
                ascending=False,
            )
            .head(15)
            .sort_values("population_worldpop")
        )


        fig_population = px.bar(
            population_chart,
            x="population_worldpop",
            y="prefecture",
            orientation="h",
            title="👥 Top 15 des préfectures par population",
            labels={
                "population_worldpop": "Population estimée",
                "prefecture": "Préfecture",
            },
            text="population_worldpop",
        )


        fig_population.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
        )


        fig_population.update_layout(
            height=550,
            margin=dict(
                l=20,
                r=40,
                t=70,
                b=20,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
        )


        st.plotly_chart(
            fig_population,
            use_container_width=True,
        )


    # --------------------------------------------------------
    # MOBILE MONEY
    # --------------------------------------------------------

    with col_right:

        mm_chart = (
            df.sort_values(
                "agents_mm_pour_10000_hab",
                ascending=True,
            )
            .head(15)
        )


        fig_mm = px.bar(
            mm_chart,
            x="agents_mm_pour_10000_hab",
            y="prefecture",
            orientation="h",
            title="💳 Plus faible densité Mobile Money",
            labels={
                "agents_mm_pour_10000_hab":
                    "Agents / 10 000 habitants",
                "prefecture":
                    "Préfecture",
            },
            text="agents_mm_pour_10000_hab",
        )


        fig_mm.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
        )


        fig_mm.update_layout(
            height=550,
            margin=dict(
                l=20,
                r=40,
                t=70,
                b=20,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
        )


        st.plotly_chart(
            fig_mm,
            use_container_width=True,
        )


    # --------------------------------------------------------
    # AGENCES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🏢 Présence des agences télécom</div>',
        unsafe_allow_html=True,
    )


    # NB : "agences_telecom" est le référentiel agrégé = union de
    # agences_moov + agences_togocom (vérifié à la source). On l'exclut
    # ici pour éviter d'afficher un double comptage dans la répartition
    # par opérateur.
    agency_columns = [
        col
        for col in [
            "agences_moov",
            "agences_togocom",
            "agences_canal",
        ]
        if col in df.columns
    ]


    if agency_columns:

        agency_data = pd.DataFrame(
            {
                "Opérateur": [
                    col.replace(
                        "agences_",
                        ""
                    ).capitalize()
                    for col in agency_columns
                ],
                "Nombre": [
                    df[col].sum()
                    for col in agency_columns
                ],
            }
        )


        fig_agencies = px.bar(
            agency_data,
            x="Opérateur",
            y="Nombre",
            text="Nombre",
            title="Répartition des agences par opérateur",
        )


        fig_agencies.update_traces(
            textposition="outside"
        )


        fig_agencies.update_layout(
            height=420,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )


        st.plotly_chart(
            fig_agencies,
            use_container_width=True,
        )


    # --------------------------------------------------------
    # MOBILE MONEY OPERATEURS
    # --------------------------------------------------------

    if (
        not mobile_money_raw.empty
        and "operateur" in mobile_money_raw.columns
    ):

        st.markdown(
            '<div class="section-title">'
            "💳 Structure du réseau Mobile Money"
            "</div>",
            unsafe_allow_html=True,
        )


        operator_counts = (
            mobile_money_raw["operateur"]
            .fillna("Non renseigné")
            .astype(str)
            .value_counts()
            .reset_index()
        )


        operator_counts.columns = [
            "operateur",
            "nombre",
        ]


        fig_operator = px.pie(
            operator_counts,
            names="operateur",
            values="nombre",
            hole=0.55,
            title="Répartition des points Mobile Money",
        )


        fig_operator.update_layout(
            height=430,
            paper_bgcolor="white",
        )


        st.plotly_chart(
            fig_operator,
            use_container_width=True,
        )


# ============================================================
# TAB 2 — CARTE
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">'
        "🗺️ Carte de la priorité numérique"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        "Visualisation territoriale du niveau de priorité."
        "</div>",
        unsafe_allow_html=True,
    )


    if prefectures is not None:

        map_data = prefectures.copy()


        merge_columns = [
            "prefecture",
            "population_worldpop",
            "agents_mobile_money",
            "agents_mm_pour_10000_hab",
            "antennes_opencellid",
            "score_priorite",
            "niveau_priorite",
        ]


        merge_columns = [
            col
            for col in merge_columns
            if col in df.columns
        ]


        map_data = map_data.merge(
            df[merge_columns],
            on="prefecture",
            how="left",
        )

        map_filter_col1, map_filter_col2 = st.columns(2)

        with map_filter_col1:
            map_niveau_options = ["Tous"] + sorted(
                map_data["niveau_priorite"].dropna().astype(str).unique().tolist()
            )
            map_niveau = st.selectbox(
                "Niveau à afficher",
                map_niveau_options,
                key="map_niveau",
            )

        with map_filter_col2:
            map_prefecture_options = ["Toutes"] + sorted(
                map_data["prefecture"].dropna().astype(str).unique().tolist()
            )
            map_prefecture = st.selectbox(
                "Préfecture à analyser",
                map_prefecture_options,
                key="map_prefecture",
            )

        map_filtered = map_data.copy()
        if map_niveau != "Tous":
            map_filtered = map_filtered[
                map_filtered["niveau_priorite"].astype(str) == map_niveau
            ]
        if map_prefecture != "Toutes":
            map_filtered = map_filtered[
                map_filtered["prefecture"] == map_prefecture
            ]

        map_kpi1, map_kpi2, map_kpi3 = st.columns(3)
        with map_kpi1:
            st.metric("Territoires affichés", len(map_filtered))
        with map_kpi2:
            st.metric(
                "Population concernée",
                format_number(map_filtered["population_worldpop"].sum()),
            )
        with map_kpi3:
            st.metric(
                "Score moyen",
                format_decimal(map_filtered["score_priorite"].mean(), 3),
            )

        show_points = st.checkbox(
            "Afficher les infrastructures et services ponctuels",
            value=True,
            help="Les points proviennent des sources ouvertes nettoyées. "
            "OpenCelliD ne constitue pas un inventaire exhaustif.",
        )


        m = folium.Map(
            location=[
                8.65,
                1.15,
            ],
            zoom_start=7,
            tiles="CartoDB positron",
        )


        def style_function(feature):

            niveau = feature[
                "properties"
            ].get(
                "niveau_priorite",
                "Faible",
            )


            if niveau == "Forte":

                fill_color = "#ef4444"

            elif niveau == "Moyenne":

                fill_color = "#f59e0b"

            else:

                fill_color = "#22c55e"


            return {
                "fillColor": fill_color,
                "color": "#ffffff",
                "weight": 1,
                "fillOpacity": 0.70,
            }


        tooltip_fields = [
            "prefecture",
        ]

        tooltip_aliases = [
            "Préfecture",
        ]


        optional_map_fields = [
            (
                "population_worldpop",
                "Population",
            ),
            (
                "agents_mobile_money",
                "Agents Mobile Money",
            ),
            (
                "agents_mm_pour_10000_hab",
                "Agents / 10 000 hab.",
            ),
            (
                "antennes_opencellid",
                "Antennes OpenCelliD",
            ),
            (
                "score_priorite",
                "Score priorité",
            ),
            (
                "niveau_priorite",
                "Niveau",
            ),
        ]


        for field, alias in optional_map_fields:

            if field in map_data.columns:

                tooltip_fields.append(field)

                tooltip_aliases.append(alias)


        tooltip = folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            labels=True,
        )


        folium.GeoJson(
            map_filtered.to_json(),
            name="Priorité numérique",
            style_function=style_function,
            tooltip=tooltip,
        ).add_to(m)

        if show_points:
            point_layers = [
                ("Agences Moov", "agences_moov.csv", "#0b7285", "Agence"),
                ("Agences Togocom", "agences_togocom.csv", "#f4b942", "Agence"),
                ("Datacenters", "datacenters.csv", "#7c3aed", "Datacenter"),
            ]
            for layer_name, filename, color, point_type in point_layers:
                points_path = BASE_DIR / "data" / "processed" / filename
                if not points_path.exists():
                    continue
                points_df = pd.read_csv(points_path)
                if points_df.empty or "geometry" not in points_df.columns:
                    continue
                points = gpd.GeoDataFrame(
                    points_df,
                    geometry=gpd.GeoSeries.from_wkt(points_df["geometry"]),
                    crs="EPSG:4326",
                )
                joined_points = gpd.sjoin(
                    points,
                    map_filtered[["prefecture", "geometry"]],
                    how="inner",
                    predicate="within",
                )
                feature_group = folium.FeatureGroup(name=layer_name)
                for _, point in joined_points.iterrows():
                    folium.CircleMarker(
                        location=[point.geometry.y, point.geometry.x],
                        radius=5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.85,
                        tooltip=f"{point_type} · {point.get('prefecture', 'Territoire')}",
                    ).add_to(feature_group)
                feature_group.add_to(m)

            cell_path = BASE_DIR / "data" / "processed" / "opencellid_615.csv"
            if cell_path.exists():
                cells = pd.read_csv(cell_path)
                cell_group = folium.FeatureGroup(name="Antennes OpenCelliD")
                for _, cell in cells.dropna(subset=["lat", "lon"]).iterrows():
                    cell_point = gpd.GeoSeries.from_xy(
                        [cell["lon"]], [cell["lat"]], crs="EPSG:4326"
                    ).iloc[0]
                    if not map_filtered.geometry.contains(cell_point).any():
                        continue
                    folium.CircleMarker(
                        location=[cell["lat"], cell["lon"]],
                        radius=4,
                        color="#dc2626",
                        fill=True,
                        fill_color="#dc2626",
                        fill_opacity=0.8,
                        tooltip="Antenne observée · OpenCelliD",
                    ).add_to(cell_group)
                cell_group.add_to(m)

            mobile_group = folium.FeatureGroup(name="Mobile Money par préfecture")
            for _, territory in map_filtered.iterrows():
                centroid = territory.geometry.representative_point()
                agents = territory.get("agents_mobile_money", 0)
                radius = max(5, min(18, 5 + agents / 250))
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=radius,
                    color="#16a34a",
                    fill=True,
                    fill_color="#16a34a",
                    fill_opacity=0.35,
                    tooltip=(
                        f"Mobile Money · {territory['prefecture']} · "
                        f"{format_number(agents)} agents"
                    ),
                ).add_to(mobile_group)
            mobile_group.add_to(m)

            folium.LayerControl(collapsed=False).add_to(m)


        legend_html = """
        <div style="
            position: fixed;
            bottom: 35px;
            left: 35px;
            z-index: 9999;
            background: white;
            padding: 12px 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            font-size: 13px;
        ">

            <b>Priorité</b><br>

            <span style="color:#ef4444;">●</span>
            Forte<br>

            <span style="color:#f59e0b;">●</span>
            Moyenne<br>

            <span style="color:#22c55e;">●</span>
            Faible

        </div>
        """


        m.get_root().html.add_child(
            folium.Element(
                legend_html
            )
        )


        st_folium(
            m,
            width=None,
            height=650,
            returned_objects=[],
        )

        st.markdown(
            '<div class="section-title">📋 Données des territoires affichés</div>',
            unsafe_allow_html=True,
        )
        map_table = map_filtered[
            [
                "prefecture",
                "niveau_priorite",
                "score_priorite",
                "population_worldpop",
                "agents_mm_pour_10000_hab",
                "antennes_opencellid",
            ]
        ].copy().sort_values("score_priorite", ascending=False)
        map_table.columns = [
            "Préfecture",
            "Priorité",
            "Score",
            "Population",
            "Agents MM / 10k",
            "Antennes",
        ]
        map_table["Population"] = map_table["Population"].round(0).astype(int)
        map_table["Score"] = map_table["Score"].round(3)
        map_table["Agents MM / 10k"] = map_table["Agents MM / 10k"].round(2)
        map_table["Antennes"] = map_table["Antennes"].round(0).astype(int)
        st.dataframe(
            map_table,
            use_container_width=True,
            hide_index=True,
        )

        zero_antenna = map_filtered[
            map_filtered["antennes_opencellid"] == 0
        ]["prefecture"].tolist()
        if zero_antenna:
            st.info(
                "Zones sans antenne observée dans OpenCelliD : "
                + ", ".join(zero_antenna)
                + ". Cela signale une absence dans la donnée disponible, "
                "pas nécessairement une absence réelle de couverture."
            )


    else:

        st.error(
            "La carte ne peut pas être affichée sans "
            "le fichier des limites administratives."
        )


# ============================================================
# TAB 3 — PRIORITÉS
# ============================================================

with tab3:

    st.markdown(
        '<div class="section-title">'
        "🏆 Classement des territoires prioritaires"
        "</div>",
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-description">'
        "Les territoires sont classés selon le score de priorité."
        "</div>",
        unsafe_allow_html=True,
    )


    top_priorites = (
        df_filtre.sort_values(
            indicateur,
            ascending=False,
        )
        .head(15)
        .copy()
    )


    fig_priority = px.bar(
        top_priorites.sort_values(
            indicateur
        ),
        x=indicateur,
        y="prefecture",
        orientation="h",
        color="niveau_priorite",
        text=indicateur,
        title=f"Top des préfectures — {indicateur_label}",
        labels={
            "score_priorite":
                "Score de priorité",
            indicateur:
                indicateur_label,
            "prefecture":
                "Préfecture",
            "niveau_priorite":
                "Niveau",
        },
        color_discrete_map={
            "Forte": "#ef4444",
            "Moyenne": "#f59e0b",
            "Faible": "#22c55e",
        },
    )


    fig_priority.update_traces(
        texttemplate=(
            "%{text:.2f}"
            if indicateur in [
                "score_priorite",
                "agents_mm_pour_10000_hab",
            ]
            else "%{text:,.0f}"
        ),
        textposition="outside",
    )


    fig_priority.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=20,
            r=60,
            t=70,
            b=20,
        ),
    )


    st.plotly_chart(
        fig_priority,
        use_container_width=True,
    )


    st.markdown(
        '<div class="section-title">📋 Tableau détaillé</div>',
        unsafe_allow_html=True,
    )


    table_columns = [
        "prefecture",
        "population_worldpop",
        "agents_mobile_money",
        "agents_mm_pour_10000_hab",
        "antennes_opencellid",
        "score_priorite",
        "niveau_priorite",
    ]


    table_columns = [
        col
        for col in table_columns
        if col in top_priorites.columns
    ]


    display_df = top_priorites[
        table_columns
    ].copy()


    display_df = display_df.rename(
        columns={
            "prefecture": "Préfecture",
            "population_worldpop": "Population",
            "agents_mobile_money": "Agents MM",
            "agents_mm_pour_10000_hab":
                "MM / 10k hab.",
            "antennes_opencellid": "Antennes",
            "score_priorite": "Score",
            "niveau_priorite": "Priorité",
        }
    )


    if "Population" in display_df.columns:

        display_df["Population"] = (
            display_df["Population"]
            .round(0)
            .astype(int)
        )


    if "Agents MM" in display_df.columns:

        display_df["Agents MM"] = (
            display_df["Agents MM"]
            .round(0)
            .astype(int)
        )


    if "Antennes" in display_df.columns:

        display_df["Antennes"] = (
            display_df["Antennes"]
            .round(0)
            .astype(int)
        )


    if "MM / 10k hab." in display_df.columns:

        display_df["MM / 10k hab."] = (
            display_df["MM / 10k hab."]
            .round(2)
        )


    if "Score" in display_df.columns:

        display_df["Score"] = (
            display_df["Score"]
            .round(3)
        )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Télécharger le classement filtré (CSV)",
        data=display_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="classement_priorites_filtre.csv",
        mime="text/csv",
    )


# ============================================================
# TAB 4 — DIAGNOSTIC
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">'
        "🔎 Diagnostic d’une préfecture"
        "</div>",
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-description">'
        "Sélectionnez une préfecture pour obtenir une lecture détaillée."
        "</div>",
        unsafe_allow_html=True,
    )


    diagnostic_options = sorted(
        df["prefecture"]
        .dropna()
        .unique()
        .tolist()
    )


    diagnostic_prefecture = st.selectbox(
        "📍 Choisir une préfecture",
        diagnostic_options,
        key="diagnostic_prefecture",
    )


    row = df[
        df["prefecture"]
        == diagnostic_prefecture
    ].iloc[0]


    niveau = row["niveau_priorite"]


    if niveau == "Forte":

        st.markdown(
            textwrap.dedent(
                """
            <div class="danger-card">

                <b>🔴 Priorité forte</b><br><br>

                Cette préfecture présente un besoin relatif important
                au regard des indicateurs retenus.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


    elif niveau == "Moyenne":

        st.markdown(
            textwrap.dedent(
                """
            <div class="warning-card">

                <b>🟠 Priorité moyenne</b><br><br>

                Cette préfecture présente une situation intermédiaire
                nécessitant une surveillance et potentiellement
                des actions ciblées.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


    else:

        st.markdown(
            textwrap.dedent(
                """
            <div class="success-card">

                <b>🟢 Priorité faible</b><br><br>

                Les indicateurs disponibles suggèrent une situation
                relativement moins prioritaire.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


    st.write("")


    # --------------------------------------------------------
    # KPI DIAGNOSTIC
    # --------------------------------------------------------

    d1, d2, d3, d4 = st.columns(4)


    with d1:

        st.metric(
            "👥 Population",
            format_number(
                row["population_worldpop"]
            ),
        )


    with d2:

        st.metric(
            "💳 Agents Mobile Money",
            format_number(
                row["agents_mobile_money"]
            ),
        )


    with d3:

        st.metric(
            "📊 MM / 10 000 hab.",
            format_decimal(
                row["agents_mm_pour_10000_hab"],
                2,
            ),
        )


    with d4:

        st.metric(
            "📡 Antennes",
            format_number(
                row["antennes_opencellid"]
            ),
        )


    # --------------------------------------------------------
    # COMPARAISON NATIONALE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        "📐 Positionnement"
        "</div>",
        unsafe_allow_html=True,
    )


    national_mm = df[
        "agents_mm_pour_10000_hab"
    ].mean()


    national_population = df[
        "population_worldpop"
    ].mean()


    national_antennas = df[
        "antennes_opencellid"
    ].mean()


    comp1, comp2, comp3 = st.columns(3)


    with comp1:

        value = row[
            "agents_mm_pour_10000_hab"
        ]


        if value < national_mm:

            st.markdown(
                f"""
                <div class="danger-card">

                    <b>💳 Mobile Money</b><br><br>

                    {format_decimal(value, 2)}
                    agents / 10 000 habitants

                    <br>

                    Moyenne :
                    {format_decimal(national_mm, 2)}

                    <br><br>

                    <b>
                    → Densité inférieure à la moyenne.
                    </b>

                </div>
                """,
                unsafe_allow_html=True,
            )


        else:

            st.markdown(
                f"""
                <div class="success-card">

                    <b>💳 Mobile Money</b><br><br>

                    {format_decimal(value, 2)}
                    agents / 10 000 habitants

                    <br>

                    Moyenne :
                    {format_decimal(national_mm, 2)}

                    <br><br>

                    <b>
                    → Densité supérieure à la moyenne.
                    </b>

                </div>
                """,
                unsafe_allow_html=True,
            )


    with comp2:

        population_value = row[
            "population_worldpop"
        ]


        if population_value > national_population:

            population_message = (
                "Population supérieure à la moyenne."
            )

        else:

            population_message = (
                "Population inférieure à la moyenne."
            )


        st.markdown(
            f"""
            <div class="info-card">

                <b>👥 Pression démographique</b>

                <br><br>

                Population :
                <b>{format_number(population_value)}</b>

                <br>

                Moyenne :
                <b>{format_number(national_population)}</b>

                <br><br>

                {population_message}

            </div>
            """,
            unsafe_allow_html=True,
        )


    with comp3:

        antenna_value = row[
            "antennes_opencellid"
        ]


        if antenna_value <= national_antennas:

            antenna_message = (
                "Présence d'antennes observées "
                "inférieure ou égale à la moyenne."
            )

        else:

            antenna_message = (
                "Présence d'antennes observées "
                "supérieure à la moyenne."
            )


        st.markdown(
            f"""
            <div class="info-card">

                <b>📡 Infrastructure observée</b>

                <br><br>

                Antennes OpenCelliD :
                <b>{format_number(antenna_value)}</b>

                <br>

                Moyenne :
                <b>{format_decimal(national_antennas, 2)}</b>

                <br><br>

                {antenna_message}

            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # SCATTER
    # --------------------------------------------------------

    comparaison = df[
        [
            "prefecture",
            "population_worldpop",
            "agents_mm_pour_10000_hab",
            "antennes_opencellid",
            "score_priorite",
            "niveau_priorite",
        ]
    ].copy()


    fig_scatter = px.scatter(
        comparaison,
        x="agents_mm_pour_10000_hab",
        y="score_priorite",
        size="population_worldpop",
        color="niveau_priorite",
        hover_name="prefecture",
        hover_data=[
            "population_worldpop",
            "antennes_opencellid",
        ],
        title="💳 Mobile Money et niveau de priorité",
        labels={
            "agents_mm_pour_10000_hab":
                "Agents Mobile Money / 10 000 hab.",
            "score_priorite":
                "Score de priorité",
            "population_worldpop":
                "Population",
            "niveau_priorite":
                "Priorité",
        },
        color_discrete_map={
            "Forte": "#ef4444",
            "Moyenne": "#f59e0b",
            "Faible": "#22c55e",
        },
    )


    selected_point = comparaison[
        comparaison["prefecture"]
        == diagnostic_prefecture
    ]


    if not selected_point.empty:

        fig_scatter.add_scatter(
            x=selected_point[
                "agents_mm_pour_10000_hab"
            ],
            y=selected_point[
                "score_priorite"
            ],
            mode="markers",
            marker=dict(
                size=20,
                symbol="star",
                line=dict(
                    width=2,
                    color="black",
                ),
            ),
            name="Préfecture sélectionnée",
        )


    fig_scatter.update_layout(
        height=560,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )


    st.plotly_chart(
        fig_scatter,
        use_container_width=True,
    )


# ============================================================
# TAB 5 — RECOMMANDATIONS
# ============================================================

with tab5:

    st.markdown(
        '<div class="section-title">'
        "🎯 Recommandations stratégiques"
        "</div>",
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-description">'
        "Des pistes d'action sont proposées à partir du profil "
        "des territoires."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(
        "⚠️ Limites méthodologiques et conditions de lecture",
        expanded=True,
    ):
        st.markdown(
            """
            **À retenir avant toute décision d'investissement :**

            - La population provient de l'estimation WorldPop 2020 : elle sert à comparer les territoires, mais ne remplace pas un recensement.
            - OpenCelliD est une base collaborative. Une antenne non observée signifie une absence dans la donnée, pas nécessairement une absence réelle de couverture.
            - Le score combine la pression démographique (40 %), le déficit Mobile Money (40 %) et les antennes observées (20 %).
            - Le classement est un outil de présélection. Il doit être confirmé par des données réseau officielles, une validation terrain et une analyse de la qualité de service.
            - Les agences Telecom sont un référentiel agrégé : elles ne doivent pas être additionnées aux agences Moov et Togocom pour éviter le double comptage.
            """
        )


    # --------------------------------------------------------
    # TOP 5
    # --------------------------------------------------------

    top5 = (
        df.sort_values(
            "score_priorite",
            ascending=False,
        )
        .head(5)
    )


    st.markdown(
        textwrap.dedent(
            """
        <div class="priority-card">

            <b>🚨 Territoires à examiner en premier</b>

        </div>
        """
        ).strip(),
        unsafe_allow_html=True,
    )


    st.write("")


    for index, (_, row_rec) in enumerate(
        top5.iterrows(),
        start=1,
    ):

        prefecture = row_rec["prefecture"]

        score = row_rec["score_priorite"]

        mm_density = row_rec[
            "agents_mm_pour_10000_hab"
        ]

        antennas = row_rec[
            "antennes_opencellid"
        ]

        population = row_rec[
            "population_worldpop"
        ]


        if mm_density < national_mm:

            mm_action = (
                "renforcer en priorité la densité "
                "du réseau Mobile Money"
            )

        else:

            mm_action = (
                "maintenir la couverture Mobile Money "
                "tout en surveillant l'évolution de la demande"
            )


        if antennas == 0:

            antenna_action = (
                "évaluer la nécessité d'un renforcement "
                "de la couverture mobile"
            )

        else:

            antenna_action = (
                "examiner la capacité et la répartition "
                "des infrastructures existantes"
            )


        st.markdown(
            f"""
            <div class="info-card">

                <b>{index}. {prefecture}</b>

                &nbsp;&nbsp;

                {niveau_badge(
                    row_rec["niveau_priorite"]
                )}

                <br><br>

                <b>Score de priorité :</b>
                {format_decimal(score, 3)}

                &nbsp; · &nbsp;

                <b>Population :</b>
                {format_number(population)}

                &nbsp; · &nbsp;

                <b>Mobile Money :</b>
                {format_decimal(mm_density, 2)}
                / 10 000 hab.

                &nbsp; · &nbsp;

                <b>Antennes :</b>
                {format_number(antennas)}

                <br><br>

                <b>➡️ Orientation :</b>

                <br>

                • {mm_action}.

                <br>

                • {antenna_action}.

                <br>

                • Prioriser une validation terrain avant
                  tout investissement majeur.

            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # AXES D'ACTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        "🧭 Axes d’action proposés"
        "</div>",
        unsafe_allow_html=True,
    )


    rec1, rec2 = st.columns(2)


    with rec1:

        st.markdown(
            textwrap.dedent(
                """
            <div class="info-card">

                <b>
                1️⃣ Étendre les services dans les territoires sous-dotés
                </b>

                <br><br>

                Concentrer les diagnostics complémentaires sur les
                préfectures combinant forte population et faible densité
                de services Mobile Money.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


        st.markdown(
            textwrap.dedent(
                """
            <div class="info-card">

                <b>
                2️⃣ Renforcer le maillage numérique
                </b>

                <br><br>

                Utiliser la combinaison des indicateurs démographiques
                et d'infrastructures pour identifier les zones nécessitant
                une analyse technique plus approfondie.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


    with rec2:

        st.markdown(
            textwrap.dedent(
                """
            <div class="info-card">

                <b>
                3️⃣ Prioriser les investissements
                </b>

                <br><br>

                Le score de priorité peut servir de mécanisme de
                présélection des territoires avant les études de terrain,
                les audits réseau et les arbitrages d'investissement.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


        st.markdown(
            textwrap.dedent(
                """
            <div class="info-card">

                <b>
                4️⃣ Améliorer progressivement la donnée
                </b>

                <br><br>

                Compléter les données disponibles par des mesures
                actualisées de couverture réseau, de qualité de service,
                de capacité des antennes et de fréquentation réelle
                des services numériques.

            </div>
            """
            ).strip(),
            unsafe_allow_html=True,
        )


# ============================================================
# MÉTHODOLOGIE
# ============================================================

with st.expander(
    "📐 Voir la méthodologie du score de priorité"
):

    st.markdown(
        textwrap.dedent(
            """
        Le score de priorité repose sur trois dimensions :

        ### 1. Pression démographique — 40 %

        Les territoires fortement peuplés obtiennent une priorité
        plus importante.

        ### 2. Déficit Mobile Money — 40 %

        Une faible densité d'agents Mobile Money par rapport à la
        population augmente le niveau de priorité.

        ### 3. Déficit d'antennes observées — 20 %

        Une faible présence d'antennes OpenCelliD augmente également
        le niveau de priorité.

        ### Formule

        **Score = 0,40 × Population
        + 0,40 × Déficit Mobile Money
        + 0,20 × Déficit Antennes**

        Les indicateurs sont normalisés avant leur combinaison.

        Le score sert à hiérarchiser les territoires et doit être
        interprété comme un outil d'aide à la décision.
        """
        ).strip()
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    textwrap.dedent(
        """
    <div class="footer">

        <b>Togo Digital Access</b>

        <br>

        Défi Économie numérique · Analyse territoriale du Togo

        <br>

        Python · Streamlit · GeoPandas · Folium · Plotly

    </div>
    """
    ).strip(),
    unsafe_allow_html=True,
)