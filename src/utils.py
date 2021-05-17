import numpy as np
import pandas as pd
from collections import defaultdict
from urllib.request import urlopen
import json

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


