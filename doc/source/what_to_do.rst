.. _what-to-do:

What to Do When Something Goes Wrong?
-------------------------------------

The ACIS Load Review script ``lr`` runs the thermal models that are used to
approve a load for flight. Occasionally, one of these model scripts might fail 
to run. If help is not available to determine a reason for the failure, these
are some steps that may be taken, which involve running the model script manually
outside of ``lr``. Many of these scenarios invovle running the model script with
additional flags, all of which are detailed in :ref:`cmd-line-args`, but we provide
some examples here.

Running a Model Manually
========================

Log into a HEAD workstation as ``acisdude`` and run the command ``setska``. From the 
home directory (or any other directory writable by ``acisdude``), you can run a
model script like ``acisfp_check``:

.. code-block:: text

    barth-v.acisdude:~[104]> setska

    barth-v.acisdude:~[105]> acisfp_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --out=test_jan2725_fp

where ``--oflsdir`` is the directory where the backstop and other necessary files are
located, and ``--out`` is the name of the directory into which the files will be output.

Running Predictions Only
========================

``acis_thermal_check`` scripts run both predictions and validations, the latter so we can 
check the performance of the model against actual telemetry on a regular basis. If the code 
is crashing during the validation phase, it is possible to run with predictions only. This
can be done with the ``--pred-only`` flag:

.. code-block:: text

    barth-v.acisdude:~[105]> dpa_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --pred-only --out=test_jan2725_dpa

Running on Loads that are Interrupted
=====================================

If the load under review is a return to science from a shutdown, or a replan due to a TOO, then 
you would have run ``lr`` with the ``--break`` flag. If you have to run a model manually under
these circumstances, you should use the ``--interrupt`` flag:

.. code-block:: text

    barth-v.acisdude:~[105]> dpa_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --interrupt --out=test_jan2725_dpa

Running with the ``kadi`` State Builder
=======================================

The ``"acis"`` State Builder constructs a history of states using a series of backstop files and
the Non-Load Event Tracker (NLET) file. This is the default state builder used with 
``acis_thermal_check``, and is used by ``lr``. The ``"kadi"`` state builder constructs a history 
of states using ``kadi``-based commands (though even for the ``"acis"`` state builder ``kadi`` is
used to get states from commands). If there is a suspicion that something has gone wrong with the 
ACIS continuity files that the ``"acis"`` state builder uses to construct a mission history, then 
the script can be run with the ``"kadi"`` state builder using the ``--state-builder`` flag:

.. code-block:: text

    barth-v.acisdude:~[105]> dea_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --state-builder=kadi --out=test_jan2725_dea

Changing the Run Start Time
===========================

By default, the run start time is set to the current time. If the model is crashing 
because of problems with telemetry or commanded states at a particular time, the run
start time can be set by hand:

.. code-block:: text

    barth-v.acisdude:~[105]> psmc_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --run-start=2025:027:00:00:00 --out=test_jan2725_psmc

Changing the Initial Temperature
================================

By default, the initial temperature for the model will be set using an average 
of telemetry in a few minutes around the run start time. If there is an issue with
the telemetry at the run start time, the model can be started with a user-specified
temperature value using the ``--T-init`` argument, which is assumed to be in degrees C:

.. code-block:: text

    barth-v.acisdude:~[105]> dpa_check --oflsdir=/data/acis/LoadReviews/2025/JAN2725/ofls --out=test_jan2725_dpa --T-init=12.0

Copying Model Outputs to the Web Page Location
==============================================

Once you have run the model yourself, if you wish you can copy the model run files to 
the appropriate location for the web page (which is what ``lr`` would have done had it
run successfully). This is done with the ``copy_model_outputs`` script:

.. code-block:: text

    (ska) barth-v.acisdude:~[138]> copy_model_outputs --help
    usage: copy_model_outputs [-h] [--overwrite] [--dry_run] location load
    
    positional arguments:
      location     The location of the model files to copy
      load         The load name. Must be 8 characters, e.g. 'JAN2725A'
    
    options:
      -h, --help   show this help message and exit
      --overwrite  Overwrite existing files.
      --dry_run    Show what would have been done.
    
In general, after you have created the model files, you run the ``copy_model_outputs``
script like this:

.. code-block:: text

    barth-v.acisdude:~[106]> copy_model_outputs test_jan2725_fp JAN2725A
    
which, if it runs successfully, gives output like this:

.. code-block:: text

    Files to be copied are from a "acisfp" model run.
    Copied contents of test_jan2725_fp to /proj/web-cxc/htdocs/acis/FP_thermPredic/JAN2725/oflsa.

If the location to be copied to already has files, ``copy_model_outputs`` will refuse
to copy the files unless you use the ``--overwrite`` flag:

.. code-block:: text

    barth-v.acisdude:~[106]> copy_model_outputs test_jan2725_fp JAN2725A --overwrite

If you want to see what would be copied without actually doing anything, you can use
the ``--dry_run`` flag:

.. code-block:: text

    barth-v.acisdude:~[106]> copy_model_outputs test_jan2725_fp JAN2725A --dry_run

which, if it runs successfully, gives output like this:

.. code-block:: text

    Files to be copied are from a "acisfp" model run.
    Would have copied contents of test_jan2725_fp to /proj/web-cxc/htdocs/acis/FP_thermPredic/JAN2725/oflsa.

If the path to the model files does not exist, or if the directory exists but the 
appropriate files are not found, or if the script cannot determine the model type,
then it will report these errors with the necessary specificity.




