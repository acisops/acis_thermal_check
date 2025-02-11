.. acis_thermal_check documentation master file

ACIS Thermal Model Tools (``acis_thermal_check``)
=================================================

Overview
--------

.. |Chandra_cmd_states| replace:: ``Chandra.cmd_states``
.. _Chandra_cmd_states: http://cxc.harvard.edu/mta/ASPECT/tool_doc/cmd_states/

.. |Ska_engarchive| replace:: ``Ska.engarchive``
.. _Ska_engarchive: http://cxc.cfa.harvard.edu/mta/ASPECT/tool_doc/eng_archive/

.. |xija| replace:: ``xija``
.. _xija: http://cxc.cfa.harvard.edu/mta/ASPECT/tool_doc/xija/

``acis_thermal_check`` is a library which provides the tools to use and maintain
*Chandra* thermal models.  More specifically, ``acis_thermal_check`` generates 
backstop load review outputs for checking ACIS temperatures such as 1DEAMZT, 
1DPAMZT, 1PDEAAT, the ACIS focal plane temperature, and the HRC CEA model. It 
also generates model validation plots for these temperatures comparing predicted 
values to telemetry for the previous three weeks.

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
       
   install
   how_it_works
   running_models
   developing_models
   test_suite
   what_to_do