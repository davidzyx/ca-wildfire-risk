from typing import Container
from dash.dependencies import State
from dash_html_components.Tr import Tr
import plotly.graph_objects as go 
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import dash_table
import dash_daq as daq

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

last_valid = (32.715736, -117.161087)

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


# Set Mapbox Access Token
if path.exists('src/.mapbox_token'):
    px.set_mapbox_access_token(open("src/.mapbox_token").read())
elif 'MAPBOX_TOKEN' in environ.keys():
    px.set_mapbox_access_token(environ['MAPBOX_TOKEN'])
else:
    print("TOKEN not found in env or local dir")


# Create App
app = dash.Dash(__name__, suppress_callback_exceptions=True)


# Navbar
navbar = html.Div(id='navbar', className='topnav' ,children=[
        html.A('Home', id='home-page-nav', className="home-page", href='home'),
        html.A('California Incident Map', id='cali-map-nav', className="non-home", href='app1'),
        html.A('County Incident Map', id='county-map-nav', className="non-home", href='app2'), 
        html.A('County Based Prediction', id='county-based-pred-nav', className="non-home", href='app3'),
        html.A('Geo Location Based Prediction', id='geo-based-pred-nav', className="non-home", href='app4')
])
# End of Navbar


# Header
header = html.Div(id='header', style={'backgroundColor':colors['background']}, children=[
            html.H1(children='California Wildfire Interactive Dashboard', className='main-title')
])
# End of Header


# Home Page - referenced https://www.w3schools.com/
prompt_message_container = html.Div(className='prompt', children=[
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

learn_more_container_2 = html.Div(className='row', style={'padding':'2rem'}, children=[
    html.Div(className='col-md-3 d-flex align-items-stretch', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p1.png'), className='card-img-top'),
            html.Div(className='card-body', children=[
                html.H3('California Incident Map', className='card-title'),
                html.P(className='title', children='Data Visualization & Inspection'),
                html.P(className='card-text',children='This service provides tools for the user to inspect the location of incidents on a California map.'),
            ]),
            html.P(className='card-footer',children=html.A(className='button', id='incident_map', children='Learn More', href='#desc_text2')),
            ])
    ]),
    html.Div(className='col-md-3 d-flex align-items-stretch', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p2.png'), className='card-img-top'),
            html.Div(className='card-body', children=[
                html.H3('County Incident Map', className='card-title'),
                html.P(className='title', children='Data Visualization & Inspection'),
                html.P(className='card-text',children='This tool provide visuals for the user to inspect county incidents more closely'),
            ]),
            html.P(className='card-footer',children=html.A(className='button', children='Learn More', id='lmcounty', href='#desc_text2'))
        ])
    ]),
    html.Div(className='col-md-3 d-flex align-items-stretch', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p3.png'), className='card-img-top'),
            html.Div(className='card-body', children=[
                html.H3('Prediction - County wise', className='card-title'),
                html.P(className='title', children='Analysis & Prediction'),
                html.P(className='card-text',children='Based on an extensive predictive model on the backend, the user can know the expected number of incidents in a desired month and county'),
            ]),
            html.P(className='card-footer',children=html.A(className='button', children='Learn More', id='lmp1', href='#desc_text2'))
        ])
    ]),
    html.Div(className='col-md-3 d-flex align-items-stretch', children=[
        html.Div(className='card', children=[
            html.Img(src=app.get_asset_url('p4.png'), alt='Jane', className='card-img-top'),
            html.Div(className='card-body', children=[
                html.H3('Predictions - Geo Location', className='card-title'),
                html.P(className='title', children='Analysis & Prediction'),
                html.P(className='card-text',children='This model generates a probability for an incident, based on the user desired lon/lat and time'),
            ]),
            html.P(className='card-footer',children=html.A(className='button', children='Learn More', id='lmp2', href='#desc_text2'))
        ])
    ])
    
])

second_row_service = html.Div(className='row', children=[
    html.Div(style={'padding': '1rem 3rem', 'background-color': '#333', 'color':'white'},children=[
        html.H2(id='desc_heading', className='desc_heading', children=["Learn More"]),
        html.P(id='desc_subhead', className='desc_subhead'),
    ]),
    html.Div(style={'padding': '1rem 3rem', 'background-color': '#d8f3d8'},children=[
        html.Br(),
        html.P(id='desc_text1', children=["Click \"Learn more\" to find out how the different services work"]),
        html.P(id='desc_text2', children=[''])
    ])
])

our_services = html.Div(id='services', children=[learn_more_container_1, learn_more_services, learn_more_container_2, second_row_service])
# End of Home Page


# Incident Page
date_picker_widget = dcc.DatePickerRange(
    style={'margin-bottom': '2rem'},
    id='date_picker',
    min_date_allowed=min_date,
    max_date_allowed=max_date,
    start_date=datetime.strptime('2021-01-01', '%Y-%m-%d'),
    end_date=max_date,
    number_of_months_shown=4, 
)
date_picker_row = html.Div(id='datepicker', style={'padding': '1 rem'}, children=[
    html.Div(children=[
        html.P(html.Strong('Filter by Date'))
    ]), 
    date_picker_widget
])

cali_map = dcc.Graph(id='cali_map', style={'width':'100%'})

cali_map_table = dash_table.DataTable(
    style_table={
        'height': 550,
        'overflowY': 'scroll',
        'width': '100%'
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

label_cali_map = html.Div([
    html.H3('Please choose your preferred date range between 02-28-2013 and 01-22-2021'), 
    html.P('(Note that a small date range is required for full functionality with the select and hovering tools)')
])
cali_second_row = html.Div(style={'columnCount': 2}, children=[cali_map, cali_map_table])
cali_map_div = html.Div(id = 'calmap', children=[label_cali_map, date_picker_row, cali_second_row])
# End of Incident Page


# County Incident Page
county_map = dcc.Graph(id='county_map', style={'width':'100%'})
county_pie = dcc.Graph(id='county_pie', style={'width':'100%'})

county_map_div = html.Div(id='county_map_div', style={'border':'2px #f2f2f2 solid'}, children=[html.H4('County Incident Frequency'),county_map])
county_pie_div = html.Div(id='county_pie_div', style={'border':'2px #f2f2f2 solid'}, children=[html.H4('County Incident Distribution'),county_pie])

label_county_map = html.Div(html.H3('Please choose your preferred date range between 02-28-2013 and 01-22-2021'))
second_row = html.Div(style={'columnCount': 2}, children=[county_map_div, county_pie_div])
county_div = html.Div(id = 'countymap', children=[label_county_map, date_picker_row, second_row])
# End of County Incident Page


# County-based Prediction Page
county_prediction = dcc.Graph(id='county_prediction', style={'width':'100%'})

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

month_picker_row = html.Div(style={'textAlign': 'center', 'padding-bottom':'2rem'}, children=[html.Div(children='Query a Month:'), month_picker_slider])

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

pred_table = dash_table.DataTable(
    style_table={
        'height': 550,
        'overflowY': 'scroll',
        'width': '100%'
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

## Number of Predicted Incidents
county_prediction_div = html.Div(id = 'pred-map', children=[county_prediction])
pred_subdiv = html.Div(style={'columnCount': 2}, children=[county_prediction_div, pred_table])
pred_div = html.Div(id = 'pred', children=[month_picker_row, county_dropdown, html.H3(className='county_graph_title',children=[f'Number of Predicted Incidents']), pred_subdiv])

## Past Incident Trend
fire_trend = dcc.Graph(id='fire-trend')
title_trend = html.Div(html.H2('How is the incident trend in past years? ', className='hh'),style={'margin-bottom':0})
label_trend = html.Div(html.H3('Please choose your preferred time range'))
trend_picker = html.Div(children = [range_slider, county_dropdown2], style={'color':'#04AA6D', 'padding-top':'1rem','padding-bottom':'2rem'})
trend_container = html.Div(children=[label_trend, trend_picker, fire_trend], style={'padding': '10px'})
fire_trend_div = html.Div(id='trend', style={'padding': '0px', 'columnCount': 1}, children=[title_trend, trend_container])
# End of County-based Prediction Page 



# Geo Location Based Prediction
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

month_picker_row2 = html.Div(style={'textAlign': 'center', 'padding-bottom':'2rem'}, children=[html.Div(children='Query a Month:'), month_picker_slider2])
th = daq.Thermometer(id = 'th', value=0.00, min=0.00, max=100, showCurrentValue=True, width=20, height=450, label='Risk Percentage')

label_cali_map2 = html.Div(html.H3(''),style={'margin-bottom':5, 'margin-left':5})
cali_map2 = dl.Map([dl.TileLayer(), dl.LayerGroup(id="layer")], id='map-id', style={'width':'100%', 'height':550}, center=[37.219306366090116, -119.66673872628975], zoom=5)
cali_map_subdiv2 = html.Div(id = 'cal-map2',style={'columnCount': 2}, children=[cali_map2, th])
cali_map_div2 = html.Div(id = 'calmap2', children=[label_cali_map2, cali_map_subdiv2])
pred_div2 = html.Div(id = 'pred', children=[month_picker_row2, html.H3(className='county_graph_title', children=[f'Please pick a point from the map below']), cali_map_div2])
# End of Geo Located Based Prediction


# Building App 
app.title = 'Cal Fire Dashboard'
app.layout = html.Div(children=[dcc.Location(id='url', refresh=False), header, navbar, html.Div(id='page-content', children=[prompt_message_container, our_services])])


# Observer Functions

@app.callback(
   dash.dependencies.Output(component_id='desc_heading', component_property='children'), [dash.dependencies.Input('incident_map', 'n_clicks'),
   dash.dependencies.Input('lmcounty', 'n_clicks'),
   dash.dependencies.Input('lmp1', 'n_clicks'),
   dash.dependencies.Input('lmp2', 'n_clicks')])
def show_heading(incident_map, lmcounty, lmp1, lmp2):
    ctx = dash.callback_context
    div_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (incident_map==None and lmcounty==None and lmp1==None and lmp2==None) or (incident_map%2==0 and lmcounty%2==0 and lmp1%2==0 and lmp2%2==0):
        return 'Learn More'
    elif div_id=='incident_map':
        return 'California Incident Map'
    elif div_id=='lmcounty':
        return 'County Incident Map'
    elif div_id=='lmp1':
        return 'County Based Prediction'
    elif div_id=='lmp2':
        return 'Geo Location Based Prediction'


@app.callback(
   dash.dependencies.Output(component_id='desc_subhead', component_property='children'), [dash.dependencies.Input('incident_map', 'n_clicks'),
   dash.dependencies.Input('lmcounty', 'n_clicks'),
   dash.dependencies.Input('lmp1', 'n_clicks'),
   dash.dependencies.Input('lmp2', 'n_clicks')])
def show_subheading(incident_map=0, lmcounty=0, lmp1=0, lmp2=0):
    ctx = dash.callback_context
    div_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if (incident_map==None and lmcounty==None and lmp1==None and lmp2==None) or (incident_map%2==0 and lmcounty%2==0 and lmp1%2==0 and lmp2%2==0):
        return ''
    elif div_id=='incident_map':
        return 'You can take a grasp of location, size and time of the previous incidents with just a glance'
    elif div_id=='lmcounty':
        return 'If you are looking for a tool to interact with the dataset from county point of view, this is the right tool for you.'
    elif div_id=='lmp1':
        return 'If you want to do prediction on the expected number of fires, based on the county and the month, this tool can help'
    elif div_id=='lmp2':
        return 'After using other tools in the dashboard, you may come up with some spots of interest, you can do an specific prediction on these spots by this tool'


@app.callback(
   dash.dependencies.Output(component_id='desc_text1', component_property='children'), [dash.dependencies.Input('incident_map', 'n_clicks'),
   dash.dependencies.Input('lmcounty', 'n_clicks'),
   dash.dependencies.Input('lmp1', 'n_clicks'),
   dash.dependencies.Input('lmp2', 'n_clicks')])
def show_text1(incident_map=0, lmcounty=0, lmp1=0, lmp2=0):
    ctx = dash.callback_context
    div_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (incident_map==None and lmcounty==None and lmp1==None and lmp2==None) or (incident_map%2==0 and lmcounty%2==0 and lmp1%2==0 and lmp2%2==0):
        return 'Click \"Learn more\" to find out how the different services work'
    elif div_id=='incident_map':
        return 'For using this tool, you need to set a time range, and the map will update based on what you chose. Radius of scattered points change proportional to the size of the incident.'
    elif div_id=='lmcounty':
        return 'For using this tool, you need to set a time range, and the county heat map will be updated. The heat map indicates number of incidents per county.'
    elif div_id=='lmp1':
        return 'For using this tool, you need to set a month and the county you are interested in, and the predicted number of fire occurences would be calculated based on a combined model of averaging past, Seasonal Arima, and Unobserved components.'
    elif div_id=='lmp2':
        return 'For using this tool, you need to set a month and pick the geo coordinates of the location you are interested in, and the probability of incident and the risk will be shown.'


@app.callback(
   dash.dependencies.Output(component_id='desc_text2', component_property='children'), [dash.dependencies.Input('incident_map', 'n_clicks'),
   dash.dependencies.Input('lmcounty', 'n_clicks'),
   dash.dependencies.Input('lmp1', 'n_clicks'),
   dash.dependencies.Input('lmp2', 'n_clicks')])
def show_text2(incident_map=0, lmcounty=0, lmp1=0, lmp2=0):
    ctx = dash.callback_context
    div_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (incident_map==None and lmcounty==None and lmp1==None and lmp2==None) or (incident_map%2==0 and lmcounty%2==0 and lmp1%2==0 and lmp2%2==0):
        return ''
    elif div_id=='incident_map':
        return 'You can use the toolkit above the map to select the incidents you are interested to investigate more. Further information about the chosen incidents will pop up in a table.'
    elif div_id=='lmcounty':
        return 'A pie chart is provided beside the map, to give the user a general insight of rate of incidents in all counties together.'
    elif div_id=='lmp1':
        return 'The location of the county will be shown on the map and the expected number of fire occurences would be shown in the table on the right.'
    elif div_id=='lmp2':
        return 'A widget with probability of incident will be shown based on the geo coordinates with location pinned in the map.'


@app.callback([dash.dependencies.Output("layer", "children"), dash.dependencies.Output("th", "value"), dash.dependencies.Output("th", "color")],
              [dash.dependencies.Input('map-id', 'click_lat_lng'), dash.dependencies.Input('month_slider2', 'value')])
def map_click(coordinates, month):
    global last_valid

    if coordinates == None:
        coordinates = last_valid
    else:
        last_valid = coordinates

    if coordinates[0] < 32.534156 or coordinates[0] > 42.009518 or coordinates[1] <-124.409591 or coordinates[1] > -114.131211:
        return [dl.Marker(position=coordinates, children=dl.Tooltip("({:.3f}, {:.3f})".format(*coordinates))), 100, '#666']
    val = utils.pred_func_geo(geo_all_data, geo_county_coordinates, geo_model, geo_encodings, geo_extreames, coordinates[0], coordinates[1], month)
    return [dl.Marker(position=coordinates, children=dl.Tooltip("({:.3f}, {:.3f})".format(*coordinates))), 100*val, '#FF3300']


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

    table_data = table_data[['incident_name' ,'incident_administrative_unit', 'incident_location']]
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
        zoom=4, height=550, size_max=22,  hover_name="incident_name", 
        color_discrete_sequence=['red'], center={'lon':-119.66673872628975, 'lat':37.219306366090116}, title='Wildfires Incident Map',
    )

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
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
        color_continuous_scale=px.colors.sequential.Reds, center={'lon':-119.66673872628975, 'lat':37.219306366090116},
        height=550
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
        height=550
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
        height=550, title=f'{calendar.month_name[month]}'
    )

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
            tickangle = -45
        )
    )
    return fig
    

# Navbar callback
@app.callback([dash.dependencies.Output('page-content', 'children'), dash.dependencies.Output('home-page-nav', 'className'), dash.dependencies.Output('cali-map-nav', 'className'), dash.dependencies.Output('county-map-nav', 'className'), dash.dependencies.Output('county-based-pred-nav', 'className'), dash.dependencies.Output('geo-based-pred-nav','className')],
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/app1':
        return [html.Div(id='app1-div', children=[cali_map_div]), "non-home","home-page","non-home","non-home","non-home"]
    elif pathname == '/app2':
        return [html.Div(id='app2-div', children=[county_div]), "non-home","non-home","home-page","non-home","non-home"]
    elif pathname == '/app3':
        return [html.Div(id='app3-div', children=[pred_div, fire_trend_div]), "non-home","non-home","non-home","home-page","non-home"]
    elif pathname == '/app4':
        return [html.Div(id='app4-div', children=[pred_div2]), "non-home","non-home","non-home","non-home","home-page"]
    else:
        return [html.Div(children=[prompt_message_container, our_services]), "home-page","non-home","non-home","non-home","non-home"]





if __name__ == '__main__':
    #Running App (Port 8050 by default)
    if 'PORT' in environ.keys():
        port = int(environ['PORT'])
    else:
        port = 8050
    app.run_server(host='0.0.0.0', debug=False, use_reloader=False, port=port, dev_tools_ui=False)  
