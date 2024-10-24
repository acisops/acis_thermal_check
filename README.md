`acis_thermal_check`
====================

`acis_thermal_check` is a library which provides the tools to use and maintain
*Chandra* thermal models.  More specifically, `acis_thermal_check` generates 
backstop load review outputs (in the form of web pages) for checking ACIS 
temperature predictions such as 1DEAMZT, 1DPAMZT, 1PDEAAT, the ACIS focal plane 
temperature, and the HRC CEA model. It also generates model validation plots for 
these temperatures comparing model values to telemetry for recent times, to 
evaluate model performance.

Prediction plots are used to show the thermal behavior of a particular 
component for a load. If a violation of a planning limit occurs, these 
violations are flagged on the page, including the time of the violation and 
the maximum or minimum temperature reached. 

Validation plots are used to compare model outputs of the temperature and other
quantities vs. actual past data which was telemetered from the spacecraft. 
Histograms of data - model errors are shown and error quantiles are also listed.

More information on how to use `acis_thermal_check` can be found in the 
[documentation](https://cxc.cfa.harvard.edu/acis/acis_thermal_check). Example 
web pages for the most recent load review can be found 
[here](https://asc.harvard.edu/acis/Thermal/index.html). 
