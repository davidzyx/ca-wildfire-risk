from dash.testing.application_runners import import_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import numpy as np
import dash_table
from datetime import datetime, time
import calendar
import json
from os import path, environ

TIMEOUT_TIME = 30

def test_header(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)

    dash_duo.wait_for_element('#header', timeout=TIMEOUT_TIME)
    assert dash_duo.find_element('#header').text == 'California Wildfire Interactive Dashboard'

def test_tab_cal(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to cali map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#cali-map-nav', 1)

    dash_duo.wait_for_element('#calmap', timeout=TIMEOUT_TIME)
    assert "Incidents on California map, based on size, date and location" in dash_duo.find_element('#calmap').text


def test_tab_county(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to county map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#county-map-nav', 1)

    dash_duo.wait_for_element('#app2-div', timeout=TIMEOUT_TIME)
    print(dash_duo.find_element('#app2-div').text)
    assert "Incidents in California by County" in dash_duo.find_element('#app2-div').text

def test_cal_date_update(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to cali map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#cali-map-nav', 1)

    dash_duo.wait_for_element('#calmap', timeout=TIMEOUT_TIME)
    
    #start date is updated to 11/01/2020 
    start_date_element = dash_duo.find_element('html > body > div > div > div:nth-of-type(3) > div > div > div:nth-of-type(3) > div:nth-of-type(2) > div > div > div > div:nth-of-type(1) > input')
    start_date_element.click()
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD0)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD1)

    # click away from the date widget
    dash_duo.multiple_click('#header', 1)

    # see the graphic update
    dash_duo.wait_for_element('#cali_map', timeout=TIMEOUT_TIME)


def test_cal_select(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to cali map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#cali-map-nav', 1)

    dash_duo.wait_for_element('#calmap', timeout=TIMEOUT_TIME)

    dash_duo.driver.maximize_window()
    action = ActionChains(dash_duo.driver)

    map_element = dash_duo.driver.find_element_by_class_name('js-plotly-plot')
    action.pause(2).move_to_element(map_element).perform()
    elements = dash_duo.driver.find_elements_by_class_name('modebar-btn')

    for element in elements:
        if element.get_attribute('data-title') == 'Box Select':
            # click on the box select element of the map
            action.click(element).perform()

    # create bounding box around some incidents
    action.click_and_hold(map_element).move_by_offset(-100, 100).release().pause(5).perform()

    dash_duo.wait_for_element('#cali_map_table', timeout=TIMEOUT_TIME)


def test_county_map_date_update(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to cali map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#county-map-nav', 1)

    dash_duo.wait_for_element('#county_map_div', timeout=TIMEOUT_TIME)
    
    #start date is updated to 11/01/2020 
    start_date_element = dash_duo.find_element('html > body > div > div > div:nth-of-type(3) > div > div:nth-of-type(2) > div:nth-of-type(2) > div > div > div > div:nth-of-type(1) > input')
    start_date_element.click()
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD0)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD1)

    # click away from the date widget
    dash_duo.multiple_click('#header', 1)

    # see the graphic update
    dash_duo.wait_for_element('#county_map_div', timeout=TIMEOUT_TIME)


def test_county_pie_date_update(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    
    # navigate to county map page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#county-map-nav', 1)

    dash_duo.wait_for_element('#county_pie_div', timeout=TIMEOUT_TIME)
    
    #start date is updated to 11/01/2020 
    start_date_element = dash_duo.find_element('html > body > div > div > div:nth-of-type(3) > div > div:nth-of-type(2) > div:nth-of-type(2) > div > div > div > div:nth-of-type(1) > input')
    start_date_element.click()
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.ARROW_RIGHT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD0)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.ARROW_LEFT)
    start_date_element.send_keys(Keys.BACKSPACE)
    start_date_element.send_keys(Keys.NUMPAD1)

    # click away from the date widget
    dash_duo.multiple_click('#header', 1)

    # see the graphic update
    dash_duo.wait_for_element('#county_pie_div', timeout=TIMEOUT_TIME)


def test_county_prediction(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    dash_duo.driver.maximize_window()

    # load page and navigate to page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#county-based-pred-nav', 1)

    dash_duo.wait_for_element('#pred', timeout=TIMEOUT_TIME)

    # find the elements to interact with 
    month_picker_element = dash_duo.find_element('#month_slider')
    county_picker_element = dash_duo.find_element('#county_dropdown')

    # click month 
    dash_duo.click_at_coord_fractions(month_picker_element, fx=0.3, fy=0.1)

    # click multiple counties
    action = ActionChains(dash_duo.driver)
    action.move_to_element(county_picker_element).click().move_by_offset(0, 50).click().pause(1).perform()
    action.move_to_element(county_picker_element).click().move_by_offset(0, 50).click().pause(1).perform()

    dash_duo.multiple_click('#header', 1)

    # see the graphic update
    dash_duo.wait_for_element('#pred_table', timeout=TIMEOUT_TIME)


def test_location_prediction(dash_duo):
    app = import_app('src.app')
    dash_duo.start_server(app)
    dash_duo.driver.maximize_window()

    # load page and navigate to page
    dash_duo.wait_for_page(url=None, timeout=TIMEOUT_TIME)
    dash_duo.multiple_click('#geo-based-pred-nav', 1)

    dash_duo.wait_for_element('#map-id', timeout=TIMEOUT_TIME)

    # find the elements to interact with 
    month_picker_element = dash_duo.find_element('#month_slider2')

    # click month 
    dash_duo.click_at_coord_fractions(month_picker_element, fx=0.3, fy=0.1)

    # click multiple counties
    dash_duo.multiple_click('#map-id', 1)
    dash_duo.multiple_click('#header', 1)

    # see the graphic update
    dash_duo.wait_for_element('#coordinate-click-id', timeout=TIMEOUT_TIME)