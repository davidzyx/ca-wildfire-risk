import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.cluster import KMeans
import datetime
import requests
import json
import os
from joblib import dump
from geopy.geocoders import Nominatim
from pathlib import Path

def get_countyLocations():
    '''
    Returns latitudes & longitudes for each county
    '''

    geolocator = Nominatim(user_agent="user_agent")

    mp = {}
    Counties = ['Alameda','Alpine','Amador','Butte','Calaveras','Colusa','Contra Costa','Del Norte','El Dorado','Fresno','Glenn','Humboldt','Imperial','Inyo','Kern','Kings','Lake','Lassen','Los Angeles','Madera','Marin','Mariposa','Mendocino','Merced','Modoc','Mono','Monterey','Napa','Nevada','Orange','Placer','Plumas','Riverside','Sacramento','San Benito','San Bernardino','San Diego','San Francisco','San Joaquin','San Luis Obispo','San Mateo','Santa Barbara','Santa Clara','Santa Cruz','Shasta','Sierra','Siskiyou','Solano','Sonoma','Stanislaus','Sutter','Tehama','Trinity','Tulare','Tuolumne','Ventura','Yolo','Yuba']
    for cnty in Counties:
        location = geolocator.geocode(cnty)
        mp[cnty] = ( location.latitude,location.longitude)

    return mp

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


def get_extreames_weatherInfo(all_data):
    '''
    Returns Returns min & max values for data normalization of weather data
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    '''

    tmp = all_data[['temperature (degC)','wind_speed (m/s)','total_precipitation (mm of water equivalent)','relative_humidity (0-1)','surface_pressure (Pa)','humidex (degC)']].values

    Max = list(np.max(np.array(tmp),axis=0))
    Min = list(np.min(np.array(tmp),axis=0))

    return Max, Min

def get_extreames_positionalInfo(cluster_centers, all_data):
    '''
    Returns Returns min & max values for data normalization of positional data
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    '''

    tmp1 = all_data[['incident_latitude','incident_longitude','latitude','longitude']].values
    tmp2 = [PosEncoder(cluster_centers, xi[0],xi[1],xi[2],xi[3]) for xi in tmp1]

    Max = list(np.max(np.array(tmp2),axis=0))
    Min = list(np.min(np.array(tmp2),axis=0))

    return Max, Min

def get_encodings(all_data):
    '''
    Returns encodings for non-numerical data
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    '''

    # one Hot Encodings for Non-numerical data
    month_enc = OneHotEncoder(handle_unknown='ignore')
    month_enc.fit(np.array(list(all_data['month'])).reshape(-1,1))

    return month_enc

def make_features(all_data):
    '''
    Returns processed feature and information required from the cleaned data for model training
    
    :param all_data: cleaned and processed data set used for the whole application
    :type all_data: pandas DF
    '''

    # find all the hotspots
    cluster_centers = get_hotspots(all_data)

    # one Hot Encodings for Non-numerical data
    encodings = get_encodings(all_data)

    # feature selection
    X_data = all_data[['date','incident_latitude','incident_longitude','latitude','longitude','temperature (degC)','wind_speed (m/s)','total_precipitation (mm of water equivalent)','relative_humidity (0-1)','surface_pressure (Pa)','humidex (degC)']].values
    
    # get extreme points for data normalization
    weather_extreames = get_extreames_weatherInfo(all_data)
    distace_extreames = get_extreames_positionalInfo(cluster_centers, all_data)

    X = []
    for xi in X_data:
        # normlaize weather data
        tmp = [(c-a)/(b-a) for a,b,c in zip(weather_extreames[1], weather_extreames[0], list(xi[5:]))]
        tmp_pos = PosEncoder(cluster_centers, xi[1],xi[2],xi[3],xi[4])
        # normlaize distance data
        tmp.extend([(c-a)/(b-a) for a,b,c in zip(distace_extreames[1], distace_extreames[0],tmp_pos)])
        # add time data
        tmp.extend(dateEncoder(encodings,xi[0]))
        # add bias term
        tmp.insert(0,1)
        X.append(tmp)

    return X, encodings, (weather_extreames, distace_extreames)

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

def train(all_data):
    model_data = all_data.dropna()

    model_X, encodings, extreames = make_features(all_data)
    model_y = all_data['y'].values
    
    # split test and train
    X_train, X_test, y_train, y_test = train_test_split(model_X, model_y, test_size=0.2, shuffle=True)
    
    # build model
    LR = LogisticRegression(max_iter=1000, class_weight='balanced').fit(X_train, y_train.reshape(-1))

    # test
    y_pred = LR.predict(X_test)
    acc = sum((y_pred == y_test.reshape(-1)))/len(y_pred)

    print(f'model: Logistic Regression\tacc: {acc}')
    return LR, encodings, extreames

def geo_model(model, model_features):
    '''
    Returns probability of wildfire, given a model and its features
    
    :param model: the model used for the prediction
    :type model: sklearn model
    :param model_features: the contex rich features generated for predication
    :type model_features: float (ranging from 0 to 1)
    
    '''
    assert all((fi>=0 and fi<=1) for fi in model_features)
    
    feature = np.array(model_features).reshape(1, -1)

    return model.predict_proba(feature)[0][0]

def pred_func_geo(lat, lon, month):
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

    path = Path(os.getcwd()).parent.absolute()
    file_name = os.path.join(path, 'data/final_data.csv')
    all_data = pd.read_csv(file_name)

    county_coordinates = np.load(os.path.join(path, 'data/county_positions.npy'),  allow_pickle=True)
    model = np.load(os.path.join(path, 'data/geo_model.npy'),  allow_pickle=True)
    encodings = np.load(os.path.join(path, 'data/encodings.npy'),  allow_pickle=True)
    extreames = np.load(os.path.join(path, 'data/extreames.npy'),  allow_pickle=True)

    sample_weather_data = get_weatherInfo(all_data, county_coordinates[0], lat, lon, int(month))
    all_features = make_sample_features(all_data, encodings[0], extreames[0], sample_weather_data, lat, lon, "{:0>2d}".format(month))

    prob = geo_model(model[0], all_features)
    print(f'probability of wildfire: {1-prob}')

    return 1-prob

def model_init():
    '''
    Initailizes model training and saves processed information for model evalutaion
    '''
    path = Path(os.getcwd()).parent.absolute()
    file_name = os.path.join(path, 'data/final_data.csv')
    all_data = pd.read_csv(file_name)

    model, encodings, extreames = train(all_data)
    county_coordinates = get_countyLocations()

    np.save(os.path.join(path, 'data/county_positions.npy'), [county_coordinates])
    np.save(os.path.join(path, 'data/geo_model.npy'), [model])
    np.save(os.path.join(path, 'data/encodings.npy'), [encodings])
    np.save(os.path.join(path, 'data/extreames.npy'), [extreames])

    # testing
    month = '03'
    lat, lon = 37.706700, -121.834125

    sample_weather_data = get_weatherInfo(all_data, county_coordinates, lat, lon, int(month))
    all_features = make_sample_features(all_data, encodings, extreames, sample_weather_data, lat, lon, month)

    geo_model(model, all_features)


if __name__ == '__main__':
    model_init()