"""Netflix-style (dark) Plotly genre fingerprints (over/under-index vs baseline)."""
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

def theme_css() -> str:
    """Light CSS to make Streamlit app look Netflix-dark."""
    return f"""
    <style>
      .stApp {{ background: {BG}; }}
      section[data-testid="stSidebar"] {{ background: {PANEL}; }}
      h1, h2, h3, p, li, label, span {{ color: {TEXT}; }}
    </style>
    """

def _split_list(x) -> list[str]:
    if pd.isna(x):
        return []
    return [t.strip() for t in str(x).split(",") if t.strip()]

def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure we have: show_id, genres_list (list), countries_list (list)."""
    out = df.copy()

    if "show_id" not in out.columns:
        out = out.reset_index().rename(columns={"index": "show_id"})

    # genres_list already exists in your pipeline; fallback from listed_in if needed
    if "genres_list" not in out.columns:
        if "listed_in" in out.columns:
            out["genres_list"] = out["listed_in"].astype(str).str.split(", ")
        else:
            out["genres_list"] = [[] for _ in range(len(out))]

    # countries_list: from 'country' (comma-separated)
    if "countries_list" not in out.columns:
        if "country" in out.columns:
            out["countries_list"] = out["country"].apply(_split_list)
        else:
            out["countries_list"] = [[] for _ in range(len(out))]

    out["genres_list"] = out["genres_list"].apply(lambda x: x if isinstance(x, list) else [])
    out["countries_list"] = out["countries_list"].apply(lambda x: x if isinstance(x, list) else [])
    return out

def compute_fingerprints(
    df: pd.DataFrame,
    countries: list[str],
    top_pos: int = 6,
    top_neg: int = 4,
    min_count: int = 5,
    baseline: str = "global",  # "global" or "only_selected"
    remove_international_labels: bool = False,
) -> dict:
    """Compute per-country over/under-indexing vs baseline (percentage points)."""
    df = _ensure_columns(df).drop_duplicates(subset=["show_id"])

    blocked = set()
    if remove_international_labels:
        blocked = {"International Movies", "International TV Shows"}

    # (title,country,genre) for selected countries
    rows = []
    for _, r in df.iterrows():
        tid = r["show_id"]
        cs = r["countries_list"]
        gs = set(r["genres_list"])  # title contributes once per genre
        if blocked:
            gs = {g for g in gs if g not in blocked}
        for c in cs:
            if c in countries:
                for g in gs:
                    rows.append((tid, c, g))
    long_sel = pd.DataFrame(rows, columns=["show_id", "country", "genre"]).drop_duplicates()

    # Baseline dataset
    if baseline == "only_selected":
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

def create_genre_fingerprints_figure(
    result: dict,
    title: str = "Genre Fingerprints by Country",
    use_flag_emoji: bool = True,
) -> go.Figure:
    selection: dict = result["selection"]
    country_totals: pd.Series = result["country_totals"]

    countries = list(selection.keys())

    if use_flag_emoji:
        flags = {
            "United States": "🇺🇸 United States",
            "India": "🇮🇳 India",
            "United Kingdom": "🇬🇧 United Kingdom",
            "Japan": "🇯🇵 Japan",
        }
        subplot_titles = [flags.get(c, c) for c in countries]
    else:
        subplot_titles = countries

    max_abs = max(float(np.nanmax(np.abs(selection[c].values))) for c in countries if len(selection[c]) > 0)
    lim = min(80.0, max(10.0, max_abs * 1.20))

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=subplot_titles,
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
                hovertemplate="<b>%{y}</b><br>Δ vs baseline: %{x:.1f} pp<extra></extra>",
            ),
            row=r, col=cidx
        )

        # zero line
        fig.add_shape(
            type="line",
            x0=0, x1=0,
            y0=-0.5, y1=len(y) - 0.5,
            xref=f"x{(r-1)*2 + cidx}",
            yref=f"y{(r-1)*2 + cidx}",
            line=dict(color=AXIS, width=2),
        )

        fig.update_xaxes(
            range=[-lim, lim],
            showgrid=True,
            gridcolor=GRID,
            zeroline=False,
            ticksuffix="pp",
            tickfont=dict(color=SUBTEXT, family=FONT_STACK),
            row=r, col=cidx,
        )
        fig.update_yaxes(
            tickfont=dict(color=TEXT, family=FONT_STACK),
            row=r, col=cidx,
        )

        n_titles = int(country_totals.loc[country]) if pd.notna(country_totals.loc[country]) else 0
        fig.add_annotation(
            text=f"n={n_titles:,} titles • Δ vs baseline",
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
            x=0.02, xanchor="left",
            font=dict(size=24, family=FONT_STACK, color=TEXT),
        ),
        margin=dict(l=40, r=40, t=110, b=60),
        height=820,
        showlegend=False,
    )

    fig.update_annotations(font=dict(color=TEXT, family=FONT_STACK, size=16))
    return fig
