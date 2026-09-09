
import pandas as pd
import numpy as np


def normaliser_directe(series):
    """Normalise une série entre 0 et 1."""
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0, index=series.index)

    return (series - minimum) / (maximum - minimum)


def normaliser_inverse(series):
    """Normalise inversement : faible valeur = score élevé."""
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0, index=series.index)

    return 1 - (series - minimum) / (maximum - minimum)


def calculer_indicateurs(df):
    """Calcule les indicateurs utiles au dashboard."""

    df = df.copy()

    # Population
    df["population_worldpop"] = df["population_worldpop"].fillna(0)

    # Agents Mobile Money pour 10 000 habitants
    df["agents_mm_pour_10000_hab"] = np.where(
        df["population_worldpop"] > 0,
        df["agents_mobile_money"]
        / df["population_worldpop"]
        * 10000,
        0,
    )

    # Agences télécom
    df["agences_telecom_total"] = (
        df["agences_moov"]
        + df["agences_togocom"]
        + df["agences_telecom"]
        + df["agences_canal"]
    )

    # Agences télécom pour 10 000 habitants
    df["agences_pour_10000_hab"] = np.where(
        df["population_worldpop"] > 0,
        df["agences_telecom_total"]
        / df["population_worldpop"]
        * 10000,
        0,
    )

    # Antennes pour 10 000 habitants
    df["antennes_pour_10000_hab"] = np.where(
        df["population_worldpop"] > 0,
        df["antennes_opencellid"]
        / df["population_worldpop"]
        * 10000,
        0,
    )

    # Score population
    df["score_population"] = normaliser_directe(
        np.log1p(df["population_worldpop"])
    )

    # Score déficit Mobile Money
    df["score_deficit_mobile_money"] = normaliser_inverse(
        df["agents_mm_pour_10000_hab"]
    )

    # Score déficit antennes
    df["score_deficit_antennes"] = normaliser_inverse(
        df["antennes_opencellid"]
    )

    # Score global
    df["score_priorite"] = (
        0.40 * df["score_population"]
        + 0.40 * df["score_deficit_mobile_money"]
        + 0.20 * df["score_deficit_antennes"]
    )

    return df