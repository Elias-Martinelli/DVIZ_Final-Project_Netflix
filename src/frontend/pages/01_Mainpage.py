"""This module contains the mainpage content"""
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

from thenetflixstory.data_processing import load_netflixdata
from thenetflixstory.graph1 import create_wordmap

st.title("MainPage-Title")

st.set_page_config(layout="wide")

# ----------------------------------------------------------------------
# Load Data
# ----------------------------------------------------------------------
df_netflix = load_netflixdata()
df_netflix_ex = df_netflix.explode('genres_list').rename(columns={'genres_list':'genre'})


# ----------------------------------------------------------------------
# Weltkarte
# ----------------------------------------------------------------------
df_formap = (
    df_netflix[~df_netflix['ISO3_country'].isna()] # Remove Moview without Country
    .groupby(['release_year','ISO3_country'],as_index=False)['title']
    .count()
)
map_fig = create_wordmap(df_formap)
st.plotly_chart(map_fig)
