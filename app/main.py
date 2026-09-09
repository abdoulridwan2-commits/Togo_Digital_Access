from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Togo Digital Access | Intelligence territoriale",
    page_icon="TG",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED = BASE_DIR / "data" / "processed"
DATA_PATH = PROCESSED / "priorites_prefectures.csv"
PREFECTURES_PATH = PROCESSED / "prefectures_adm2.geojson"

st.markdown(
    """
    <style>
    :root { --ink:#102a43; --muted:#58708a; --teal:#087e8b; --gold:#f4b942; --line:#d9e2ec; }
    .stApp { background:linear-gradient(180deg,#f4f7fb 0%,#fff 46%,#f8fafc 100%); color:#172033; }
    .main .block-container { max-width:1400px; padding:1.1rem 2rem 3.5rem; }
    .stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp select { font-family:"Segoe UI","Helvetica Neue",sans-serif; }
    [data-testid="stHeader"] { background:rgba(244,247,251,.92); }
    .hero { background:linear-gradient(125deg,#102a43 0%,#0b4f6c 58%,#087e8b 100%); color:#fff; padding:2.3rem 2.6rem; border-radius:8px; border-left:6px solid var(--gold); box-shadow:0 16px 38px rgba(16,42,67,.18); margin-bottom:1rem; }
    .hero-grid { display:grid; grid-template-columns:minmax(0,1.7fr) minmax(220px,.8fr); gap:2rem; align-items:end; }
    .eyebrow { color:#f4b942; font-size:.75rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.7rem; }
    .hero h1 { font-size:2.75rem; line-height:1.05; margin:0 0 .65rem; color:#fff; }
    .hero p { font-size:1.08rem; color:#d8f3f0; max-width:780px; margin:0 0 1rem; }
    .hero-badge { display:inline-block; padding:.45rem .7rem; border:1px solid rgba(244,185,66,.5); background:rgba(244,185,66,.14); border-radius:4px; color:#fff4d6; font-size:.83rem; }
    .hero-signal { border-left:1px solid rgba(216,243,240,.4); padding-left:1.2rem; }
    .hero-signal small,.kicker { color:#b8e4df; text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; font-weight:800; }
    .hero-signal strong { display:block; color:#fff; font-size:2.1rem; margin:.2rem 0; }
    .hero-signal span { color:#d8f3f0; font-size:.85rem; }
    .section-head { margin:1.35rem 0 .75rem; }
    .section-head h2 { color:var(--ink); font-size:1.35rem; margin:0; }
    .section-head p { color:var(--muted); margin:.25rem 0 0; }
    .panel { background:#fff; border:1px solid var(--line); border-radius:7px; padding:1rem 1.15rem; box-shadow:0 5px 18px rgba(16,42,67,.045); }
    .panel h3 { color:var(--ink); font-size:1rem; margin:0 0 .55rem; }
    .interpretation { background:#eef7f7; border-left:4px solid var(--teal); border-radius:5px; padding:.8rem 1rem; margin:.7rem 0 1.2rem; color:#164e63; }
    .conclusion { background:#fff8e7; border-left:4px solid var(--gold); border-radius:5px; padding:.8rem 1rem; margin:.7rem 0 1.2rem; color:#6d4b09; }
    .method { background:#f8fafc; border:1px solid var(--line); border-radius:6px; padding:.85rem 1rem; color:#40566d; font-size:.9rem; }
    .priority-strong { color:#b91c1c; font-weight:800; } .priority-medium { color:#a16207; font-weight:800; } .priority-low { color:#15803d; font-weight:800; }
    .executive { display:grid; grid-template-columns:1.35fr 1fr 1fr; gap:1px; background:var(--line); border:1px solid var(--line); border-radius:7px; overflow:hidden; margin:1rem 0 1.3rem; }
    .executive > div { background:#fff; padding:1rem 1.15rem; } .executive small { color:var(--muted); display:block; text-transform:uppercase; letter-spacing:.07em; font-weight:800; } .executive strong { display:block; color:var(--ink); font-size:1.15rem; margin-top:.25rem; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-top:3px solid var(--teal); border-radius:6px; padding:.85rem 1rem; box-shadow:0 5px 18px rgba(16,42,67,.05); }
    div[data-testid="stMetricLabel"] { color:var(--muted); } div[data-testid="stMetricValue"] { color:var(--ink); font-size:1.65rem; font-weight:800; }
    div[data-baseweb="select"] > div { border-color:#c9d5e2; border-radius:5px; background:#fff; min-height:2.55rem; }
    div[data-baseweb="select"] > div:hover, div[data-baseweb="select"] > div:focus-within { border-color:var(--teal); box-shadow:0 0 0 2px rgba(8,126,139,.12); }
    div[data-testid="stCheckbox"] { background:#fff; border:1px solid var(--line); border-radius:5px; padding:.45rem .7rem; }
    button[data-baseweb="tab"] { color:var(--muted); font-weight:750; border-bottom:3px solid transparent; padding:.75rem .8rem .65rem; }
    button[data-baseweb="tab"]:hover { color:var(--teal); background:#eef7f7; } button[data-baseweb="tab"][aria-selected="true"] { color:var(--teal); border-bottom-color:var(--gold); background:#fff; }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:.2rem; border-bottom:1px solid var(--line); }
    [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] { border:1px solid var(--line); border-radius:6px; overflow:hidden; box-shadow:0 5px 18px rgba(16,42,67,.04); background:#fff; }
    [data-testid="stAlert"] { border-radius:6px; border-left-width:4px; } details[data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:6px; }
    .map-guide { display:flex; flex-wrap:wrap; gap:.45rem; margin:.45rem 0 .75rem; } .map-guide span { background:#fff; border:1px solid var(--line); border-radius:4px; padding:.3rem .5rem; color:var(--muted); font-size:.78rem; } .map-guide i { display:inline-block; width:.65rem; height:.65rem; border-radius:50%; margin-right:.25rem; }
    @media(max-width:800px) { .main .block-container{padding:1rem .8rem 2rem;} .hero{padding:1.6rem 1.2rem;} .hero-grid,.executive{grid-template-columns:1fr;} .hero h1{font-size:2rem;} .hero-signal{border-left:0;border-top:1px solid rgba(216,243,240,.4);padding:1rem 0 0;} }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_number(value):
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}".replace(",", " ")


def fmt_decimal(value, digits=2):
    if pd.isna(value):
        return "-"
    return f"{value:.{digits}f}".replace(".", ",")


def priority_class(level):
    return {"Forte": "priority-strong", "Moyenne": "priority-medium", "Faible": "priority-low"}.get(str(level), "")


def interpretation(title, text, conclusion):
    st.markdown(f'<div class="interpretation"><strong>💡 Interprétation · {title}</strong><br>{text}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="conclusion"><strong>📌 Conclusion</strong><br>{conclusion}</div>', unsafe_allow_html=True)


def section(title, description):
    st.markdown(f'<div class="section-head"><h2>{title}</h2><p>{description}</p></div>', unsafe_allow_html=True)


def plot_theme(fig, height=450):
    fig.update_layout(height=height, font=dict(family="Segoe UI, sans-serif", color="#102a43"), title_font=dict(size=16, color="#102a43"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", margin=dict(l=20, r=28, t=68, b=35), hoverlabel=dict(bgcolor="#102a43", font_color="#ffffff"), legend=dict(orientation="h", y=-.18))
    fig.update_xaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    for column in data.columns:
        if column not in {"prefecture", "niveau_priorite"}:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    return data


@st.cache_data
def load_boundaries():
    boundaries = gpd.read_file(PREFECTURES_PATH)
    if "shapeName" in boundaries.columns:
        boundaries = boundaries.rename(columns={"shapeName": "prefecture"})
    return boundaries.to_crs("EPSG:4326")


@st.cache_data
def load_points(filename):
    path = PROCESSED / filename
    if not path.exists():
        return gpd.GeoDataFrame()
    data = pd.read_csv(path)
    if data.empty or "geometry" not in data.columns:
        return gpd.GeoDataFrame()
    return gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data.geometry), crs="EPSG:4326")


try:
    df = load_data()
    boundaries = load_boundaries()
except Exception as error:
    st.error(f"Impossible de charger les données: {error}")
    st.stop()


df["niveau_priorite"] = df["niveau_priorite"].astype(str)
top = df.sort_values("score_priorite", ascending=False).reset_index(drop=True)
top3 = top.head(3)
strong_count = int((df["niveau_priorite"] == "Forte").sum())
low_mm = df.nsmallest(5, "agents_mm_pour_10000_hab")

st.markdown(f'<div class="hero"><div class="hero-grid"><div><div class="eyebrow">Togo AI Lab · Économie numérique · Défi 1</div><h1>Togo Digital Access</h1><p>Intelligence territoriale pour prioriser l\'extension de la connectivité et l\'inclusion numérique au Togo.</p><span class="hero-badge">🇹🇬 Données ouvertes · Analyse spatiale · Décision publique</span></div><div class="hero-signal"><small>Signal national</small><strong>{strong_count} / {len(df)}</strong><span>préfectures en priorité forte selon le score composite</span></div></div></div>', unsafe_allow_html=True)

tabs = st.tabs(["01 · Vue nationale", "02 · Carte", "03 · Mobile Money", "04 · Réseau mobile", "05 · Infrastructures", "06 · Comparateur", "07 · Recommandations"])

with tabs[0]:
    section("Le territoire en un regard", "Comprendre le signal, les volumes et les trois premiers territoires à examiner.")
    st.markdown('<div class="panel"><h3>Objectif décisionnel</h3>Répondre à trois questions: <strong>où agir ? pourquoi agir ? que faire ?</strong> Le score combine la pression démographique, le déficit en agents Mobile Money et les antennes OpenCelliD observées.</div>', unsafe_allow_html=True)
    st.write("")
    kpi = st.columns(5)
    for column, label, value in zip(kpi, ["Population estimée", "Agents Mobile Money", "Antennes observées", "Agences télécom", "Priorités fortes"], [fmt_number(df.population_worldpop.sum()), fmt_number(df.agents_mobile_money.sum()), fmt_number(df.antennes_opencellid.sum()), fmt_number(df.agences_telecom.sum()), str(strong_count)]):
        column.metric(label, value)
    st.markdown(f'<div class="executive"><div><small>Signal prioritaire</small><strong>{top.iloc[0].prefecture} · score {fmt_decimal(top.iloc[0].score_priorite, 3)}</strong></div><div><small>Population couverte</small><strong>{fmt_number(df.population_worldpop.sum())} habitants estimés</strong></div><div><small>Cadre de lecture</small><strong>40% population · 40% Mobile Money · 20% antennes</strong></div></div>', unsafe_allow_html=True)
    section("Top 3 des préfectures prioritaires", "Le classement est calculé à partir des indicateurs réellement disponibles.")
    top3_view = top3[["rang_priorite", "prefecture", "score_priorite", "niveau_priorite", "population_worldpop", "agents_mm_pour_10000_hab", "antennes_opencellid"]].copy()
    top3_view.columns = ["Rang", "Préfecture", "Score", "Priorité", "Population", "Agents MM / 10k", "Antennes"]
    top3_view["Score"] = top3_view["Score"].round(3); top3_view["Population"] = top3_view["Population"].round(0).astype(int); top3_view["Agents MM / 10k"] = top3_view["Agents MM / 10k"].round(2)
    st.dataframe(top3_view, use_container_width=True, hide_index=True)
    interpretation("Top 3", f"{top.iloc[0].prefecture}, {top.iloc[1].prefecture} et {top.iloc[2].prefecture} arrivent en tête. {top.iloc[0].prefecture} affiche un score de {fmt_decimal(top.iloc[0].score_priorite, 3)} avec {fmt_number(top.iloc[0].agents_mobile_money)} agents Mobile Money et {int(top.iloc[0].antennes_opencellid)} antenne observée.", "Ces territoires constituent le premier périmètre de validation terrain et de ciblage opérationnel.")
    home_chart = px.bar(top.head(10).sort_values("score_priorite"), x="score_priorite", y="prefecture", orientation="h", color="niveau_priorite", title="Top 10 des scores de priorité", color_discrete_map={"Forte":"#dc2626", "Moyenne":"#f4b942", "Faible":"#16a34a"}, labels={"score_priorite":"Score", "prefecture":"Préfecture", "niveau_priorite":"Priorité"})
    st.plotly_chart(plot_theme(home_chart, 470), use_container_width=True)
    interpretation("Classement national", f"Les 10 scores affichés vont de {fmt_decimal(top.iloc[9].score_priorite, 3)} à {fmt_decimal(top.iloc[0].score_priorite, 3)}.", "Le score sert à concentrer les moyens d'analyse sur un périmètre prioritaire avant les décisions d'investissement.")

with tabs[1]:
    section("Carte territoriale de décision", "Cliquez sur une préfecture ou utilisez les filtres pour passer de la vision nationale à la fiche territoire.")
    map_col1, map_col2 = st.columns(2)
    with map_col1:
        selected_level = st.selectbox("Priorité à afficher", ["Toutes", "Forte", "Moyenne", "Faible"], key="map_level")
    with map_col2:
        selected_pref = st.selectbox("Préfecture à détailler", ["Toutes"] + sorted(df.prefecture.tolist()), key="map_pref")
    map_data = boundaries.merge(df, on="prefecture", how="left")
    if selected_level != "Toutes":
        map_data = map_data[map_data.niveau_priorite == selected_level]
    if selected_pref != "Toutes":
        map_data = map_data[map_data.prefecture == selected_pref]
    st.markdown('<div class="map-guide"><span><i style="background:#16a34a"></i> Faible</span><span><i style="background:#f4b942"></i> Moyenne</span><span><i style="background:#dc2626"></i> Forte</span><span><i style="background:#0b7285"></i> Agences</span><span><i style="background:#7c3aed"></i> Datacenters</span><span><i style="background:#dc2626"></i> Antennes observées</span></div>', unsafe_allow_html=True)
    m = folium.Map(location=[8.65, 1.15], zoom_start=7, tiles="CartoDB positron")
    colors = {"Forte":"#dc2626", "Moyenne":"#f4b942", "Faible":"#16a34a"}
    def style(feature):
        level = feature["properties"].get("niveau_priorite", "Faible")
        return {"fillColor": colors.get(level, "#16a34a"), "color":"#ffffff", "weight":1.2, "fillOpacity":.68}
    fields = ["prefecture", "population_worldpop", "agents_mobile_money", "agents_mm_pour_10000_hab", "antennes_opencellid", "score_priorite", "niveau_priorite"]
    aliases = ["Préfecture", "Population", "Agents Mobile Money", "Agents / 10 000 hab.", "Antennes observées", "Score", "Priorité"]
    folium.GeoJson(map_data.to_json(), name="Priorité par préfecture", style_function=style, tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, labels=True, sticky=False)).add_to(m)
    show_points = st.checkbox("Afficher les couches ponctuelles", value=True, key="map_points")
    if show_points:
        for name, filename, color, label in [("Agences Moov", "agences_moov.csv", "#0b7285", "Agence Moov"), ("Agences Togocom", "agences_togocom.csv", "#f4b942", "Agence Togocom"), ("Datacenters", "datacenters.csv", "#7c3aed", "Datacenter")]:
            points = load_points(filename)
            if points.empty:
                continue
            joined = gpd.sjoin(points, map_data[["prefecture", "geometry"]], how="inner", predicate="within")
            group = folium.FeatureGroup(name=name)
            for _, point in joined.iterrows():
                folium.CircleMarker([point.geometry.y, point.geometry.x], radius=5, color=color, fill=True, fill_color=color, fill_opacity=.85, tooltip=f"{label} · {point.prefecture}").add_to(group)
            group.add_to(m)
        cells = pd.read_csv(PROCESSED / "opencellid_615.csv")
        cell_group = folium.FeatureGroup(name="Antennes OpenCelliD")
        for _, cell in cells.dropna(subset=["lat", "lon"]).iterrows():
            point = gpd.GeoSeries.from_xy([cell.lon], [cell.lat], crs="EPSG:4326").iloc[0]
            if map_data.geometry.contains(point).any():
                folium.CircleMarker([cell.lat, cell.lon], radius=4, color="#dc2626", fill=True, fill_color="#dc2626", tooltip="Antenne observée · OpenCelliD").add_to(cell_group)
        cell_group.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
    legend = """<div style='position:fixed;bottom:24px;left:24px;z-index:9999;background:rgba(255,255,255,.96);padding:12px 15px;border:1px solid #d9e2ec;border-radius:6px;box-shadow:0 6px 18px rgba(16,42,67,.16);font:12px/1.7 Arial;color:#102a43'><strong>Lecture</strong><br><span style='color:#16a34a'>●</span> Faible<br><span style='color:#f4b942'>●</span> Moyenne<br><span style='color:#dc2626'>●</span> Forte<br><span style='color:#0b7285'>●</span> Agences<br><span style='color:#7c3aed'>●</span> Datacenters<br><span style='color:#dc2626'>●</span> Antennes observées</div>"""
    m.get_root().html.add_child(folium.Element(legend))
    map_event = st_folium(m, width=None, height=620, returned_objects=["last_object_clicked"])
    map_kpis = st.columns(3)
    map_kpis[0].metric("Territoires affichés", len(map_data)); map_kpis[1].metric("Population concernée", fmt_number(map_data.population_worldpop.sum())); map_kpis[2].metric("Score moyen", fmt_decimal(map_data.score_priorite.mean(), 3))
    interpretation("Carte choroplèthe", f"La carte affiche {len(map_data)} territoire(s). Les couleurs représentent le niveau de priorité; les points représentent uniquement les observations disponibles dans les sources ouvertes.", "Utiliser la carte pour localiser les territoires prioritaires, puis ouvrir leur fiche via le sélecteur.")
    clicked_pref = None
    clicked = map_event.get("last_object_clicked") if map_event else None
    if clicked and clicked.get("lat") is not None and clicked.get("lng") is not None:
        click_point = gpd.GeoSeries.from_xy([clicked["lng"]], [clicked["lat"]], crs="EPSG:4326").iloc[0]
        clicked_matches = boundaries[boundaries.geometry.contains(click_point)]
        if not clicked_matches.empty:
            clicked_pref = clicked_matches.iloc[0]["prefecture"]

    detail_pref = clicked_pref or (selected_pref if selected_pref != "Toutes" else None)
    if detail_pref:
        detail = df[df.prefecture == detail_pref].iloc[0]
        st.markdown(f'<div class="panel"><h3>Fiche · {detail_pref}</h3><strong class="{priority_class(detail.niveau_priorite)}">{detail.niveau_priorite} · score {fmt_decimal(detail.score_priorite,3)}</strong><br><br>Population: {fmt_number(detail.population_worldpop)} · Mobile Money: {fmt_decimal(detail.agents_mm_pour_10000_hab)} / 10 000 hab. · Antennes observées: {int(detail.antennes_opencellid)}<br><br><strong>Facteurs du score:</strong> population {fmt_decimal(detail.score_population,2)} · déficit Mobile Money {fmt_decimal(detail.score_deficit_mobile_money,2)} · déficit antennes {fmt_decimal(detail.score_deficit_antennes,2)}</div>', unsafe_allow_html=True)

with tabs[2]:
    section("Analyse Mobile Money", "Mesurer la disponibilité du canal de services numériques le plus décentralisé.")
    mm1, mm2, mm3 = st.columns(3); mm1.metric("Agents recensés", fmt_number(df.agents_mobile_money.sum())); mm2.metric("Moyenne agents / 10k", fmt_decimal(df.agents_mm_pour_10000_hab.mean(),2)); mm3.metric("Territoire le moins doté", low_mm.iloc[0].prefecture)
    mm_chart_data = df.nsmallest(12, "agents_mm_pour_10000_hab").sort_values("agents_mm_pour_10000_hab")
    mm_chart = px.bar(mm_chart_data, x="agents_mm_pour_10000_hab", y="prefecture", orientation="h", color="agents_mm_pour_10000_hab", color_continuous_scale=["#dc2626", "#f4b942", "#16a34a"], title="Les territoires les moins dotés en agents Mobile Money", labels={"agents_mm_pour_10000_hab":"Agents / 10 000 habitants", "prefecture":"Préfecture"})
    st.plotly_chart(plot_theme(mm_chart, 500), use_container_width=True)
    interpretation("Mobile Money", f"{low_mm.iloc[0].prefecture} est le territoire le moins doté avec {fmt_decimal(low_mm.iloc[0].agents_mm_pour_10000_hab,2)} agents pour 10 000 habitants. Les 5 territoires sous-dotés sont {', '.join(low_mm.prefecture.tolist())}.", "Le Mobile Money est un levier d'action rapide: renforcer les points dans ces territoires peut améliorer l'accès sans attendre une infrastructure lourde.")
    mm_table = low_mm[["prefecture","population_worldpop","agents_mobile_money","agents_mm_pour_10000_hab"]].copy(); mm_table.columns=["Préfecture","Population","Agents","Agents / 10k"]; mm_table["Population"]=mm_table.Population.round(0).astype(int); mm_table["Agents / 10k"]=mm_table["Agents / 10k"].round(2); st.dataframe(mm_table,use_container_width=True,hide_index=True)
    interpretation("Tableau Mobile Money", f"Le tableau met en évidence les {len(mm_table)} territoires ayant les densités les plus faibles parmi les données affichées.", "Ce tableau est le premier filtre opérationnel pour cibler une extension de réseau d'agents.")

with tabs[3]:
    section("Analyse du réseau mobile", "Identifier les territoires où les antennes sont peu ou pas observées, sans confondre donnée incomplète et absence de couverture.")
    net1, net2, net3 = st.columns(3); net1.metric("Antennes observées", fmt_number(df.antennes_opencellid.sum())); net2.metric("Préfectures à zéro observation", int((df.antennes_opencellid == 0).sum())); net3.metric("Antennes / 10k habitants", fmt_decimal(df.antennes_pour_10000_hab.mean(),3))
    network_data = df.nsmallest(15,"antennes_opencellid").sort_values("population_worldpop",ascending=False)
    net_chart = px.scatter(network_data, x="population_worldpop", y="antennes_opencellid", size="score_priorite", color="niveau_priorite", hover_name="prefecture", title="Population et antennes OpenCelliD observées", labels={"population_worldpop":"Population estimée", "antennes_opencellid":"Antennes observées", "niveau_priorite":"Priorité"}, color_discrete_map={"Forte":"#dc2626","Moyenne":"#f4b942","Faible":"#16a34a"})
    st.plotly_chart(plot_theme(net_chart, 500), use_container_width=True)
    zero_count = int((df.antennes_opencellid == 0).sum()); largest_zero = df[df.antennes_opencellid == 0].sort_values("population_worldpop", ascending=False).iloc[0]
    interpretation("Réseau mobile", f"{zero_count} préfectures ne comportent aucune antenne dans le fichier OpenCelliD. Parmi elles, {largest_zero.prefecture} est la plus peuplée avec {fmt_number(largest_zero.population_worldpop)} habitants estimés.", "Ces territoires sont des signaux de vérification prioritaire, pas une carte officielle des zones blanches.")
    st.warning("Une absence d'antenne dans OpenCelliD ne constitue pas une preuve d'absence de couverture réelle. Il s'agit d'un signal à vérifier avec les données opérateurs ou une validation terrain.")
    net_table = df.nsmallest(12,"antennes_opencellid")[["prefecture","population_worldpop","antennes_opencellid","score_priorite","niveau_priorite"]].copy(); net_table.columns=["Préfecture","Population","Antennes","Score","Priorité"]; net_table["Population"]=net_table.Population.round(0).astype(int); net_table["Score"]=net_table.Score.round(3); st.dataframe(net_table,use_container_width=True,hide_index=True)
    interpretation("Territoires à vérifier", "Le tableau ordonne les territoires selon le nombre d'antennes observées tout en conservant population et score.", "La prochaine étape est de croiser ces signaux avec les données de couverture et de qualité de service des opérateurs.")

with tabs[4]:
    section("Infrastructures et résilience", "Lire la concentration des agences et des datacenters, puis identifier les déséquilibres territoriaux.")
    infra_cols = st.columns(4); infra_cols[0].metric("Moov", fmt_number(df.agences_moov.sum())); infra_cols[1].metric("Togocom", fmt_number(df.agences_togocom.sum())); infra_cols[2].metric("CANAL+", fmt_number(df.agences_canal.sum())); infra_cols[3].metric("Datacenters", fmt_number(df.datacenters.sum()))
    agency_long = df[["prefecture","agences_moov","agences_togocom","agences_canal"]].melt("prefecture",var_name="Opérateur",value_name="Agences"); agency_long["Opérateur"] = agency_long["Opérateur"].str.replace("agences_", "", regex=False).str.title()
    agency_chart = px.bar(agency_long[agency_long.Agences > 0].sort_values("Agences",ascending=False).head(24), x="Agences", y="prefecture", color="Opérateur", orientation="h", barmode="stack", title="Agences recensées par préfecture", color_discrete_sequence=["#0b7285","#f4b942","#9ca3af"], labels={"prefecture":"Préfecture","Agences":"Nombre d'agences"})
    st.plotly_chart(plot_theme(agency_chart, 600), use_container_width=True)
    leading = df.assign(total=df.agences_moov + df.agences_togocom).sort_values("total",ascending=False).iloc[0]
    interpretation("Agences opérateurs", f"{leading.prefecture} arrive en tête avec {int(leading.total)} agences Moov/Togocom recensées. Le référentiel Télécom est agrégé et ne doit pas être additionné aux deux opérateurs.", "La présence physique est concentrée: les territoires peu équipés doivent être traités par des solutions proportionnées, en priorité Mobile Money et points de service.")
    dc = df.sort_values("datacenters",ascending=False).head(10)
    dc_chart = px.bar(dc, x="datacenters", y="prefecture", orientation="h", title="Datacenters par préfecture", color="datacenters", color_continuous_scale=["#e0e7ff","#7c3aed"], labels={"datacenters":"Datacenters","prefecture":"Préfecture"})
    st.plotly_chart(plot_theme(dc_chart, 380), use_container_width=True)
    dc_places = df[df.datacenters > 0].prefecture.tolist(); interpretation("Datacenters", f"Les {int(df.datacenters.sum())} datacenters recensés apparaissent dans {', '.join(dc_places) if dc_places else 'aucune préfecture'}.", "Une concentration géographique des capacités critiques justifie une réflexion sur la redondance hors de la région Maritime.")
    st.info("CANAL+ ne comporte aucune ligne dans l'export source disponible. Cette absence décrit la donnée fournie, pas nécessairement l'absence de service sur le terrain.")

with tabs[5]:
    section("Comparateur territorial", "Comparer deux préfectures sur les mêmes indicateurs et expliciter le choix prioritaire.")
    choices = sorted(df.prefecture.tolist()); c1, c2 = st.columns(2); pref_a = c1.selectbox("Préfecture A", choices, index=choices.index(top.iloc[0].prefecture), key="compare_a"); pref_b = c2.selectbox("Préfecture B", choices, index=choices.index(top.iloc[1].prefecture), key="compare_b")
    a = df[df.prefecture == pref_a].iloc[0]; b = df[df.prefecture == pref_b].iloc[0]
    compare = pd.DataFrame({"Indicateur":["Population","Agents Mobile Money","Agents MM / 10k","Agences Moov + Togocom","Antennes observées","Score priorité"], pref_a:[a.population_worldpop,a.agents_mobile_money,a.agents_mm_pour_10000_hab,a.agences_moov+a.agences_togocom,a.antennes_opencellid,a.score_priorite], pref_b:[b.population_worldpop,b.agents_mobile_money,b.agents_mm_pour_10000_hab,b.agences_moov+b.agences_togocom,b.antennes_opencellid,b.score_priorite]})
    compare_view = compare.copy(); compare_view[pref_a] = compare_view[pref_a].round(2); compare_view[pref_b] = compare_view[pref_b].round(2); st.dataframe(compare_view,use_container_width=True,hide_index=True)
    compare_long = compare.melt("Indicateur",var_name="Préfecture",value_name="Valeur"); compare_chart = px.bar(compare_long[compare_long.Indicateur.isin(["Agents MM / 10k","Antennes observées","Score priorité"])], x="Indicateur", y="Valeur", color="Préfecture", barmode="group", title="Comparaison des indicateurs de déficit", color_discrete_sequence=["#0b7285","#f4b942"]); st.plotly_chart(plot_theme(compare_chart,400),use_container_width=True)
    winner = a if a.score_priorite >= b.score_priorite else b; other = b if winner.prefecture == a.prefecture else a
    interpretation("Comparaison", f"{winner.prefecture} est plus prioritaire que {other.prefecture} avec un score de {fmt_decimal(winner.score_priorite,3)} contre {fmt_decimal(other.score_priorite,3)}. Son déficit Mobile Money vaut {fmt_decimal(winner.score_deficit_mobile_money,2)} et son déficit d'antennes {fmt_decimal(winner.score_deficit_antennes,2)}.", f"Pour départager les deux territoires, commencer par {winner.prefecture}: son score est supérieur selon la règle des 40% population, 40% Mobile Money et 20% antennes.")

with tabs[6]:
    section("Recommandations opérationnelles", "Transformer le diagnostic en décisions concrètes, avec une preuve et une action pour chaque territoire.")
    st.markdown('<div class="method"><strong>Règle de décision:</strong> le score = 40% pression démographique + 40% déficit Mobile Money + 20% déficit d’antennes. Les facteurs sont normalisés entre 0 et 1. Les recommandations restent à confirmer par les opérateurs et le terrain.</div>', unsafe_allow_html=True)
    st.write("")
    for _, row in top.head(5).iterrows():
        mm_problem = f"densité Mobile Money faible ({fmt_decimal(row.agents_mm_pour_10000_hab)} agents / 10 000 habitants)" if row.agents_mm_pour_10000_hab < df.agents_mm_pour_10000_hab.mean() else "densité Mobile Money supérieure à la moyenne nationale"
        cell_problem = "aucune antenne observée dans OpenCelliD" if row.antennes_opencellid == 0 else f"{int(row.antennes_opencellid)} antenne(s) observée(s) dans OpenCelliD"
        with st.container(border=True):
            st.markdown(f"### {int(row.rang_priorite)} · {row.prefecture}  <span class='{priority_class(row.niveau_priorite)}'>{row.niveau_priorite}</span>", unsafe_allow_html=True)
            st.write(f"**Problème:** {mm_problem}; {cell_problem}. **Preuve:** score {fmt_decimal(row.score_priorite,3)}, population estimée {fmt_number(row.population_worldpop)}, facteurs population {fmt_decimal(row.score_population,2)}, Mobile Money {fmt_decimal(row.score_deficit_mobile_money,2)}, antennes {fmt_decimal(row.score_deficit_antennes,2)}.")
            actions = []
            if row.agents_mm_pour_10000_hab < df.agents_mm_pour_10000_hab.mean(): actions.append("Mobile Money: densifier les agents et points de service")
            if row.antennes_opencellid == 0: actions.append("Connectivité: vérifier la couverture opérateur et prioriser une étude radio")
            if row.agences_moov + row.agences_togocom == 0: actions.append("Infrastructures: étudier un point de présence partagé ou mutualisé")
            actions.append("Gouvernance: valider par une mission terrain avant investissement")
            st.write("**Action proposée:** " + "; ".join(actions) + ".")
    with st.expander("Méthodologie, sources et limites", expanded=True):
        st.markdown("**Sources:** WorldPop 2020, OpenCelliD, agences et datacenters issus des données ouvertes, limites administratives GeoJSON. **Unités:** population en habitants estimés; agents et agences en nombre de points; densités en points pour 10 000 habitants; score entre 0 et 1. **Limite OpenCelliD:** une absence d'antenne dans OpenCelliD ne constitue pas une preuve d'absence de couverture réelle. Il s'agit d'un signal à vérifier avec les données opérateurs ou une validation terrain. **Limite générale:** le score est un outil de présélection, pas une mesure absolue de couverture.")

st.markdown('<div style="border-top:1px solid #d9e2ec;margin-top:2.5rem;padding-top:1rem;color:#58708a;text-align:center;font-size:.82rem">Togo Digital Access · Intelligence territoriale · Données ouvertes · Python · Streamlit · GeoPandas · Folium · Plotly</div>', unsafe_allow_html=True)
