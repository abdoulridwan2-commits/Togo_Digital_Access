from pathlib import Path
import pandas as pd
import geopandas as gpd
import rasterio

BASE_DIR = Path(__file__).resolve().parents[1]
RAW = BASE_DIR / "data" / "raw"

print("=" * 60)
print("VÉRIFICATION DES DONNÉES DU DÉFI 1")
print("=" * 60)


# --------------------------------------------------
# 1. Fichiers attendus
# --------------------------------------------------

files = [
    "agences_canal.csv",
    "agences_moov.csv",
    "agences_telecom.csv",
    "agences_togocom.csv",
    "agents_mobile_money.csv",
    "datacenters.csv",
    "opencellid_615.csv.gz",
    "population_worldpop.tif",
    "prefectures_adm2.geojson",
]

print("\n1. PRÉSENCE DES FICHIERS")
print("-" * 40)

for filename in files:
    path = RAW / filename

    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"OK  {filename} ({size_kb:.1f} Ko)")
    else:
        print(f"MANQUANT  {filename}")


# --------------------------------------------------
# 2. Vérification des CSV
# --------------------------------------------------

csv_files = [
    "agences_canal.csv",
    "agences_moov.csv",
    "agences_telecom.csv",
    "agences_togocom.csv",
    "agents_mobile_money.csv",
    "datacenters.csv",
]

print("\n2. VÉRIFICATION DES CSV")
print("-" * 40)

for filename in csv_files:
    path = RAW / filename

    if not path.exists():
        continue

    try:
        df = pd.read_csv(path)

        print(f"\n{filename}")
        print(f"  Lignes   : {len(df):,}")
        print(f"  Colonnes : {len(df.columns)}")
        print(f"  Doublons : {df.duplicated().sum():,}")
        print(f"  Colonnes : {list(df.columns)}")

    except Exception as e:
        print(f"  ERREUR : {e}")


# --------------------------------------------------
# 3. OpenCelliD
# --------------------------------------------------

print("\n3. VÉRIFICATION OPEN CELL ID")
print("-" * 40)

opencellid = RAW / "opencellid_615.csv.gz"

if opencellid.exists():
    try:
        df = pd.read_csv(opencellid, compression="gzip")

        print(f"Lignes   : {len(df):,}")
        print(f"Colonnes : {len(df.columns)}")
        print(f"Colonnes : {list(df.columns)}")

    except Exception as e:
        print(f"ERREUR : {e}")


# --------------------------------------------------
# 4. GeoJSON des préfectures
# --------------------------------------------------

print("\n4. VÉRIFICATION GEOJSON")
print("-" * 40)

geojson = RAW / "prefectures_adm2.geojson"

if geojson.exists():
    try:
        gdf = gpd.read_file(geojson)

        print(f"Préfectures : {len(gdf)}")
        print(f"CRS         : {gdf.crs}")
        print(f"Colonnes    : {list(gdf.columns)}")
        print(f"Géométries valides : {gdf.geometry.is_valid.sum()}/{len(gdf)}")

    except Exception as e:
        print(f"ERREUR : {e}")


# --------------------------------------------------
# 5. Raster WorldPop
# --------------------------------------------------

print("\n5. VÉRIFICATION WORLDPOP")
print("-" * 40)

raster = RAW / "population_worldpop.tif"

if raster.exists():
    try:
        with rasterio.open(raster) as src:
            print(f"CRS         : {src.crs}")
            print(f"Largeur     : {src.width}")
            print(f"Hauteur     : {src.height}")
            print(f"Nombre bands: {src.count}")
            print(f"Résolution  : {src.res}")
            print(f"Bounds      : {src.bounds}")

    except Exception as e:
        print(f"ERREUR : {e}")


print("\n" + "=" * 60)
print("VÉRIFICATION TERMINÉE")
print("=" * 60)