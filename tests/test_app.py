from dash.testing.application_runners import import_app
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import dash_table
from datetime import datetime
import calendar
import json
from os import path, environ

def test_no_errors(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)

    tmp = dash_duo.get_logs()
    print(tmp)
    assert tmp == [], "browser console should contain no error"

def test_header(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)

    dash_duo.wait_for_element('#header', timeout=5)
    assert dash_duo.find_element('#header').text == 'California Wildfire Interactive Dashboard'

def test_tab_cal(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    dash_duo.wait_for_page(url=None, timeout=5)
    dash_duo.multiple_click('#cali-map-nav', 1)

    dash_duo.wait_for_element('#calmap', timeout=10)
    assert "Incidents on California map, based on size, date and location" in dash_duo.find_element('#calmap').text


def test_tab_county(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    dash_duo.wait_for_page(url=None, timeout=5)
    dash_duo.multiple_click('#county-map-nav', 1)

    dash_duo.wait_for_element('#app2-div', timeout=10)
    print(dash_duo.find_element('#app2-div').text)
    assert "Incidents in California by County" in dash_duo.find_element('#app2-div').text