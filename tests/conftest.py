# add this in the conftest.py under tests folder
from selenium.webdriver.chrome.options import Options

def pytest_setup_options():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    return options
