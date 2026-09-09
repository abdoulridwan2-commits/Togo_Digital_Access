from pathlib import Path

import pandas as pd
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
RAW = BASE_DIR / "data" / "raw"
PROCESSED = BASE_DIR / "data" / "processed"

OUTPUT = PROCESSED / "indicateurs_prefectures.csv"


# ============================================================
# 1. CHARGEMENT DES PRÉFECTURES
# ============================================================

print("=" * 70)
print("ANALYSE GÉOSPATIALE — DÉFI 1")
print("=" * 70)

print("\n1. Chargement des préfectures...")

prefectures = gpd.read_file(
    PROCESSED / "prefectures_adm2.geojson"
)

prefectures = prefectures.to_crs("EPSG:4326")

# Nom standard utilisé dans nos analyses
prefectures["prefecture"] = prefectures["shapeName"].astype(str).str.strip()

print(f"Préfectures chargées : {len(prefectures)}")


# ============================================================
# 2. POPULATION WORLDPOP
# ============================================================

print("\n2. Calcul de la population par préfecture...")

worldpop = RAW / "population_worldpop.tif"

with rasterio.open(worldpop) as src:
    raster_crs = src.crs

print(f"CRS WorldPop : {raster_crs}")

# Les deux données sont en WGS84
prefectures_raster = prefectures.to_crs(raster_crs)

stats = zonal_stats(
    prefectures_raster,
    str(worldpop),
    stats=["sum", "mean"],
    nodata=None
)

prefectures["population_worldpop"] = [
    s["sum"] if s["sum"] is not None else 0
    for s in stats
]

prefectures["densite_worldpop_moyenne"] = [
    s["mean"] if s["mean"] is not None else 0
    for s in stats
]

print(
    "Population totale estimée : "
    f"{prefectures['population_worldpop'].sum():,.0f}"
)


# ============================================================
# 3. SUPERFICIE
# ============================================================

print("\n3. Calcul de la superficie...")

# Projection métrique adaptée à l'Afrique de l'Ouest
prefectures_metric = prefectures.to_crs("EPSG:32631")

prefectures["superficie_km2"] = (
    prefectures_metric.geometry.area / 1_000_000
)

prefectures["densite_calculee"] = (
    prefectures["population_worldpop"]
    / prefectures["superficie_km2"]
)


# ============================================================
# 4. FONCTION DE JOINTURE SPATIALE
# ============================================================

def compter_points_par_prefecture(
    filename,
    nom_indicateur,
):
    """
    Compte les points de chaque fichier dans chaque préfecture.
    """

    path = RAW / filename

    df = pd.read_csv(path)

    if len(df) == 0:
        print(f"  {filename} : aucune donnée")

        prefectures[nom_indicateur] = 0

        return

    points = gpd.GeoDataFrame(
        df,
        geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
        crs="EPSG:4326",
    )

    # Jointure spatiale
    joined = gpd.sjoin(
        points,
        prefectures[["prefecture", "geometry"]],
        how="left",
        predicate="within",
    )

    counts = (
        joined["prefecture"]
        .value_counts()
        .rename(nom_indicateur)
    )

    prefectures[nom_indicateur] = (
        prefectures["prefecture"]
        .map(counts)
        .fillna(0)
        .astype(int)
    )

    print(
        f"  {filename} : "
        f"{len(points):,} points → "
        f"{prefectures[nom_indicateur].sum():,} affectés"
    )


# ============================================================
# 5. AGENTS MOBILE MONEY
# ============================================================

print("\n4. Agents Mobile Money...")

compter_points_par_prefecture(
    "agents_mobile_money.csv",
    "agents_mobile_money",
)


# ============================================================
# 6. AGENCES
# ============================================================

print("\n5. Agences...")

compter_points_par_prefecture(
    "agences_moov.csv",
    "agences_moov",
)

compter_points_par_prefecture(
    "agences_togocom.csv",
    "agences_togocom",
)

compter_points_par_prefecture(
    "agences_telecom.csv",
    "agences_telecom",
)

compter_points_par_prefecture(
    "agences_canal.csv",
    "agences_canal",
)


# ============================================================
# 7. DATACENTERS
# ============================================================

print("\n6. Datacenters...")

compter_points_par_prefecture(
    "datacenters.csv",
    "datacenters",
)


# ============================================================
# 8. ANTENNES OPENCELLID
# ============================================================

print("\n7. Antennes OpenCelliD...")

opencellid = pd.read_csv(
    PROCESSED / "opencellid_615.csv"
)

opencellid_points = gpd.GeoDataFrame(
    opencellid,
    geometry=gpd.points_from_xy(
        opencellid["lon"],
        opencellid["lat"],
    ),
    crs="EPSG:4326",
)

joined_antennes = gpd.sjoin(
    opencellid_points,
    prefectures[["prefecture", "geometry"]],
    how="left",
    predicate="within",
)

antenna_counts = (
    joined_antennes["prefecture"]
    .value_counts()
    .rename("antennes_opencellid")
)

prefectures["antennes_opencellid"] = (
    prefectures["prefecture"]
    .map(antenna_counts)
    .fillna(0)
    .astype(int)
)

print(
    "Antennes OpenCelliD : "
    f"{len(opencellid_points):,}"
)

print(
    "Antennes affectées à une préfecture : "
    f"{prefectures['antennes_opencellid'].sum():,}"
)


# ============================================================
# 9. INDICATEURS DE COUVERTURE
# ============================================================

print("\n8. Calcul des indicateurs...")

prefectures["agents_mm_pour_10000_hab"] = (
    prefectures["agents_mobile_money"]
    / prefectures["population_worldpop"].replace(0, pd.NA)
    * 10_000
)

prefectures["antennes_pour_10000_hab"] = (
    prefectures["antennes_opencellid"]
    / prefectures["population_worldpop"].replace(0, pd.NA)
    * 10_000
)

# IMPORTANT : "agences_telecom.csv" (le dataset "Agences - Télécom" du
# geoportail) est l'union exacte de agences_moov + agences_togocom
# (vérifié : mêmes géométries). Il ne faut donc PAS le sommer avec
# agences_moov/agences_togocom sous peine de compter chaque agence 2 fois.
prefectures["agences_telecom_total"] = (
    prefectures["agences_telecom"]
    + prefectures["agences_canal"]
)



# ============================================================
# 10. EXPORT
# ============================================================

colonnes = [
    "prefecture",
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
]

resultat = prefectures[colonnes].copy()

resultat = resultat.sort_values(
    "population_worldpop",
    ascending=False,
)

resultat.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig",
)

print("\n" + "=" * 70)
print("ANALYSE TERMINÉE")
print("=" * 70)

print(f"\nFichier créé : {OUTPUT}")

print("\nAperçu :")
print(
    resultat.head(10).to_string(index=False)
)

print("\nTotaux :")
print(
    resultat[
        [
            "population_worldpop",
            "agents_mobile_money",
            "agences_telecom_total",
            "datacenters",
            "antennes_opencellid",
        ]
    ].sum()
)

print("\nProchaine étape : validation des indicateurs.")