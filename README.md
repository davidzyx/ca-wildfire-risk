# ca-wildfire-risk

Interactive dashboard for assessing risks of wildfires in California

by Alakh Desai, Ashutosh Lohogaonkar, Jiawen Zeng, Nikhil Pathak, Parsa Assadi, Yuxin Zou

|               	    | __Link__                                                               	|
|-------------------	|------------------------------------------------------------------------	|
| __Demo (AWS)__    	| http://ca-wildfire-app-alb-1941565096.us-west-2.elb.amazonaws.com/home 	|
| __Demo (fly.io)__ 	| https://ca-wildfire-risk.fly.dev/                                      	|
| __Sphinx Doc__    	| https://davidzyx.github.io/ca-wildfire-risk                            	|
| __Docker Image__   	| https://hub.docker.com/repository/docker/davidzz/ca-wildfire            |

## Documentation

Project description along with function definitions can be found [here](https://davidzyx.github.io/ca-wildfire-risk)

## Data

1. [CAL FIRE](https://www.fire.ca.gov/) for wildfire history
2. [oikolab](https://oikolab.com/) for weather history

## Frameworks and Tools

- Dash (plot.ly)
- [mapbox](https://www.mapbox.com/)
- Scikit-learn
- Selenium
- Sphinx
- Github Actions
- Docker
- AWS ECS with Fargate

## Code Coverage

```
$ docker run --rm -e MAPBOX_TOKEN="***" "davidzz/ca-wildfire:dd86ff6" \
  python -m pytest --cov=src --headless -vv tests/
============================= test session starts ==============================
platform linux -- Python 3.8.8, pytest-6.2.4, py-1.10.0, pluggy-0.13.1 -- /opt/conda/bin/python
cachedir: .pytest_cache
rootdir: /app
plugins: dash-1.20.0, sugar-0.9.4, cov-2.12.1, mock-3.6.1, anyio-2.2.0
collecting ... collected 10 items

tests/test_app.py::test_header PASSED                                    [ 10%]
tests/test_app.py::test_tab_cal PASSED                                   [ 20%]
tests/test_app.py::test_tab_county PASSED                                [ 30%]
tests/test_app.py::test_cal_date_update PASSED                           [ 40%]
tests/test_app.py::test_cal_select PASSED                                [ 50%]
tests/test_app.py::test_county_map_date_update PASSED                    [ 60%]
tests/test_app.py::test_county_pie_date_update PASSED                    [ 70%]
tests/test_app.py::test_county_prediction PASSED                         [ 80%]
tests/test_app.py::test_location_prediction PASSED                       [ 90%]
tests/test_model.py::test_county_prediction PASSED                       [100%]

----------- coverage: platform linux, python 3.8.8-final-0 -----------
Name              Stmts   Miss  Cover
-------------------------------------
src/__init__.py       0      0   100%
src/app.py          229     43    81%
src/utils.py        175      3    98%
-------------------------------------
TOTAL               404     46    89%
```

## Architecture Illustration

![Architecture Diagram](https://i.imgur.com/Fvb9pyz.png)
