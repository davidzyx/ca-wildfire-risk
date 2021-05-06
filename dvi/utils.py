import numpy as np
import pandas as pd


def date_to_int(string_date):
    """
    Converts 'date' to an integer for comparing purposes

    inputs:
    string_date -- date in the form of an string (ex: 2021-02-12)

    output:
    integer form of date (ex: 20210212)
    """
    splitted_string_date =  string_date.split('-')
    result = ''
    for element in splitted_string_date:
        result += element

    return int(result)



# data = pd.read_csv("https://www.fire.ca.gov/imapdata/mapdataall.csv")
# data=data[data['incident_dateonly_extinguished'].notnull()]
# int_time_column = data['incident_dateonly_extinguished'].apply(date_to_int)
# data['int_time'] = list(int_time_column)
# data = data[data.int_time > 20100000]


