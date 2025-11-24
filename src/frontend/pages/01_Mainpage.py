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
st.plotly_chart(map_fig, use_container_width=True)
selected = plotly_events(map_fig, select_event=True,override_height=0,override_width=0)

if selected:
    idx = selected[0]["pointNumber"]
    clicked = df_formap.iloc[idx]["ISO3_country"]
    st.write("Land geklickt:", clicked)
else:
    st.write("Noch nichts geklickt.")
# ----------------------------------------------------------------------
# Sankey
# ----------------------------------------------------------------------

filtered = df_netflix_ex

disable_sankey = False
if not filtered.empty and not disable_sankey:

    countries = filtered["country"].unique().tolist()
    genres = filtered["genre"].unique().tolist()
    decades = filtered["release_year"].unique().tolist()

    all_nodes = countries + genres + decades
    idx = {name: i for i, name in enumerate(all_nodes)}

    # Country → Genre
    links1 = filtered.groupby(["country", "genre"])["value"].sum().reset_index()
    # Genre → Decade
    links2 = filtered.groupby(["genre", "decade"])["value"].sum().reset_index()

    source, target, value = [], [], []

    for _, row in links1.iterrows():
        source.append(idx[row["country"]])
        target.append(idx[row["genre"]])
        value.append(row["value"])

    for _, row in links2.iterrows():
        source.append(idx[row["genre"]])
        target.append(idx[row["decade"]])
        value.append(row["value"])

    sankey = go.Figure(data=[go.Sankey(
        node=dict(label=all_nodes, pad=20, thickness=16),
        link=dict(source=source, target=target, value=value)
    )])

    st.plotly_chart(sankey, use_container_width=True)
else:
    st.warning("Keine Daten für dieses Land.")
