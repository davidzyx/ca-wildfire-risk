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
import json


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


cali_map = dcc.Graph(id='cali_map')
county_map = dcc.Graph(id='county_map')
county_pie = dcc.Graph(id='county_pie')


# Building App Layout
app = dash.Dash(__name__)
header = html.Div(style={'backgroundColor':colors['background']} ,children=[
        html.H1(children='California Wildfire Interactive Dashboard'),
    ])

cali_map_div = html.Div(style={'border':'2px black solid', 'padding': '10px', 'columnCount': 2}, children=[cali_map,  html.Div(
        html.Pre(id='lasso', style={'overflowY': 'scroll', 'height': '50vh'})
    ),])

county_map_div = html.Div(style={'border':'2px black solid', 'padding': '10px'}, children=county_map)
county_pie_div = html.Div(style={'border':'2px black solid', 'padding': '10px'}, children=county_pie)

date_picker_row = html.Div(style={'textAlign': 'center', 'padding': '4px'}, children=[html.Div(children='Filter by Date:'), date_picker_widget])

second_row = html.Div(style={'columnCount': 2}, children=[county_map_div, county_pie_div])

app.layout = html.Div(style={'border':'2px black solid'},children=[header, date_picker_row, cali_map_div, second_row])


@app.callback(
    dash.dependencies.Output('cali_map', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_cali_map(start_date, end_date):
    fig = px.scatter_mapbox(
        data[(data.date >= start_date) & (data.date <= end_date)], lat="incident_latitude", lon="incident_longitude", size='incident_acres_burned', 
        zoom=4, height=500, width=850, size_max=22,  hover_name="incident_name", hover_data=["incident_county"], 
        color_discrete_sequence=['red'], center={'lon':-119.66673872628975, 'lat':37.219306366090116}, title='Wildfires Incident Map',
    )

    fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0})
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=True,
    ) 

    return fig


@app.callback(
    dash.dependencies.Output('county_map', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_county_map(start_date, end_date):
    county_map_fig = px.choropleth(
        utils.getCountyNumbersDF(data, start_date, end_date), geojson=utils.counties, locations='county', 
        color='Number of County Incidents', featureidkey='properties.name', projection="mercator", 
        color_continuous_scale=px.colors.sequential.Reds, center={'lon':-119.66673872628975, 'lat':37.219306366090116}, title='County Incident Frequency', 
        width=800, height=800
    )

    county_map_fig.update_geos(fitbounds='geojson', visible=False)
    county_map_fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0})

    return county_map_fig

@app.callback(
    dash.dependencies.Output('county_pie', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_county_pie(start_date, end_date):
    county_pie_fig = px.pie(
        utils.getCountyNumbersDF(data, start_date, end_date), values='Number of County Incidents', names='county', 
        width=800, height=800, title='County Incident Distribution'
    )

    county_pie_fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0})

    return county_pie_fig

@app.callback(
    dash.dependencies.Output('lasso', 'children'),
    [dash.dependencies.Input('cali_map', 'selectedData')])
def display_data(selectedData):
    if not selectedData:
        return 'No selected fires!'

    returnStr = ''
    for pt in selectedData['points']:
        returnStr += f"{pt['hovertext']} - Size: TODO, Location: ({pt['lon']:.2f}, {pt['lat']:.2f})\n"
    
    return returnStr

if __name__ == '__main__':
    #Running App (Port 8050 by default)
    app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

## Note: Use <lsof -ti tcp:8050 | xargs kill -9> after running the app to kill its process ##