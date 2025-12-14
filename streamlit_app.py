"""Streamlit entry point (multipage)."""
import streamlit as st

st.set_page_config(
    page_title="The Netflix Story",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("The shift from traditional cinema to the series ecosystem")

st.markdown(
    """
    This app explores the Netflix catalog and highlights **country-specific genre fingerprints**.

    Use the sidebar to navigate:
    - **Mainpage**: world map / overview
    - **Genre Fingerprints**: dominant genres in **U.S., India, UK, Japan** (vs global baseline)
    """
)

st.info(
    "Add new charts as new Python files inside the `pages/` folder (e.g. `03_Your_New_Page.py`).",
    icon="ℹ️",
)
