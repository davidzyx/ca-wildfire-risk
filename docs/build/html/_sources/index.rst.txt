.. CA_Wildfire documentation master file, created by
   sphinx-quickstart on Fri May 21 16:18:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CA_Wildfire's documentation!
=======================================


Organization of the documentation
+++++++++++++++++++++++++++++++++

1. The first section that is there is a simple :ref:`overview <overview_marker>` . It talks about who the target user is, why is
this helpful and the tools provided for visualization and analysis.

2. The next 4 sections give a top-down approach understanding of the 4 services- what are the front end functions, which backend
functions they rely on etc. The basic structure of these 4 sections is similar - A *"How to use"* section which explains a sample
example followed by *"Dashboard elements and the functions used"* which takes a deep dive into each of the services.

3. The last section is :ref:`Source and Test Files module <modules_marker>`. It has two sub-modules - *Source code files* and
*Tests package*.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Overview
   california_incident_map
   County_incident_map
   County_based_prediction
   Geo_location
   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
