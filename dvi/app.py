## Note: Use <lsof -ti tcp:8050 | xargs kill -9> after running the app to kill its process ##

import plotly.graph_objects as go # or plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import utils
from datetime import datetime

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Preprocessing Data
data = pd.read_csv("https://www.fire.ca.gov/imapdata/mapdataall.csv")
data=data[data['incident_acres_burned'].notnull()] # Dropping Nulls
data=data[data['incident_dateonly_extinguished'].notnull()] # Dropping Nulls
data['date'] = pd.to_datetime(data['incident_dateonly_extinguished'])
data = data[data.date >  datetime.strptime('2010-01-01', '%Y-%m-%d')] # Dropping wrong/invalid dates

min_date = min(data.date)
max_date = max(data.date)

date_picker_widget = dcc.DatePickerRange(
        id='date_picker',
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        start_date=min_date,
        end_date=max_date,
        number_of_months_shown=6, 
    )


# Map Widget
px.set_mapbox_access_token(open(".mapbox_token").read())

fig = px.scatter_mapbox(
    data, lat="incident_latitude", lon="incident_longitude", size='incident_acres_burned', zoom=4, height=500,
    width=850, size_max=22,  hover_name="incident_name", hover_data=["incident_county"], 
    color_discrete_sequence=['red'], center={'lon':-119.66673872628975, 'lat':37.219306366090116}
)


fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(
    title='Wildfires on California Map',
    autosize=True,
    hovermode='closest',
    showlegend=True,
)

cali_map = dcc.Graph(id='cali_map', figure=fig)

# Building App Layout
app = dash.Dash(__name__)
header = html.Div(style={'backgroundColor':colors['background']} ,children=[
        html.H1(children='California Wildfire Interactive Dashboard'),
    ])

app.layout = html.Div(style={},children=[header, cali_map, date_picker_widget])


@app.callback(
    dash.dependencies.Output('cali_map', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_output(start_date, end_date):
    new_fig = px.scatter_mapbox(
        data[(data.date >= start_date) & (data.date <= end_date)], lat="incident_latitude", lon="incident_longitude", size='incident_acres_burned', 
        zoom=4, height=500, width=850, size_max=22,  hover_name="incident_name", hover_data=["incident_county"], 
        color_discrete_sequence=['red'], center={'lon':-119.66673872628975, 'lat':37.219306366090116}
    )

    new_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    new_fig.update_layout(
        title='Wildfires on California Map',
        autosize=True,
        hovermode='closest',
        showlegend=True,
    ) 

    return new_fig



if __name__ == '__main__':
    #Running App (Port 8050 by default)
    app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

## Note: Use <lsof -ti tcp:8050 | xargs kill -9> after running the app to kill its process ##