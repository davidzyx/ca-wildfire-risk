from os import name
import re
from dash_html_components.Tr import Tr
import numpy as np
import pandas as pd
from collections import defaultdict
from urllib.request import urlopen
import json
from datetime import datetime

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

def getCountyPredictions(queried_counties, month):
    '''
    Returns a new pandas dataframe with predicted county incident numbers for a specific month

    :param queried_counties: the counties that are being queried
    :type queried_counties: str
    :param month: the month that is being queried
    :type month: str
    '''

    #TODO: insert logic to predict using saved model
    # return pd.DataFrame({'County': queried_counties, 'Predicted Number of Fires': [model.predict(county, month) for county in queried_counties]})

    # below is a placeholder
    return pd.DataFrame({'County': queried_counties, 'Predicted Number of Fires': list(range(100))[:len(queried_counties)]})

def getTrend(data, month, start_year, end_year):
    '''
    Returns a DataFrame fo number of incidents in 'month' for different years between start and end
    data -- DataFrame
    month -- intended month
    start_year -- the start year of inspection 
    end_year -- the end year of inspection 
    '''

    data = data[data.date_start  >=  datetime.strptime(str(start_year)+'-01-01', '%Y-%m-%d')]
    data = data[data.date_start  <=  datetime.strptime(str(end_year)+'-01-01', '%Y-%m-%d')]
    data['month'] = [x.month for x in list(data.date_start)]
    data['year'] = [x.year for x in list(data.date_start)]
    data = data[data.month  ==  month]

    res =  (data['year'].value_counts())
 
    res = res.sort_index()
    res = res.to_frame(name='count')
    res.reset_index(inplace=True)
    res = res.rename(columns={'index': 'year'})
    return res




