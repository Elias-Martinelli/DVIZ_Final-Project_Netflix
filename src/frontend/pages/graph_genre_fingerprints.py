"""Plotly graph builder for Netflix-style genre fingerprints."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


FONT_STACK = "Netflix Sans,Helvetica Neue,Segoe UI,Roboto,Ubuntu,sans-serif"

# Netflix-ish theme
BG = "#141414"
PANEL = "#1E1E1E"
GRID = "#2A2A2A"
TEXT = "#F5F5F1"
SUBTEXT = "#B3B3B3"
NETFLIX_RED = "#E50914"
NEG = "#6E6E6E"
AXIS = "#3A3A3A"


def _split_list(x) -> list[str]:
    if pd.isna(x):
        return []
    return [t.strip() for t in str(x).split(",") if t.strip()]


def _ensure_lists(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures:
    - show_id (fallback to index)
    - countries_list (from 'country')
    - genres_list (from 'genres_list' or parsed from 'listed_in')
    """
    df = df.copy()

    if "show_id" not in df.columns:
        df = df.reset_index().rename(columns={"index": "show_id"})

    if "countries_list" not in df.columns:
        if "country" not in df.columns:
            raise ValueError("Missing 'country' column (or provide 'countries_list').")
        df["countries_list"] = df["country"].apply(_split_list)

    if "genres_list" not in df.columns:
        if "listed_in" not in df.columns:
            raise ValueError("Missing 'listed_in' column (or provide 'genres_list').")
        df["genres_list"] = df["listed_in"].apply(_split_list)

    # make sure lists
    df["countries_list"] = df["countries_list"].apply(lambda x: x if isinstance(x, list) else [])
    df["genres_list"] = df["genres_list"].apply(lambda x: x if isinstance(x, list) else [])

    return df


def compute_fingerprints(
    df: pd.DataFrame,
    countries: list[str],
    top_pos: int = 6,
    top_neg: int = 4,
    min_count: int = 5,
    baseline: str = "global",  # "global" or "only_selected"
    remove_international_labels: bool = False,
) -> dict:
    """
    Returns:
      {
        "selection": dict[country -> pd.Series(delta_pp indexed by genre)],
        "country_totals": pd.Series,
        "delta_pp": pd.DataFrame,
      }
    """
    df = _ensure_lists(df)
    df = df.drop_duplicates(subset=["show_id"])

    # optional filter for "International ..." labels (can dominate the story)
    blocked = set()
    if remove_international_labels:
        blocked = {"International Movies", "International TV Shows"}

    # Build long table (title,country,genre) unique
    rows = []
    for _, r in df.iterrows():
        tid = r["show_id"]
        cs = r["countries_list"]
        gs = set(r["genres_list"])  # avoid double-count per title
        if blocked:
            gs = {g for g in gs if g not in blocked}
        for c in cs:
            if c in countries:
                for g in gs:
                    rows.append((tid, c, g))
    long_sel = pd.DataFrame(rows, columns=["show_id", "country", "genre"]).drop_duplicates()

    # Baseline: global across all titles, or only selected countries' titles
    if baseline == "only_selected":
        # use only titles that appear in the selected countries (co-productions included)
        titles_in_sel = long_sel["show_id"].unique()
        df_base = df[df["show_id"].isin(titles_in_sel)]
    else:
        df_base = df

    # Global shares (each title contributes once per genre)
    g_rows = []
    for _, r in df_base.iterrows():
        tid = r["show_id"]
        gs = set(r["genres_list"])
        if blocked:
            gs = {g for g in gs if g not in blocked}
        for g in gs:
            g_rows.append((tid, g))
    g_long = pd.DataFrame(g_rows, columns=["show_id", "genre"]).drop_duplicates()
    global_total_titles = df_base["show_id"].nunique()
    global_share = g_long.groupby("genre")["show_id"].nunique() / max(global_total_titles, 1)

    # Country totals & shares
    country_totals = long_sel.groupby("country")["show_id"].nunique().reindex(countries)
    country_genre_counts = (
        long_sel.groupby(["country", "genre"])["show_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(index=countries, fill_value=0)
    )
    country_share = country_genre_counts.div(country_totals, axis=0)

    # Align
    all_genres = sorted(set(country_share.columns).union(set(global_share.index)))
    country_genre_counts = country_genre_counts.reindex(columns=all_genres, fill_value=0)
    country_share = country_share.reindex(columns=all_genres, fill_value=0.0)
    global_share = global_share.reindex(all_genres).fillna(0.0)

    delta_pp = (country_share - global_share) * 100.0

    # Per-country selection
    selection = {}
    for c in countries:
        counts = country_genre_counts.loc[c]
        eligible = counts[counts >= min_count].index
        s = delta_pp.loc[c, eligible].dropna().sort_values(ascending=False)
        if len(s) < (top_pos + top_neg):
            eligible = counts[counts >= 1].index
            s = delta_pp.loc[c, eligible].dropna().sort_values(ascending=False)
        sel = pd.concat([s.head(top_pos), s.tail(top_neg)]).sort_values()
        selection[c] = sel

    return {"selection": selection, "country_totals": country_totals, "delta_pp": delta_pp}


def create_genre_fingerprints_figure(result: dict, title: str = "Genre Fingerprints by Country") -> go.Figure:
    selection: dict = result["selection"]
    country_totals: pd.Series = result["country_totals"]

    countries = list(selection.keys())

    # consistent axis range
    max_abs = max(float(np.nanmax(np.abs(selection[c].values))) for c in countries if len(selection[c]) > 0)
    lim = min(80.0, max(10.0, max_abs * 1.20))

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=countries,
        horizontal_spacing=0.10,
        vertical_spacing=0.18,
    )

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for (r, cidx), country in zip(positions, countries):
        s = selection[country]
        y = s.index.tolist()
        x = s.values.astype(float)

        colors = [NETFLIX_RED if v > 0 else NEG for v in x]

        fig.add_trace(
            go.Bar(
                x=x,
                y=y,
                orientation="h",
                marker=dict(color=colors),
                hovertemplate="<b>%{y}</b><br>Δ vs global: %{x:.1f} pp<extra></extra>",
            ),
            row=r, col=cidx
        )

        # zero line (shape)
        fig.add_shape(
            type="line",
            x0=0, x1=0,
            y0=-0.5, y1=len(y) - 0.5,
            xref=f"x{(r-1)*2 + cidx}",
            yref=f"y{(r-1)*2 + cidx}",
            line=dict(color=AXIS, width=2),
        )

        # axes styling
        fig.update_xaxes(
            range=[-lim, lim],
            showgrid=True,
            gridcolor=GRID,
            zeroline=False,
            ticksuffix="pp",
            tickfont=dict(color=SUBTEXT),
            row=r, col=cidx,
        )
        fig.update_yaxes(
            tickfont=dict(color=TEXT),
            row=r, col=cidx,
        )

        # panel subtitle (n=...)
        n_titles = int(country_totals.loc[country]) if pd.notna(country_totals.loc[country]) else 0
        fig.add_annotation(
            text=f"n={n_titles:,} titles • Δ vs global",
            xref=f"x{(r-1)*2 + cidx} domain",
            yref=f"y{(r-1)*2 + cidx} domain",
            x=0.0, y=1.10,
            showarrow=False,
            font=dict(color=SUBTEXT, size=12, family=FONT_STACK),
            align="left",
        )

    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(family=FONT_STACK, color=TEXT),
        title=dict(
            text=f"<span style='color:{NETFLIX_RED};font-weight:800'>NETFLIX</span>  {title}",
            x=0.02,
            xanchor="left",
            font=dict(size=24, family=FONT_STACK, color=TEXT),
        ),
        margin=dict(l=40, r=40, t=110, b=60),
        height=820,
        showlegend=False,
    )

    # make subplot title text (country names) readable on dark bg
    fig.update_annotations(font=dict(color=TEXT, family=FONT_STACK, size=16))

    return fig
