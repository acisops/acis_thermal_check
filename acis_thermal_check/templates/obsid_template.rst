ACIS Observations Table
-----------------------

Observations in {{bsdir}}

=====  =================  ==================  =======  ========  =================  =====
Obsid  CCDs               # of counts in seq  Grating  SIM-Z     Spectra Max Count  Limit
=====  =================  ==================  =======  ========  =================  =====
{% for eachobs in acis_obs %}
{{ eachobs.obsid }}  {{"{0: <17}".format(eachobs.ccds)}}  {{"{0: <18}".format(eachobs.num_counts)}}  {{eachobs.grating}}     {{eachobs.sim_z}}        {{"{0: <10}".format(eachobs.spectra_max_count)}}         {{eachobs.fp_limit}}
{% endfor %}
=====  =================  ==================  =======  ========  =================  =====
