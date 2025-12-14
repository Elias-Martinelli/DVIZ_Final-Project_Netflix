"""Genre Fingerprints page (U.S., India, UK, Japan)."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is importable when Streamlit runs pages
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from thenetflixstory.data_processing import load_netflixdata
from thenetflixstory.graph_genre_fingerprints import (
    compute_fingerprints,
    create_genre_fingerprints_figure,
    theme_css,
)

st.title("Genre Fingerprints (US • India • UK • Japan)")
st.markdown(theme_css(), unsafe_allow_html=True)

df = load_netflixdata()

countries = ["United States", "India", "United Kingdom", "Japan"]

with st.sidebar:
    st.header("Controls")
    top_pos = st.slider("Top over-indexed genres", 3, 10, 6)
    top_neg = st.slider("Top under-indexed genres", 2, 10, 4)
    min_count = st.slider("Min titles per country+genre", 1, 30, 5)

    baseline = st.radio(
        "Baseline",
        options=["global", "only_selected"],
        format_func=lambda x: "Whole dataset (global)" if x == "global" else "Only selected countries",
        index=0,
    )

    remove_international = st.checkbox("Remove 'International Movies/TV' labels", value=False)
    st.caption("pp = percentage points (difference of shares vs baseline).")

result = compute_fingerprints(
    df=df,
    countries=countries,
    top_pos=top_pos,
    top_neg=top_neg,
    min_count=min_count,
    baseline=baseline,
    remove_international_labels=remove_international,
)

fig = create_genre_fingerprints_figure(
    result,
    title="Genre Fingerprints by Country",
    use_flag_emoji=True,
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Show selected deltas as table"):
    rows = []
    for c in countries:
        s = result["selection"][c]
        for genre, delta in s.items():
            rows.append({"country": c, "genre": genre, "delta_pp": float(delta)})
    st.dataframe(rows, use_container_width=True, hide_index=True)
