import numpy as np

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

def create_wordmap(df : pd.DataFrame):
    map_fig = px.choropleth(
        df,
        locations="ISO3_country",
        locationmode="ISO-3",
        #color="title",
        color = np.log1p(df['title']),
        color_continuous_scale="YlOrRd",
        animation_frame='release_year'
    )
    map_fig.update_layout(clickmode="event+select", margin=dict(l=0, r=0, t=0, b=0))

    return map_fig
