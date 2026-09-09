
from pathlib import Path
import gzip
import shutil

import pandas as pd
import geopandas as gpd
import rasterio


# ============================================================
# CONFIGURATION
# ============================================================

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

PROCESSED.mkdir(parents=True, exist_ok=True)


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def clean_text_columns(df):
    """Nettoie les colonnes texte."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip()

    return df


def clean_csv(filename):
    """Lit et nettoie un fichier CSV."""
    path = RAW / filename

    print(f"\nLecture : {filename}")

    df = pd.read_csv(path)

    # Nettoyage des espaces
    df = clean_text_columns(df)

    # Suppression des doublons exacts
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    print(f"  Lignes initiales : {before:,}")
    print(f"  Doublons supprimés : {before - after:,}")
    print(f"  Lignes finales : {after:,}")

    # Sauvegarde
    output = PROCESSED / filename
    df.to_csv(output, index=False, encoding="utf-8-sig")

    print(f"  → Sauvegardé : {output}")

    return df


# ============================================================
# 1. AGENCES
# ============================================================

print("=" * 70)
print("NETTOYAGE DES DONNÉES — DÉFI 1 ÉCONOMIE NUMÉRIQUE")
print("=" * 70)

agences_files = [
    "agences_canal.csv",
    "agences_moov.csv",
    "agences_telecom.csv",
    "agences_togocom.csv",
]

agences = {}

for filename in agences_files:
    agences[filename] = clean_csv(filename)


# ============================================================
# 2. AGENTS MOBILE MONEY
# ============================================================

print("\n" + "=" * 70)
print("AGENTS MOBILE MONEY")
print("=" * 70)

agents_mobile_money = clean_csv("agents_mobile_money.csv")


# ============================================================
# 3. DATACENTERS
# ============================================================

print("\n" + "=" * 70)
print("DATACENTERS")
print("=" * 70)

datacenters = clean_csv("datacenters.csv")


# ============================================================
# 4. OPEN CELL ID
# ============================================================

print("\n" + "=" * 70)
print("OPEN CELL ID")
print("=" * 70)

opencellid_gz = RAW / "opencellid_615.csv.gz"
opencellid_csv = PROCESSED / "opencellid_615.csv"

if opencellid_gz.exists():

    # Décompression sans modifier le fichier original
    with gzip.open(opencellid_gz, "rb") as source:
        with open(opencellid_csv, "wb") as destination:
            shutil.copyfileobj(source, destination)

    print(f"Fichier décompressé : {opencellid_csv}")

    # OpenCelliD n'a pas de ligne d'en-tête dans notre fichier.
    # On lit donc d'abord sans header pour inspecter la structure.
    opencellid = pd.read_csv(
        opencellid_csv,
        header=None
    )

    print(f"Lignes : {len(opencellid):,}")
    print(f"Colonnes : {len(opencellid.columns)}")

    print("\nPremière ligne :")
    print(opencellid.iloc[0].tolist())

    # Noms standards OpenCelliD
    opencellid_columns = [
        "radio",
        "mcc",
        "mnc",
        "area",
        "cell",
        "unit",
        "lon",
        "lat",
        "range",
        "samples",
        "changeable",
        "created",
        "updated",
        "average_signal",
    ]

    if len(opencellid.columns) == len(opencellid_columns):
        opencellid.columns = opencellid_columns

    # Conversion numérique
    numeric_columns = [
        "mcc",
        "mnc",
        "area",
        "cell",
        "unit",
        "lon",
        "lat",
        "range",
        "samples",
        "changeable",
        "created",
        "updated",
        "average_signal",
    ]

    for col in numeric_columns:
        opencellid[col] = pd.to_numeric(
            opencellid[col],
            errors="coerce"
        )

    # Garder uniquement les coordonnées valides
    opencellid = opencellid[
        opencellid["lon"].between(-180, 180)
        & opencellid["lat"].between(-90, 90)
    ].copy()

    opencellid.to_csv(
        opencellid_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nLignes après nettoyage : {len(opencellid):,}")
    print(f"Colonnes finales : {list(opencellid.columns)}")

else:
    print("ERREUR : fichier OpenCelliD introuvable.")


# ============================================================
# 5. PRÉFECTURES ADM2
# ============================================================

print("\n" + "=" * 70)
print("PRÉFECTURES ADM2")
print("=" * 70)

geojson = RAW / "prefectures_adm2.geojson"

if geojson.exists():

    prefectures = gpd.read_file(geojson)

    print(f"Nombre de préfectures : {len(prefectures)}")
    print(f"CRS original : {prefectures.crs}")

    # On travaille en WGS84 pour les cartes
    prefectures = prefectures.to_crs("EPSG:4326")

    # Vérification des géométries
    invalid_before = (~prefectures.geometry.is_valid).sum()

    if invalid_before > 0:
        prefectures.geometry = prefectures.geometry.make_valid()

    invalid_after = (~prefectures.geometry.is_valid).sum()

    print(f"Géométries invalides avant : {invalid_before}")
    print(f"Géométries invalides après : {invalid_after}")

    # Sauvegarde GeoJSON
    output_geojson = PROCESSED / "prefectures_adm2.geojson"

    prefectures.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    print(f"→ Sauvegardé : {output_geojson}")

    # Copie tabulaire utile pour les analyses
    prefectures_table = prefectures.drop(
        columns="geometry"
    )

    prefectures_table.to_csv(
        PROCESSED / "prefectures_adm2.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("→ Table attributaire sauvegardée.")


# ============================================================
# 6. WORLDPOP
# ============================================================

print("\n" + "=" * 70)
print("WORLDPOP")
print("=" * 70)

worldpop = RAW / "population_worldpop.tif"

if worldpop.exists():

    with rasterio.open(worldpop) as src:

        print(f"CRS : {src.crs}")
        print(f"Dimensions : {src.width} x {src.height}")
        print(f"Résolution : {src.res}")
        print(f"Nombre de bandes : {src.count}")
        print(f"Bounds : {src.bounds}")

    # Le raster original reste dans data/raw.
    # Nous ne le modifions pas.

    print("→ Raster original conservé dans data/raw.")


# ============================================================
# FIN
# ============================================================

print("\n" + "=" * 70)
print("NETTOYAGE TERMINÉ")
print("=" * 70)

print("\nFichiers produits dans data/processed :")

for file in sorted(PROCESSED.iterdir()):
    print(f"  - {file.name}")

print("\nProchaine étape : analyse géospatiale et calcul des indicateurs.")