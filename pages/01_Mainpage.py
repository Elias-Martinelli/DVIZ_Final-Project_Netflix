"""This module contains the mainpage content."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is importable when Streamlit runs pages
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from thenetflixstory.data_processing import load_netflixdata
from thenetflixstory.graph1 import create_wordmap

st.title("MainPage")

# ----------------------------------------------------------------------
# Load Data
# ----------------------------------------------------------------------
df_netflix = load_netflixdata()

# ----------------------------------------------------------------------
# Worldmap
# ----------------------------------------------------------------------
st.subheader("Global catalog volume (by country & year)")

if "ISO3_country" not in df_netflix.columns:
    st.error("Column `ISO3_country` not found. Check `add_iso3_countrynames()` in data_processing.py.")
    st.stop()

if "release_year" not in df_netflix.columns:
    st.error("Column `release_year` not found.")
    st.stop()

# Count titles per year + country
df_formap = (
    df_netflix[~df_netflix["ISO3_country"].isna()]
    .groupby(["release_year", "ISO3_country"], as_index=False)["title"]
    .count()
)

map_fig = create_wordmap(df_formap)
st.plotly_chart(map_fig, use_container_width=True)

st.markdown("""---
**Next:** Open **Genre Fingerprints** in the sidebar.
""")
