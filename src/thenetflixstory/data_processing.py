"""This module handles all the data processing parts """
import pandas as pd


def load_netflixdata(input_file : str = '../data/netflix1.csv'):
    """Loads the inputdata and transforms the columns in auseful format.

    Args:
        input_file (str, optional): Path to input csv. Defaults to '../data/netflix1.csv'.

    Returns:
        pd.DataFrame : The Netflixdata ready to plot.
    """
    df_netflix = pd.read_csv(input_file,
                            parse_dates=['date_added'],
                            dtype={'release_year':'Int64'})

    # Convert "Duration" into Seasons and Minutes (movies are in min, TV-Shows in Seasons)
    df_netflix["duration_minutes"] = df_netflix["duration"].str.extract(
        r"(\d+)\s*min",expand=False).astype("Int64")
    df_netflix["seasons"] = df_netflix["duration"].str.extract(
        r"(\d+)\s*Season", expand=False).astype("Int64")

    # Translate Ratigns
    rating_map = {
        "G": ("General Audience – alle Altersgruppen geeignet", 0),
        "PG": ("Elterliche Aufsicht empfohlen", 8),
        "PG-13": ("Ab 13 Jahren, elterliche Begleitung empfohlen", 13),
        "R": ("Ab 17, nur mit Eltern erlaubt", 17),
        "NC-17": ("Nur Erwachsene, keine Zuschauer unter 18", 18),
        "TV-Y": ("Geeignet für Kleinkinder (0–6)", 0),
        "TV-Y7": ("Ab 7 Jahren", 7),
        "TV-Y7-FV": ("Ab 7 Jahren (Fantasy Violence)", 7),
        "TV-G": ("Allgemein geeignet", 0),
        "TV-PG": ("Elterliche Aufsicht empfohlen (ab ca. 10)", 10),
        "TV-14": ("Ab 14 Jahren", 14),
        "TV-MA": ("Nur für Erwachsene (ab 17)", 17),
        "NR": ("Nicht bewertet", None),
        "UR": ("Unrated / Nicht bewertet", None),
    }

    # Add columns
    df_netflix["rating_description"] = df_netflix["rating"].map(
        lambda x: rating_map.get(x, ("Unbekannt", None))[0])
    df_netflix["rating_age"] = df_netflix["rating"].map(lambda x: rating_map.get(
        x, ("Unbekannt", None))[1])

    # Liste trennen
    df_netflix["genres_list"] = df_netflix["listed_in"].str.split(", ")
    # Every Genre-Combination in an own row
    df_exploded = df_netflix.explode("genres_list")

    return df_netflix, df_exploded
