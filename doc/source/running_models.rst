.. _running-models:

Running a Thermal Model with ``acis_thermal_check``
---------------------------------------------------

``acis_thermal_check`` models are adapted to each use case and run from the
command line. This section provides a brief description on how to run the 
models, including what the various options are. 

.. _where-to-run:

Where to Run the Models From
============================

These models are run from a "Ska" Python stack. It can be one already installed
or it can be `one you installed yourself <https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users>`_.

To run as ``acisdude`` on the HEAD LAN, simply issue the command ``setska`` in
the terminal. If you want to run as yourself and you do not have this alias, 
you can set it up in your startup file:

.. code-block:: text

    # for csh/tsch

    alias setska 'eval `/proj/sot/ska3/flight/bin/flt_envs -shell tcsh -ska`'

    # for bash/zsh

    alias setska='eval `/proj/sot/ska3/flight/bin/flt_envs -shell bash -ska`'

The ACIS Ops Ska stack often has versions of ``acis_thermal_check`` that are more
up-to-date than in flight Ska. To use the ACIS Ops Ska stack as ``acisdude``, issue
the command ``acisska`` in the terminal. If you want to run as yourself and you 
do not have this alias, you can set it up in your startup file:

.. code-block:: text

    # for csh/tcsh

    alias acisska 'source /data/acis/mambaforge/etc/profile.d/conda.csh; \
        setenv SKA /proj/sot/ska; conda activate ska'
    
    # for bash

    alias acisska='eval "$(/data/acis/mambaforge/bin/conda shell.bash hook)"; \
        export SKA=/proj/sot/ska; conda activate ska'
    
    # for zsh
    
    alias acisska='eval "$(/data/acis/mambaforge/bin/conda shell.zsh hook)"; \
        export SKA=/proj/sot/ska; conda activate ska’

In either case, all commands (e.g. ``dpa_check``, ``dea_check``, etc.) should 
be in your path after running one of the two aliases.

.. _cmd-line-args:

Base Command-Line Arguments
===========================

The following is a brief description of the base collection of command-line 
arguments accepted by a model using ``acis_thermal_check``. Additional arguments
may be added by individual models in the call to, as further detailed in
:ref:`developing-models`. 

.. code-block:: text

    --outdir OUTDIR       Output directory. If it does not exist it will be created. Default: 'out'
    --backstop_file BACKSTOP_FILE
                          Path to the backstop file. If a directory, the backstop file will be searched for within this directory. Default: None
    --oflsdir OFLSDIR     Path to the directory containing the backstop file (legacy argument). If specified, it will override the value of the
                          backstop_file argument. Default: None
    --model-spec MODEL_SPEC
                          Model specification file. Defaults to the one included with the model package.
    --days DAYS           Days of validation data. Default: 21
    --run-start RUN_START
                          Reference time to replace run start time for regression testing. The default is to use the current time. Default: None
    --interrupt           Set this flag if this is an interrupt load.
    --traceback           Enable tracebacks. Default: True
    --pred-only           Only make predictions. Default: False
    --verbose VERBOSE     Verbosity (0=quiet, 1=normal, 2=debug)
    --T-init T_INIT       Starting temperature (degC). Default is to compute it from telemetry.
    --state-builder STATE_BUILDER
                          StateBuilder to use (kadi|acis). Default: acis
    --nlet_file NLET_FILE
                          Full path to the Non-Load Event Tracking file that should be used for this model run.
    --version             Print version

Running Thermal Models: Examples
================================

The most common application for any model based on ``acis_thermal_check`` is to
run the model for a load. In this case, the minimum command-line arguments are
the path to the backstop file and the output directory for the files:

.. code-block:: text

    [~]$ dpa_check --backstop_file=/data/acis/LoadReviews/2017/OCT1617/ofls --outdir=dpa_oct1617 

In this case, we only supplied the directory containing the backstop file, 
assuming that there is only one present. If the load being reviewed is a return 
to science from a shutdown, or a replan due to a TOO, or any other interrupt, 
the thermal model should be run with the ``--interrupt`` flag to ensure that the 
continuity is properly handled:

.. code-block:: text

    [~]$ psmc_check --backstop_file=/data/acis/LoadReviews/2017/AUG3017/ofls --interrupt --outdir=psmc_aug3017

By default, the initial temperature for the model will be set using an average 
of telemetry in a few minutes around the run start time. However, the model can
be started with a specific temperature value using the ``--T-init`` argument, 
which is assumed to be in degrees C:

.. code-block:: text

    [~]$ acisfp_check --backstop_file=/data/acis/LoadReviews/2017/OCT1617/ofls --outdir=acisfp_oct1617 --T-init=22.0

If necessary, thermal model runs can be run for a particular load for predictions only,
using the ``--pred-only`` flag:

.. code-block:: text

    [~]$ dea_check --backstop_file=/data/acis/LoadReviews/2017/AUG3017/ofls --outdir=dea_aug3017 --pred-only

Finally, if one wishes to run validation without prediction for a specific load,
simply omit the ``backstop_file`` argument. It may make sense here to supply a 
``run_start`` argument, if one wants a different time than the current time to 
validate:

.. code-block:: text

    [~]$ dpa_check --run-start=2019:300:12:50:00 --outdir=validate_dec2019

A page describing how to use these options if something goes wrong with the model runs
performed by the ACIS Ops ``lr`` script can be found at :ref:`what-to-do`.