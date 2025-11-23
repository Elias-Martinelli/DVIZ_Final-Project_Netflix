"""This module handles all the data processing parts """
import pandas as pd
import country_converter as coco

from config import DATA_DIR


def load_netflixdata(input_file : str = DATA_DIR / 'netflix1.csv'):
    """Loads the inputdata and transforms the columns in auseful format.

    Args:
        input_file (str, optional): Path to input csv. Defaults to '../data/netflix1.csv'.

    Returns:
        pd.DataFrame : The Netflixdata ready to plot.
    """
    df_netflix = pd.read_csv(input_file,
                            parse_dates=['date_added'],
                            dtype={'release_year':'Int64'})

    df_netflix = (
        df_netflix
        .pipe(add_extracted_durations)
        .pipe(add_rating_translations)
        .pipe(add_iso3_countrynames)
        .assign(genres_list=lambda df: df['listed_in'].str.split(", "))
    )

    return df_netflix

def add_extracted_durations(df : pd.DataFrame) -> pd.DataFrame:
    """Convert "Duration" into Seasons and Minutes (movies are in min, TV-Shows
    in Seasons)
    """
    df["duration_minutes"] = df["duration"].str.extract(
        r"(\d+)\s*min",expand=False).astype("Int64")
    df["seasons"] = df["duration"].str.extract(
        r"(\d+)\s*Season", expand=False).astype("Int64")
    return df

def add_rating_translations(df : pd.DataFrame) -> pd.DataFrame:
    """ Adds the rating features for Age and its description"""
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

    # Add rating columns
    df["rating_description"] = df["rating"].map(
        lambda x: rating_map.get(x, ("Unbekannt", None))[0])
    df["rating_age"] = df["rating"].map(lambda x: rating_map.get(
        x, ("Unbekannt", None))[1])
    return df


def add_iso3_countrynames(df : pd.DataFrame) -> pd.DataFrame:
    """Adds the ISO3-Countrycodes for choroplet Worldmap"""
    # Correct problematic country-entries first
    pre_mapping = {
        "Soviet Union": "Russia",
        "West Germany": "Germany",
        'Not Given' : None
    }

    df['country_clean'] = df['country'].replace(pre_mapping)
    valid_countries = df['country_clean'].dropna().unique()
    iso3_mapping = dict(zip(
        valid_countries,
        coco.convert(names=valid_countries, to='ISO3', not_found=None)
    ))

    df['ISO3_country'] = df['country_clean'].map(iso3_mapping)
    df.drop(columns=['country_clean'])

    return df
