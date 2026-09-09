import pandas as pd
import geopandas as gpd


PREFECTURES = "data/processed/prefectures_adm2.geojson"

def charger_prefectures():
    """Charge les limites administratives des préfectures."""
    prefectures = gpd.read_file(PREFECTURES)

    if prefectures.crs is None:
        prefectures = prefectures.set_crs("EPSG:4326")

    # Standardisation du nom de la préfecture
    prefectures = prefectures.rename(
        columns={"shapeName": "prefecture"}
    )

    return prefectures

def charger_points(csv_path):
    """Charge un fichier CSV contenant soit une géométrie WKT,
    soit des coordonnées lon/lat.
    """
    df = pd.read_csv(csv_path)

    # Cas 1 : fichiers avec géométrie WKT
    if "geometry" in df.columns:
        points = gpd.GeoDataFrame(
            df,
            geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
            crs="EPSG:4326",
        )
        return points

    # Cas 2 : OpenCelliD avec lon/lat
    if "lon" in df.columns and "lat" in df.columns:
        points = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["lon"], df["lat"]),
            crs="EPSG:4326",
        )
        return points

    raise ValueError(
        f"Impossible de créer la géométrie pour {csv_path}. "
        "Colonnes 'geometry' ou 'lon'/'lat' absentes."
    )


def joindre_aux_prefectures(points, prefectures):
    """Associe chaque point à sa préfecture."""
    points = points.to_crs(prefectures.crs)

    resultat = gpd.sjoin(
        points,
        prefectures[["prefecture", "geometry"]],
        how="left",
        predicate="within",
    )

    return resultat


def compter_points_par_prefecture(
    csv_path,
    prefectures=None,
    nom_indicateur="nombre_points",
):
    """
    Compte les points géographiques par préfecture.
    """

    if prefectures is None:
        prefectures = charger_prefectures()

    points = charger_points(csv_path)

    joints = joindre_aux_prefectures(
        points,
        prefectures,
    )

    comptes = (
        joints["prefecture"]
        .value_counts()
        .rename_axis("prefecture")
        .reset_index(name=nom_indicateur)
    )

    return comptes


def ajouter_comptage_spatial(
    prefectures,
    csv_path,
    nom_indicateur,
):
    """
    Ajoute directement le nombre de points à la couche des préfectures.
    """

    comptes = compter_points_par_prefecture(
        csv_path,
        prefectures,
        nom_indicateur,
    )

    resultat = prefectures.merge(
        comptes,
        on="prefecture",
        how="left",
    )

    resultat[nom_indicateur] = (
        resultat[nom_indicateur]
        .fillna(0)
        .astype(int)
    )

    return resultat


def preparer_couche_mobile_money():
    """Prépare la couche géographique Mobile Money."""

    prefectures = charger_prefectures()

    return ajouter_comptage_spatial(
        prefectures,
        "data/processed/agents_mobile_money.csv",
        "agents_mobile_money",
    )


def preparer_couche_antennes():
    """Prépare la couche géographique des antennes."""

    prefectures = charger_prefectures()

    return ajouter_comptage_spatial(
        prefectures,
        "data/processed/opencellid_615.csv",
        "antennes_opencellid",
    )


def preparer_couche_agences():
    """Prépare la couche géographique des agences télécom."""

    prefectures = charger_prefectures()

    fichiers = {
        "agences_moov": "data/processed/agences_moov.csv",
        "agences_togocom": "data/processed/agences_togocom.csv",
        "agences_telecom": "data/processed/agences_telecom.csv",
        "agences_canal": "data/processed/agences_canal.csv",
    }

    resultat = prefectures.copy()

    for indicateur, fichier in fichiers.items():

        if not pd.io.common.file_exists(fichier):
            resultat[indicateur] = 0
            continue

        comptes = compter_points_par_prefecture(
            fichier,
            prefectures,
            indicateur,
        )

        resultat = resultat.merge(
            comptes,
            on="prefecture",
            how="left",
        )

        resultat[indicateur] = (
            resultat[indicateur]
            .fillna(0)
            .astype(int)
        )

    return resultat