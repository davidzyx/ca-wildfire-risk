.. _county_based_prediction_marker:

County Based Predictions
************************
To better understand the underlying function calls for the prediction of fires based on user input county's and date, let us look
at an example first.

Example
=======
Suppose you want to predict the chances of fire for 4 different county's - *Napa* , *Fresno* , *Mariposa* , *Tulare*
for the month of June then this is the **result.** |pred_1|

Similarly, we can also have a look at the past trends for a particular county for the month of choosing. **Here** |pred_2|, we look at the number
of fires for the county of Napa in the month of June between 2010 and 2017

.. |pred_2| image:: /county_based_pred_2.PNG
            :scale: 5%

.. |pred_1| image:: /county_based_pred_1.PNG
            :scale: 5%

Dashboard elements and the functions used
=========================================
Now, a lot of things are happening over here. Let us look at them one by one.

1. Data frame with County and number of predicted fires data
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Upon selecting the county's the first thing we see is a table on the page right, which lists the individual county's selected
and the output of the model prediction which is nothing but the number of predicted fires. Obviously, the actual model for prediction
is important to understand. But, lets look at all the supporting functions first.

Display_pred_data
-----------------
This function calls the **getCountyPredictions()** on the backend to get to the predictions.

.. automodule:: src.app
    :members: display_pred_data

GetCountyPredictions
--------------------

.. automodule:: src.utils
    :members: getCountyPredictions

Get_Single_CountyPrediction
---------------------------
This is the function that performs the main predictive task. It combines the analytical output of three different models to predict. They
are **Naive approach** , **Seasonal Arima Model** , **Unobserved components model**.

*Naive approach*: Learn from the fire occurrences in the same month each year (basically average out previous data)

*Seasonal Arima*: Stands for autoregressive and moving average- predict the value by placing a moving window in analyzing the trend with the
nearby months and the shifted history.

*Unobserved components (UCM)*: decompose the time series data by three components: seasonal, trend and irregularity and assume a Gaussian noise
in each of the components, what it adds up is that it also consider the trend for the irregular pattern, which is left out by the previous two

.. automodule:: src.utils
    :members: get_single_CountyPrediction
    :noindex:


2. A visual location of the county's and a bar chart indicating relative severity
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. automodule:: src.app
    :members: update_county_prediction


3. A bar chart indicating past trends within specified year range for the chosen month
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. automodule:: src.app
    :members: update_trend

.. automodule:: src.utils
    :members: getTrend
    :noindex:

Expected
