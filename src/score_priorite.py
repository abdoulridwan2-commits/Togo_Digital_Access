import pandas as pd
import numpy as np


INPUT = "data/processed/indicateurs_prefectures.csv"
OUTPUT = "data/processed/priorites_prefectures.csv"


def normaliser_inverse(series):
    """0 = meilleure situation, 1 = situation la plus défavorable."""
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0, index=series.index)

    return 1 - (series - minimum) / (maximum - minimum)


def normaliser_directe(series):
    """0 = valeur faible, 1 = valeur élevée."""
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0, index=series.index)

    return (series - minimum) / (maximum - minimum)


def main():
    df = pd.read_csv(INPUT)

    # Population : plus elle est élevée, plus le besoin potentiel est important.
    df["score_population"] = normaliser_directe(
        np.log1p(df["population_worldpop"])
    )

    # Mobile Money : moins il y a d'agents pour 10 000 habitants,
    # plus le déficit potentiel est important.
    df["score_deficit_mobile_money"] = normaliser_inverse(
        df["agents_mm_pour_10000_hab"]
    )

    # OpenCelliD : moins il y a d'antennes recensées,
    # plus le déficit potentiel est important.
    df["score_deficit_antennes"] = normaliser_inverse(
        df["antennes_opencellid"]
    )

    # Score global
    df["score_priorite"] = (
        0.40 * df["score_population"]
        + 0.40 * df["score_deficit_mobile_money"]
        + 0.20 * df["score_deficit_antennes"]
    )

    # Classement
    df = df.sort_values(
        "score_priorite",
        ascending=False
    ).reset_index(drop=True)

    df["rang_priorite"] = df.index + 1

    # Catégorie de priorité
    df["niveau_priorite"] = pd.cut(
        df["score_priorite"],
        bins=[-np.inf, 0.33, 0.66, np.inf],
        labels=["Faible", "Moyenne", "Forte"]
    )

    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print("\n=== TOP 10 DES PRIORITÉS ===\n")

    colonnes = [
        "rang_priorite",
        "prefecture",
        "population_worldpop",
        "agents_mobile_money",
        "agents_mm_pour_10000_hab",
        "antennes_opencellid",
        "score_priorite",
        "niveau_priorite",
    ]

    print(
        df[colonnes]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nFichier créé : {OUTPUT}")


if __name__ == "__main__":
    main()