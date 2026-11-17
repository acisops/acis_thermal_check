.. _how-it-works:

How ``acis_thermal_check`` Works
--------------------------------

The Model Check Tools
=====================

``acis_thermal_check`` is a library that is utilized by various tools to run 
ACIS and HRC thermal models and produce web pages for prediction and validation. 
The current tools which use ``acis_thermal_check`` for load review are:

* ``dpa_check`` for the 1DPAMZT model
* ``dpamyt_check`` for the 1DPAMYT model
* ``dea_check`` for the 1DEAMZT model
* ``psmc_check`` for the 1PDEAAT model
* ``acisfp_check`` for the ACIS Focal Plane model
* ``cea_check`` for the HRC CEA model

These tools run models for the BEP and FEP models which are not currently used
for flight, but are still run at every load review:

* ``fep1_mong_check`` for the FEP1 Mongoose model
* ``fep1_actel_check`` for the FEP1 Actel model
* ``bep_pcb_check`` for the BEP PCB model

Directions on how to run these models can be found at :ref:`running-models`. 

The Web Pages
=============

The web pages that are produced by ``acis_thermal_check`` generate plots and
other information for prediction and validation. 

Prediction plots are used to show the thermal behavior of a particular 
component for a load. If a violation of a planning limit occurs, these 
violations are flagged on the page, including the time of the violation and 
the maximum or minimum temperature reached. 

Validation plots are used to compare model outputs of the temperature and other
quantities vs. actual past data which was telemetered from the spacecraft. 
Histograms of data - model errors are shown and error quantiles are also listed.

Example web pages for the most recent load review can be found
`here <https://asc.harvard.edu/acis/Thermal/index.html>`_. 

The ``StateBuilder`` Class
==========================

The inputs for a thermal model include commanded states, such as attitude
quaternions, CCD count, FEP count, etc. For the load under review, these are
determined from the backstop file for that load. However, given the fact that we
need to begin the thermal model propagation before the load starts to "wash out"
any errors in the initial condition, we need to begin the propagation before the
load starts. In order to do that, we need the commanded states. 
``acis_thermal_check`` provides two different ways to construct a state history
in the ``StateBuilder`` class: the "kadi" ``StateBuilder`` (the default) and the
"ACIS" ``StateBuilder``. The "kadi" ``StateBuilder`` uses kadi commands from both
mission history, including the
`Chandra Command Events Sheet <https://docs.google.com/spreadsheets/d/19d6XqBhWoFjC-z1lS1nM6wLE_zjr4GYB1lOvrEGCbKQ/edit?gid=0#gid=0>`_,
and a backstop file to construct a history of states. The "ACIS" ``StateBuilder``
constructs a history of states using a series of backstop files from previous loads,
as well as any information from the Non-Load Event Tracker (NLET) file in case of
an interrupted load. This ``StateBuilder`` requires the full ``/data/acis/LoadReviews``
structure, at least for the last several loads. In theory, both ``StateBuilder``
types should give the same results if the sources for the states are fully updated,
but there may be small differences if a command history includes non-load commands
that may have been entered slightly differently in the NLET file and the Chandra
Command Events Sheet.

.. warning::

    As of autumn 2026 the "ACIS" ``StateBuilder`` is deprecated. The HRC CEA
    model cannot use the "ACIS" ``StateBuilder``.
