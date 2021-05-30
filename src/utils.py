from os import name
import re
from dash_html_components.Tr import Tr
import numpy as np
import pandas as pd
from collections import defaultdict
from urllib.request import urlopen
import json
from datetime import datetime
import sys
import os
import statsmodels.api as sm
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans


with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/california-counties.geojson') as response:
    counties = json.load(response)

unique_ca_counties = set()
for feature in counties['features']:
    unique_ca_counties.add(feature['properties']['name'])

ca_counties_list = sorted(unique_ca_counties)

def getCountyNumbersDF(data, start_date, end_date):
    '''
    Returns a new pandas dataframe with county incident numbers from a specific date range

    :param data: the original dataframe from the Calfire csv
    :type data: pandas DF
    :param start_date: the start date which we are filtering by
    :type start_date: datetime object
    :param end_date: the end date which we are filtering by
    :type end_date: datetime object
    '''

    tmp_df = data[(data.date >= start_date) & (data.date <= end_date)]

    county_numbers = defaultdict(int)

    counties_in_range = tmp_df['incident_county']
    for affected_counties in counties_in_range:
        if isinstance(affected_counties, float): # check if nan
            continue

        split_counties = affected_counties.strip().split(',')

        for split_county in split_counties:
            if split_county in unique_ca_counties:
                county_numbers[split_county] += 1

    return pd.DataFrame({'county': county_numbers.keys(), 'Number of County Incidents': county_numbers.values()})

def get_single_CountyPrediction(all_df, queried_county, mode='running'):
    '''
    Returns a new pandas dataframe with predicted county incident numbers for a specific month
    :param queried_counties: the counties that are being queried
    :type queried_counties: str
    :type month: str
    '''

    assert isinstance(queried_county, str)
    assert queried_county in unique_ca_counties
    assert mode in ['running', 'eval']
    

    # select different mode
    if mode == 'running':
        df = all_df
    if mode == 'eval':
        all_df = pd.read_csv(file_name)
        df = all_df[all_df['year'] < 2020]
    
    res = df.groupby(by=['County', 'year', 'month']).mean()['size']
    selected_county_data = res[queried_county]

    # change 'year and month' to appropriate index and fill the missing year and month with zero
    timeLine = []
    starting_time = selected_county_data.index[0]
    max_time = (selected_county_data.index[-1][0] - selected_county_data.index[0][0])*12 + (selected_county_data.index[-1][1] - selected_county_data.index[0][1])
    fire_occurs = np.zeros(max_time+1)
    for i in range(len(selected_county_data.index)):
        diff = (selected_county_data.index[i][0] - starting_time[0])*12 + (selected_county_data.index[i][1] - starting_time[1])
        fire_occurs[diff] = selected_county_data.iloc[i]

    # naive approach
    past_res = df.groupby(by=['County', 'month']).mean()['size']
    county_past_res = past_res[queried_county]
    past_res = np.zeros(12)
    for i in range(12):
        if (i+1) in county_past_res.index:
            past_res[i] = county_past_res[i+1]
        else:
            past_res[i] = 0
    
    # construct Seasonal Arima Model
    sarima_model = sm.tsa.statespace.SARIMAX(fire_occurs)
    res_sarima = sarima_model.fit()
    forecast1 = res_sarima.get_prediction(end=sarima_model.nobs).predicted_mean
    last_month = selected_county_data.index[-1][1]
    predicted_month = np.zeros(12)
    for i in range(12):
        predicted_month[(last_month-i)%12] = forecast1[-i]

    # construct UnobservedComponents model
    uobc_model = sm.tsa.UnobservedComponents(fire_occurs, level='fixed intercept', seasonal=12, freq_seasonal=[{'period': 144, 'harmonics': 3}])
    res_uobc = uobc_model.fit()
    month = 12
    year = 2021
    diff = (year - starting_time[0])*12 + month - starting_time[1]
    forecast2 = res_uobc.get_prediction(end=diff).predicted_mean
    pred_uobc = forecast2[-12:]
    pred_uobc = np.array(list(map(lambda x: max(x,0), pred_uobc)))
    
    # ensemble the prediction
    alpha1 = 0.5
    alpha2 = 0.5
    final_res = alpha1*predicted_month + alpha2*past_res
    return [round(res) for res in final_res]



def getCountyPredictions(queried_counties, month):
    '''
    Returns a new pandas dataframe with predicted county incident numbers for a specific month
    :param queried_counties: the counties that are being queried
    :type queried_counties: str
    :param month: the month that is being queried
    :type month: int
    '''
    assert isinstance(queried_counties, list)
    assert all(bool(qc in unique_ca_counties) for qc in queried_counties)

    predicted_num = []
    print(queried_counties)
    for ct in queried_counties:
        fire_occ = get_single_CountyPrediction(ct)[month-1]
        predicted_num.append(fire_occ)

    # below is a placeholder
    return pd.DataFrame({'County': queried_counties, 'Predicted Number of Fires': predicted_num})


def getTrend(county, month, start_year, end_year):
    '''
    Returns a DataFrame fo number of incidents in 'month' for different years between start and end
    data -- DataFrame
    month -- intended month
    start_year -- the start year of inspection 
    end_year -- the end year of inspection 
    '''

    assert isinstance(county, str)
    assert county in unique_ca_counties

    assert 1 <= month <= 12
    assert start_year >= 1969
    assert end_year <= 2021
   
    path = Path(os.getcwd()).parent.absolute()
    file_name = os.path.join(path, 'data/fire_occurrances_data.csv')
    df = pd.read_csv(file_name)
    res = df.groupby(by=['County', 'year', 'month']).mean()['size']
    selected_county_data = res[county]
    years = list(range(start_year, end_year+1))
    trend = np.zeros(len(years))
    for yr in years:
        if (yr, month) not in selected_county_data.index:
            trend[yr-start_year] = 0
        else:
            trend[yr-start_year] = selected_county_data[yr][month]
    print(pd.DataFrame({'year': years, 'count': trend}))
    return pd.DataFrame({'year': years, 'count': trend})

######## Prediction Model ##########

def get_countyInfo(county_coordinates, lat, lon):
    '''
    Returns best match county name for given latitude & longitude
    
    :param county_coordinates: the county wise co-ordinates 
    :type county_coordinates: dictionary of county as keys and co-ordinates as values
    :param lon: the longitude of the location of interest within California
    :type lon: float/int
    :param lat: the latitude of the location of interest within California
    :type lat: float/int
    :param month: the month of the year for which use want to check the danger of fire incident within California
    :type month: int
    '''

    dx = (county_coordinates['Alameda'][0]-lat)
    dy = (county_coordinates['Alameda'][1]-lon)
    minDist = dx*dx + dy*dy
    retCounty = 'Alameda'
    
    for k in county_coordinates:
        dx = (county_coordinates[k][0]-lat)
        dy = (county_coordinates[k][1]-lon)
        
        if (minDist > dx*dx + dy*dy):
            minDist = dx*dx + dy*dy
            retCounty = k

    return retCounty

def get_weatherInfo(all_data, county_coordinates, lat, lon, month):
    '''
    Returns weather information for the sample
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    :param county_coordinates: the county wise co-ordinates 
    :type county_coordinates: dictionary of county as keys and co-ordinates as values
    :param lon: the longitude of the location of interest within California
    :type lon: float/int
    :param lat: the latitude of the location of interest within California
    :type lat: float/int
    :param month: the month of the year for which use want to check the danger of fire incident within California
    :type month: int
    '''

    county = get_countyInfo(county_coordinates, lat, lon)
    grouped_data = all_data.groupby(['County','month']).mean()[['temperature (degC)','wind_speed (m/s)','total_precipitation (mm of water equivalent)','relative_humidity (0-1)','surface_pressure (Pa)','humidex (degC)']]
    return list(grouped_data.loc[county,month])

def get_hotspots(all_data):
    '''
    Returns hotspots centers which have high probability of wildfire occurunce
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    '''

    X = all_data[['incident_longitude', 'incident_latitude']]
    kmeans = KMeans(n_clusters=6, random_state=0).fit(X[X['incident_longitude']!=0])
    return kmeans.cluster_centers_

def dateEncoder(month_enc, month):
    '''
    Returns encoded features based on month 
    
    :param month_enc: the encodings for month
    :type month_enc: sklearn encoder
    :param month: the month of the year
    :type month: float/int
    '''

    return month_enc.transform([[month]]).toarray().reshape(-1)

def PosEncoder(cluster_centers, lat1, lon1, lat2, lon2):
    '''
    Returns feature vector based on latitude & longitude 
    By calculating distance btw the location and hotspots predicated from the original dataset.
    
    :param cluster_centers: the hotspots predicated from the original dataset.
    :type cluster_centers: list of floats
    :param lon: the longitude of the location of interest within California
    :type lon: float/int
    :param lat: the latitude of the location of interest within California
    :type lat: float/int
    '''

    # Taking care of special cases
    if(lat1==0):
        lat = lat2
        lon = lon2    
    else:
        lat = lat1
        lon = lon1

    return np.sqrt(np.sum((cluster_centers-np.array([lat,lon]))**2,axis=1))

def make_sample_features(all_data, encodings, extreames, weather_data, lat, lon, month):
    '''
    Returns feature required for wildfire predication
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    :param encodings: the month encodings
    :type encodings: sklearn encodigs
    :param extreames: the minimum and maximum values needed for data normalization
    :type extreames: list of float
    :param weather_data: the weather data like temp, humidity, wind speed needed for predication
    :type weather_data: list of floats
    :param lon: the longitude of the location of interest within California
    :type lon: float/int
    :param lat: the latitude of the location of interest within California
    :type lat: float/int
    :param month: the month of the year for which use want to check the danger of fire incident within California
    :type month: string
    '''

    # find all the hotspots
    cluster_centers = get_hotspots(all_data)      

    # get extreme points for data normalization
    weather_extreames = extreames[0]
    distace_extreames = extreames[1]

    # normlaize weather data
    tmp = [(c-a)/(b-a) for a,b,c in zip(weather_extreames[1], weather_extreames[0], weather_data)]
    tmp_pos = PosEncoder(cluster_centers, 0, 0, lat, lon)
    # normlaize distance data
    tmp.extend([(c-a)/(b-a) for a,b,c in zip(distace_extreames[1], distace_extreames[0], tmp_pos)])
    # add time data
    tmp.extend(dateEncoder(encodings,month))
    # add bias term
    tmp.insert(0,1)

    return tmp

def geo_model(model, model_features):
    '''
    Returns probability of wildfire, given a model and its features
    
    :param model: the model used for the prediction
    :type model: sklearn model
    :param model_features: the contex rich features generated for predication
    :type model_features: float (ranging from 0 to 1)
    
    '''
    # assert all((fi>=0 and fi<=1) for fi in model_features)
    
    feature = np.array(model_features).reshape(1, -1)
    return model.predict_proba(feature)[0][0]

def pred_func_geo(all_data, county_coordinates, model, encodings, extreames, lat, lon, month):
    '''
    Wrapper function that,
    Returns probability of safety from wildfire incidents given latitude, longitude and month of the year

    :param lon: the longitude of the location of interest within California
    :type lon: float/int
    :param lat: the latitude of the location of interest within California
    :type lat: float/int
    :param month: the month of the year for which use want to check the danger of fire incident within California
    :type month: int
    '''
    assert isinstance(month, int) and (int(month)>0 and int(month)<=12), 'Sanity Check for month!'
    assert isinstance(lon, float) or isinstance(lon, int), 'Sanity Check for longitude!'
    assert isinstance(lat, float) or isinstance(lata, int), 'Sanity Check for latitude!'

    sample_weather_data = get_weatherInfo(all_data, county_coordinates[0], lat, lon, int(month))
    all_features = make_sample_features(all_data, encodings[0], extreames[0], sample_weather_data, lat, lon, "{:0>2d}".format(month))

    prob = geo_model(model[0], all_features)
    print(f'probability of wildfire: {1-prob}')

    return 1-prob
