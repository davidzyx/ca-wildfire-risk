## Note: Use <lsof -ti tcp:8050 | xargs kill -9> after running the app to kill its process ##

from typing import Container
from dash.dependencies import State
from dash_html_components.Tr import Tr
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import dash_table

from src import utils
# import utils

from datetime import datetime
import calendar
import json
from os import path, environ
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from pathlib import Path
import os

colors = {
    'background': '##333',
    'text': '#7FDBFF'
}
    
# Data loading fire occurance
ppath = Path(os.getcwd()).absolute()
file_name = os.path.join(ppath, 'data/fire_occurrances_data.csv')
df_fire_occurrances = pd.read_csv(file_name) 

# Data loading for geo-model
geo_all_data = pd.read_csv(os.path.join(ppath, 'data/final_data.csv'))
geo_county_coordinates = np.load(os.path.join(ppath, 'data/county_positions.npy'),  allow_pickle=True)
geo_model = np.load(os.path.join(ppath, 'data/geo_model.npy'),  allow_pickle=True)
geo_encodings = np.load(os.path.join(ppath, 'data/encodings.npy'),  allow_pickle=True)
geo_extreames = np.load(os.path.join(ppath, 'data/extreames.npy'),  allow_pickle=True)

# Preprocessing Data
STATE = 'START'
data = pd.read_csv("https://www.fire.ca.gov/imapdata/mapdataall.csv")
table_data = pd.DataFrame()
data=data[data['incident_acres_burned'].notnull()] # Dropping Nulls
data=data[data['incident_dateonly_extinguished'].notnull()] # Dropping Nulls
data['date'] = pd.to_datetime(data['incident_dateonly_extinguished'])
data['date_start'] = pd.to_datetime(data['incident_dateonly_created'])
data = data[data.date >  datetime.strptime('2010-01-01', '%Y-%m-%d')] # Dropping wrong/invalid dates



min_date = min(data.date)
max_date = max(data.date)

navbar = html.Div(id='navbar', className='topnav' ,children=[
        html.A('Home', id='home-page-nav', className="home-page", href='home'),
        html.A('California Incident Map', id='cali-map-nav', className="cali-map", href='app1'),
        html.A('County Incident Map', id='county-map-nav', className="county-map", href='app2'), 
        html.A('County Based Prediction', id='county-based-pred-nav', className="county-based-pred", href='app3'),
        html.A('Geo Coordinates Based Prediction', id='geo-based-pred-nav', className="geo-based-pred", href='app4')
])

date_picker_widget = dcc.DatePickerRange(
        style={'border':'2px black solid'},
        id='date_picker',
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        start_date=datetime.strptime('2021-01-01', '%Y-%m-%d'),
        end_date=max_date,
        number_of_months_shown=4, 
    )

month_picker_slider = dcc.Slider(
        id='month_slider',
        min=1,
        max=12,
        marks={
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        },
        step=1,
        value=1,
    )

county_dropdown = dcc.Dropdown(
        id='county_dropdown',
        options=[{'label': county, 'value': county} for county in utils.ca_counties_list],
        multi=True, 
        placeholder='Select one or more California Counties...'
    )

county_dropdown2 = dcc.Dropdown(
        id='county_dropdown2',
        options=[{'label': county, 'value': county} for county in utils.ca_counties_list],
        value='Alameda'
    )

range_slider = dcc.RangeSlider(
        id='range_slider', 
        min=2010, 
        max=2021, 
        marks = {
            2010: '2010', 2011: '2011', 2012: '2012', 2013: '2013', 2014: '2014', 2015: '2015', 2016: '2016', 2017: '2017', 2018: '2018', 2019: '2019', 2020: '2020', 2021: '2021'
        },
        value=[2010, 2021],
        allowCross=False
    )

# Map Widget
if path.exists('src/.mapbox_token'):
    px.set_mapbox_access_token(open("src/.mapbox_token").read())
elif 'MAPBOX_TOKEN' in environ.keys():
    px.set_mapbox_access_token(environ['MAPBOX_TOKEN'])
else:
    print("TOKEN not found in env or local dir")



cali_map = dcc.Graph(id='cali_map')
county_map = dcc.Graph(id='county_map')
county_pie = dcc.Graph(id='county_pie')
county_prediction = dcc.Graph(id='county_prediction', style={'border':'2px black solid'})


# Building App Layout
app = dash.Dash(__name__, suppress_callback_exceptions=True)
header = html.Div(id='header', style={'backgroundColor':colors['background']} ,children=[
        html.H1(children='California Wildfire Interactive Dashboard', className='main-title'),
    ])
county_map_div = html.Div(id='county_map_div', style={'textAlign': 'center'}, children=county_map)
county_pie_div = html.Div(id='county_pie_div', style={'textAlign': 'center'}, children=county_pie)

date_picker_row = html.Div(id='datepicker', style={'textAlign': 'center', 'padding': '4px'}, children=[html.Div(children='Filter by Date:'), date_picker_widget])
month_picker_row = html.Div(style={'textAlign': 'center', 'padding': '4px'}, children=[html.Div(children='Query a Month:'), month_picker_slider])

cali_map_table = dash_table.DataTable(
    style_table={
        'border':'2px black solid',
        'height': 500,
        'overflowY': 'scroll',
        'width': 540
    },
    id='cali_map_table',
    style_header={'backgroundColor': '#04AA6D'},
    style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    columns=[{"name": i, "id": i} for i in ['incident_name' ,'incident_administrative_unit', 'incident_location']],
)


pred_table = dash_table.DataTable(
    style_table={
        'border':'2px black solid',
        'height': 700,
        'overflowY': 'scroll',
        'width': 300
    },
    id='pred_table',
    style_header={'backgroundColor': '#04AA6D'},
    style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    columns=[{"name": i, "id": i} for i in ['County', 'Predicted Number of Fires']],
)

fire_trend = dcc.Graph(id='fire-trend', style={'border':'2px black solid'})
trend_picker = html.Div(children = [range_slider, county_dropdown2], style={'color':'#04AA6D'})
label_trend = html.Div(html.Label('Please choose your preferred time range:'),style={'margin-bottom':0})
title_trend = html.Div(html.H2('How is the incident trend in past years? ', className='hh'),style={'margin-bottom':0})
trend_container = html.Div(children=[label_trend, trend_picker, fire_trend], style={'padding': '10px'})
fire_trend_div = html.Div(id='trend', style={'padding': '0px', 'columnCount': 1}, children=[title_trend ,trend_container])
title_pred = html.Div(html.H2('Prediction Based on County & Month',className='hh'),style={'margin-bottom':10})

title_cali_map = html.Div(html.H2('Incidents on California map with Size, Date and Location', className='hh'),style={'margin-bottom':0})
label_cali_map = html.Div(html.Label('Please choose your preferred date range between 02/28/2013 and 01/22/2021 (Note that a small date range is required for full functionality with the select and hovering tools):'),style={'margin-bottom':5, 'margin-left':5})
cali_map_div_container = html.Div(id = 'cal-map',style={'padding': '10px', 'columnCount': 2}, children=[cali_map, html.Div(style={'padding':'150px'},children=[cali_map_table])])
cali_map_div = html.Div(id = 'calmap', children=[title_cali_map, label_cali_map, date_picker_row, cali_map_div_container])

title_county_map = html.Div(html.H2('Incidents in California by County', className='hh'),style={'margin-bottom':0})
label_county_map = html.Div(html.Label('Please choose your preferred date range between 02/28/2013 and 01/22/2021:'),style={'margin-bottom':5, 'margin-left':5})
second_row = html.Div(style={'columnCount': 2}, children=[county_map_div, county_pie_div])
county_map_div = html.Div(id = 'countymap', children=[title_county_map, label_county_map, date_picker_row, second_row])

pred_graph_div_container = html.Div(id = 'pred-map',style={'padding': '10px', 'columnCount': 2}, children=[county_prediction, html.Div(style={'padding':'150px'},children=[pred_table])])
pred_div_container = html.Div(children=[month_picker_row, county_dropdown, pred_graph_div_container])
pred_div = html.Div(id = 'pred' ,style={'padding': '0px', 'columnCount': 1}, children=[title_pred ,pred_div_container])


# Home Page
# https://www.w3schools.com/
prompt_message_container = html.Div(className='prompt', children=[
    html.Div(className='brand-box', children=[html.Span(className='brand', children='ECE 229 - Spring 2021')]),
    html.Div(className='text-box', children=[html.H1(className='heading-primary', children=[
        html.Span(className='heading-primary-main', children='Looking for a tool to analyze California Wildfires ?'),
        html.Span(className='heading-primary-sub', children='You are in the right place!')
    ]),
    html.A(href='#services', className="btn btn-white btn-animated", children='Discover more')])
])


learn_more_container_1 = html.Div(className='about-section', children=[
    html.H1(className='about-us-header',children='Our Services'),
    html.P(children='The tools we provide include data visualization, data inspection, incident analysis based on time and location, and incident prediction based on user data entries.'),
    html.P(children=['All of these services are based on CAL FIRE dataset provided by']),
    html.A(children=['California Department of Forestry and Fire Protection '], href='https://www.fire.ca.gov/', className='linkk')
])

learn_more_services = html.H2(className='services-header', style='text-align:center', children='Our Services')

learn_more_container_2 = html.Div(className='row', children=[
    html.Div(className='column', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p1.png'), className='service-images'),
            html.Div(className='containerr', children=[
                html.H2('California Incident Map', className='services-header'),
                html.P(className='title', children='Data Visualization & Inspection'),
                html.P('This service provides tools for the user to inspect the location of incidents on a California map.'),
                html.P(children=html.A(className='button', children='Learn More', href='#lmcali'))
            ])
        ])
    ]),
    html.Div(className='column', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p2.png'), className='service-images'),
            html.Div(className='containerr', children=[
                html.H2('County Incident Map', className='services-header'),
                html.P(className='title', children='Data Visualization & Inspection'),
                html.P('This tool provide visuals for the user to inspect county incidents more closely'),
                html.P(children=html.A(className='button', children='Learn More', href='#lmcounty'))
            ])
        ])
    ]),
    html.Div(className='column', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p3.png'), className='service-images'),
            html.Div(className='containerr', children=[
                html.H2('County Based Prediction', className='services-header'),
                html.P(className='title', children='Analysis & Prediction'),
                html.P('Based on an extensive predictive model on the backend, the user can know the expected number of incidents in a desired month and county'),
                html.P(children=html.A(className='button', children='Learn More', href='#lmp1'))
            ])
        ])
    ]),
    
])

second_row_service = html.Div(className='row', children=[
    html.Div(className='column', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p4.png'), alt='Jane', className='service-images'),
            html.Div(className='containerr', children=[
                html.H2('Geo Coordinates Based Prediction', className='services-header'),
                html.P(className='title', children='Analysis & Prediction'),
                html.P('This model generates a probability for an incident, based on the user desired lon/lat and time'),
                html.P(children=html.A(className='button', children='Learn More', href='#lmp2'))
            ])
        ])
    ])
])

our_services = html.Div(id='services', children=[learn_more_container_1, learn_more_services, learn_more_container_2, second_row_service])

more_on_cali_map = html.Div(id='lmcali', className='more-on-cali-map', children=[
    html.H2(className='more-on-cali-head', children=['California Incident Map']),
    html.H3(className='more-on-cali-subhead', children=['You can take a grasp of location, size and time of the previous incidents with just a glance!']),
    html.P(className='more-on-cali-p', children=['For using this tool, you just need to set a time range, and the map will update based on what you chose. Radius of scattered points change proportional to the size of the incident']),
    html.P(className='more-on-cali-p', children=['You can use the toolkit above the map to select the incidents you are interested to investigate more. Further information about the chosen incidents will pop up in a table.'])
])

more_on_county_map = html.Div(id='lmcounty', className='more-on-county-map', children=[
    html.H2(className='more-on-county-head', children=['County Incident Map']),
    html.H3(className='more-on-county-subhead', children=['If you are looking for a tool to interact with the dataset from county point of view, this is the right tool for you.']),
    html.P(className='more-on-county-p', children=['For using this tool, you just need to set a time range, and the county heat map will be updated. the heat map indicates number of incidents per county.']),
    html.P(className='more-on-county-p', children=['A pie chart is provided beside the map, to give  the user a general insight of rate of incidents in all counties together.'])
])

more_on_pred1 = html.Div(id='lmp1',className='more-on-pred1', children=[
    html.H2(className='more-on-pred1-head', children=['County Based Prediction']),
    html.H3(className='more-on-pred1-subhead', children=['If you want to do prediction on the expected number of fires, based on the county and the month, this tool can help']),
    html.P(className='more-on-pred1-p', children=['For using this tool, you just need to set a month and the county you are interested in, and the predicted number of fire occurences would be calculated based on a combined model of averaging past, Seasonal Arima, and Unobserved components.']),
    html.P(className='more-on-pred1-p', children=['The location of the county will be shown on the map and the expected number of fire occurences would be shown in the table on the right.'])
])

more_on_pred2 = html.Div(id='lmp2',className='more-on-pred2', children=[
    html.H2(className='more-on-pred2-head', children=['Geo Coordinates Based Prediction']),
    html.H3(className='more-on-pred2-subhead', children=['After using other tools in the dashboard, you may come up with some spots of interest, you can do an specific prediction on these spots by this tool']),
    html.P(className='more-on-pred2-p', children=['HOW THE PREDICTIVE MODEL WORKS (TO BE COMPLETED)  HOW THE PREDICTIVE MODEL WORKS (TO BE COMPLETED)  HOW THE PREDICTIVE MODEL WORKS (TO BE COMPLETED)  HOW THE PREDICTIVE MODEL WORKS (TO BE COMPLETED)']),
    html.P(className='more-on-pred2-p', children=['HOW IT IS GONNA HELP USER  (BASED ON USER STORY) HOW IT IS GONNA HELP USER  (BASED ON USER STORY) HOW IT IS GONNA HELP USER  (BASED ON USER STORY)  HOW IT IS GONNA HELP USER  (BASED ON USER STORY)'])
])

MAP_ID = "map-id"
COORDINATE_CLICK_ID = "coordinate-click-id"
cali_map_table2 = dash_table.DataTable(
    style_table={
        'border':'2px black solid',
        'height': 500,
        'overflowY': 'scroll',
        'width': 540
    },
    id=COORDINATE_CLICK_ID,
    style_header={'backgroundColor': '#04AA6D'},
    style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    columns=[{"name": i, "id": i} for i in ['Longitude' ,'Latitude', 'Month', 'Probability of Incident']],
)
month_picker_slider2 = dcc.Slider(
        id='month_slider2',
        min=1,
        max=12,
        marks={
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        },
        step=1,
        value=1,
    )
month_picker_row2 = html.Div(id = 'prow', style={'textAlign': 'center', 'padding': '4px', 'margin-top': '0px'}, children=[html.Div(id='prow', children='Query a Month:'), month_picker_slider2])
title_cali_map2 = html.Div(html.H2('Prediction Based on Chosen Longitude and Latitude', className='hh'),style={'margin-bottom':0})
label_cali_map2 = html.Div(html.Label('Please pick a point from the map below:'),style={'margin-bottom':5, 'margin-left':5})
cali_map2 = dl.Map(id=MAP_ID, style={'width': '800px', 'height': '400px', 'border':'2px black solid'}, center=[37.219306366090116, -119.66673872628975], zoom=5, children=[
        dl.TileLayer()
        ])
cali_map_div2_container = html.Div(id = 'cal-map2',style={'padding': '10px', 'columnCount': 2}, children=[cali_map2, html.Div(style={'padding':'150px'},children=[cali_map_table2])])
cali_map_div2 = html.Div(id = 'calmap2', children=[label_cali_map2, cali_map_div2_container])
pred2_container = html.Div(style={'padding':'0px'}, children=[
    title_cali_map2, month_picker_row2, cali_map_div2
])


app.title = 'Cal Fire Dashboard'


app.layout = html.Div(style={'border':'2px black solid'},children=[dcc.Location(id='url', refresh=False), header, navbar, html.Div(id='page-content', children=[prompt_message_container, our_services, more_on_cali_map, more_on_county_map,  more_on_pred1, more_on_pred2])])

@app.callback(dash.dependencies.Output(COORDINATE_CLICK_ID, 'data'),
              [dash.dependencies.Input(MAP_ID, 'click_lat_lng'), dash.dependencies.Input('month_slider2', 'value')])
def click_coord(e, month):
    global table_data
    bad_input = False
    if e is not None:
        coordinates = e
    else:
        return "-"

    if coordinates[0] < 32.534156 or coordinates[0] > 42.009518 or coordinates[1] <-124.409591 or coordinates[1] > -114.131211:
        bad_input = True
    if bad_input:
        coordinates[0] = 'Out of Region'
        coordinates[1] = 'Out of Region'
        coordinates.append(calendar.month_name[month])
        coordinates.append('N/A')
        df_row = pd.DataFrame([coordinates], columns = ['Longitude' ,'Latitude', 'Month', 'Probability of Incident'])
        table_data = table_data.append(df_row, ignore_index=True)
        table_dataa = table_data[['Longitude' ,'Latitude', 'Month', 'Probability of Incident']]
        table_dataa = table_dataa.to_dict('records')
        return table_dataa

    coordinates.append(calendar.month_name[month])
    coordinates.append(utils.pred_func_geo(geo_all_data, geo_county_coordinates, geo_model, geo_encodings, geo_extreames, coordinates[0], coordinates[1], month))
    
    if not coordinates:
        return table_data.to_dict('records')

    df_row = pd.DataFrame([coordinates], columns = ['Longitude' ,'Latitude', 'Month', 'Probability of Incident'])
    table_data = table_data.append(df_row, ignore_index=True)
    table_dataa = table_data[['Longitude' ,'Latitude', 'Month', 'Probability of Incident']]
    table_dataa = table_dataa.to_dict('records')
    return table_dataa

# county-map callbacks
@app.callback(
    dash.dependencies.Output('cali_map_table', 'data'),
    [dash.dependencies.Input('cali_map', 'selectedData')])
def display_data(selectedData):
    table_data =  pd.DataFrame()
    if not selectedData:
        return table_data.to_dict('records')

    for pt in selectedData['points']:
        row = data.loc[(data['incident_longitude'] == pt['lon']) & (data['incident_latitude'] == pt['lat'])]
        table_data = table_data.append(row)

    table_data = table_data[["incident_name", "incident_administrative_unit", "incident_location"]]
    table_data = table_data.to_dict('records')
    return table_data


@app.callback(
    dash.dependencies.Output('pred_table', 'data'),
    [dash.dependencies.Input('county_dropdown', 'value'), dash.dependencies.Input('month_slider', 'value')])
def display_pred_data(queried_counties, month):
    return utils.getCountyPredictions(queried_counties, month).to_dict('records')
    

@app.callback(
    dash.dependencies.Output('cali_map', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_cali_map(start_date, end_date):
    fig = px.scatter_mapbox(
        data[(data.date >= start_date) & (data.date <= end_date)], lat="incident_latitude", lon="incident_longitude", size='incident_acres_burned', 
        zoom=4, height=400, width=800, size_max=22,  hover_name="incident_name", 
        color_discrete_sequence=['red'], center={'lon':-119.66673872628975, 'lat':37.219306366090116}, title='Wildfires Incident Map',
    )

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=True,
    ) 

    return fig






# county-map callbacks
@app.callback(
    dash.dependencies.Output('county_map', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_county_map(start_date, end_date):
    county_map_fig = px.choropleth(
        utils.getCountyNumbersDF(data, start_date, end_date), geojson=utils.counties, locations='county', 
        color='Number of County Incidents', featureidkey='properties.name', projection="mercator", 
        color_continuous_scale=px.colors.sequential.Reds, center={'lon':-119.66673872628975, 'lat':37.219306366090116}, title='County Incident Frequency', 
        width=700, height=700
    )

    county_map_fig.update_geos(fitbounds='geojson', visible=False)
    county_map_fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    return county_map_fig

@app.callback(
    dash.dependencies.Output('county_pie', 'figure'),
    [dash.dependencies.Input('date_picker', 'start_date'), dash.dependencies.Input('date_picker', 'end_date')])
def update_county_pie(start_date, end_date):
    county_pie_fig = px.pie(
        utils.getCountyNumbersDF(data, start_date, end_date), values='Number of County Incidents', names='county',
        width=700, height=700, title='County Incident Distribution'
    )

    county_pie_fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    return county_pie_fig

@app.callback(
    dash.dependencies.Output('county_prediction', 'figure'),
    [dash.dependencies.Input('county_dropdown', 'value'), dash.dependencies.Input('month_slider', 'value')])
def update_county_prediction(queried_counties, month):
    if not queried_counties:
        df = pd.DataFrame({'County': [], 'Predicted Number of Fires': []})
    else: 
        df = utils.getCountyPredictions(queried_counties, month)

    county_pred_fig = px.choropleth(
        df, geojson=utils.counties, locations='County', 
        color='Predicted Number of Fires', featureidkey='properties.name', projection="mercator", 
        color_continuous_scale=px.colors.sequential.Reds, 
        width=650, height=650, title=f'Number of Predicted Incidents in {calendar.month_name[month]}'
    )
    # print(month)
    county_pred_fig.update_geos(fitbounds='geojson', visible=False)
    county_pred_fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0})

    return county_pred_fig

@app.callback(
    dash.dependencies.Output('fire-trend', 'figure'),
    [dash.dependencies.Input('county_dropdown2', 'value'),dash.dependencies.Input('month_slider', 'value'), dash.dependencies.Input('range_slider', 'value')]
)
def update_trend(county, month, year_range):
    year_start, year_end= year_range
    filtered_data = utils.getTrend(county, month, year_start, year_end)
    filtered_data['year'] = [str(x) for x in filtered_data.year]
    print(type(filtered_data['year'][0]))
    fig = px.bar(filtered_data, x="year", y="count", title="Incidents per Year, in "  + str(calendar.month_name[month]))
    fig.update_traces(marker_color='#04AA6D')
    fig.update_layout(margin={"r":0,"t":70,"l":0,"b":0})
    fig.update_layout(
    xaxis = go.layout.XAxis(
        tickangle = -45)
)
    return fig
    

# Navbar callback
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    global STATE
    global table_data
    table_data = pd.DataFrame()

    if STATE == 'START':

        STATE = 'END'
        return html.Div(children=[prompt_message_container, our_services, more_on_cali_map, more_on_county_map,  more_on_pred1, more_on_pred2])

    if STATE == 'END':

        STATE = 'DONE'
        return html.Div(children=[prompt_message_container, our_services, more_on_cali_map, more_on_county_map,  more_on_pred1, more_on_pred2])

    if pathname == '/home' or pathname == None:
        return html.Div(children=[prompt_message_container, our_services, more_on_cali_map, more_on_county_map,  more_on_pred1, more_on_pred2])
    elif pathname == '/app1':
        return html.Div(id='app1-div', children=[cali_map_div])
    elif pathname == '/app2':
        return html.Div(id='app2-div', children=[county_map_div])
    elif pathname == '/app3':
        return html.Div(id='app3-div', children=[pred_div, fire_trend_div])
    elif pathname == '/app4':
        return html.Div(id='app4-div', children=[pred2_container])

if __name__ == '__main__':
    #Running App (Port 8050 by default)
    if 'PORT' in environ.keys():
        port = int(environ['PORT'])
    else:
        port = 8050
    app.run_server(host='0.0.0.0', debug=False, use_reloader=False, port=port, dev_tools_ui=False)  # Turn off reloader if inside Jupyter

## Note: Use <lsof -ti tcp:8050 | xargs kill -9> after running the app to kill its process ##
