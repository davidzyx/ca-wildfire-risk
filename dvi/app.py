import plotly.graph_objects as go # or plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import utils




colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

data = pd.read_csv("https://www.fire.ca.gov/imapdata/mapdataall.csv")
data=data[data['incident_acres_burned'].notnull()]
data=data[data['incident_dateonly_extinguished'].notnull()]
int_time_column = data['incident_dateonly_extinguished'].apply(utils.date_to_int)
data['int_time'] = list(int_time_column)
data = data[data.int_time > 20100000]



fig = px.scatter_mapbox(data, lat="incident_latitude",
 lon="incident_longitude", color="int_time", size='incident_acres_burned', zoom=4, height=500,
  width=850, size_max=22, hover_name='incident_name', hover_data=['incident_county'],
   color_continuous_scale=["red",  "blue"]
   )


fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(
    title='Wildfires on California Map',
    autosize=True,
    hovermode='closest',
    showlegend=True,

)


app = dash.Dash(__name__)
app.layout =html.Div(style={},children=[
    html.Div(style={'backgroundColor':colors['background']} ,children=[
        html.H1(children='California Wildfire Interactive Dashboard'),
    ]),
    html.Div([
        html.Div(id='right', children=[html.H2(children='Map Widget') ,dcc.Graph(figure=fig)]),
    ])
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
# lsof -ti tcp:8050 | xargs kill -9