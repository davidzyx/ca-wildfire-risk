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

def get_single_CountyPrediction(queried_county):
    '''
    Returns a new pandas dataframe with predicted county incident numbers for a specific month
    :param queried_counties: the counties that are being queried
    :type queried_counties: str
    :type month: str
    '''

    assert isinstance(queried_county, str)
    assert queried_county in unique_ca_counties
    
    file_name = os.path.join(os.getcwd(), 'data/fire_occurrances_data.csv')
    df = pd.read_csv(file_name)
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
    alpha1 = 0.8
    alpha2 = 0.2
    final_res = alpha1*predicted_month + alpha2*pred_uobc
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
    
    file_name = os.path.join(os.getcwd(), 'data/fire_occurrances_data.csv')
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

def dummy_pred_func(lon, lat, month):
    return('to do')





