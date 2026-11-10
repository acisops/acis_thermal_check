.. _test_suite:

Using the ``acis_thermal_check`` Testing Framework
--------------------------------------------------

``acis_thermal_check`` includes a testing framework that includes both unit tests
of various functionalities, as well as regression tests which allow one to
develop tests for a given thermal model against a set of "gold standard" model 
outputs for a number of load weeks. This section describes the test suite, how 
to run it, how to add new loads for testing, and how to update the gold standard
model answers.

Regression Tests
================

When an ``acis_thermal_check`` model is run, it produces numerical outputs for 
model prediction and validation in addition to the plots and tables on the 
webpages. The ``acis_thermal_check`` regression testing framework compares output
from model runs against a set of "gold standard" stored outputs. The idea is that 
code developments should not change the values compared to those stored in the 
gold standard, or if they do, that the reasons for the changes are understood and 
deemed necessary (e.g., you found a bug, you added a feature to a model, etc.). 
This allows us to track the effect of code changes in a systematic way and flag 
those changes which are not expected to change results but do, so that bugs can 
be identified and fixed before merging the new code into master. 

Load Tests
++++++++++

The bulk of the regression tests consists of checking the outputs of
``acis_thermal_check`` runs against known correct answers. These consist of
prediction tests and validation tests. These are run for a number of previous
load scenarios, including loads which have a "normal" continuity with a previous
load and those which have continuity with some kind of "interrupt". We also set
the "now" time for the tests to be contemporaneous with the load in question.

For a given load, the prediction tests check the values in the ``temperatures.dat``
and ``states.dat`` files produced by the model run against those in the "gold
standard" versions of these files, and validation tests check the values in the
``validation_data.pkl`` file produced by the model run against the ones in the
"gold standard" version of this file. These tests are run for both the "ACIS" and
"kadi" state builders.

.. note::

    In the case of the ACIS FP model, an additional file ``earth_solid_angles.dat``
    is generated for the prediction tests and is checked against its gold standard
    answers.

Violations Tests
++++++++++++++++

Violations tests set up a thermal model run which is guaranteed to violate thermal
limits, often by setting those limits in such a way as to force a violation. It then 
checks that the violations which occur are the expected ones, including the start 
and stop times for the violations, the maximum or minimum temperatures for the 
violations, and (in the case of the focal plane model) the obsids. The "gold 
standard" answers for these tests are stored in a JSON file.

Observation Table Tests
+++++++++++++++++++++++

For the ACIS FP model, a table of observations and a number of properties which
determine the science data quality limit for those observations. Accordingly, there
are also regression tests that check the values stored in this table for a few
loads. The "gold standard" answers for these tests are stored in a JSON file.

Prediction and Validation Only Tests
++++++++++++++++++++++++++++++++++++

There are two additional regression tests for the 1DPAMZT model, which test the conditions
whether only predictions or validations are run. These generate the products for prediction
or validation only, and test that the other products are not generated.

Unit Tests
==========

At the current time, the only "unit" tests which do not check regression are related to
non-load events. The 1DPAMZT model tests in ``test_dpa_non_load.py`` check for correct
inclusion of non-load commands from NLET and non-load event files, and that the resulting
state histories and temperature predictions agree. The tests in ``test_nonload_cmds.py``
are for checking the outputs of particular non-load commands.

Running Tests
=============

Running the Entire ``acis_thermal_check`` Test Suite
++++++++++++++++++++++++++++++++++++++++++++++++++++

There are two equivalent ways to run the entire ``acis_thermal_check`` test 
suite. The first is to go to the root of the ``acis_thermal_check`` directory
and run ``py.test`` like so (this assumes you have the Ska environment 
activated):

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check # or wherever you put it

    [~]$ py.test -s acis_thermal_check

The ``-s`` flag is optionally included here so that the output has maximum
verbosity.

Normally, the outputs of the thermal model runs used in the tests are stored 
in a temporary directory which is discarded after the tests have been carried 
out. If you want to dump these outputs to a different location for later 
examination, use the ``test_root`` argument on the command line:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ py.test -s acis_thermal_check --test_root=/Users/jzuhone/test_outputs

You can also import the ``acis_thermal_check`` package from an interactive 
Python session and run the ``test()`` method on it to run all of the tests:

.. code-block:: pycon

    >>> import acis_thermal_check
    >>> acis_thermal_check.test()

Running the Test Suite for a Particular Model
+++++++++++++++++++++++++++++++++++++++++++++

If you only want to run the tests for a particular model, simply run the same
command, but specify the ``tests`` subdirectory appropriate to the model you
want to test:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/
    __init__.py  acisfp   cea          data  dpa         fep1_mong  regression_testing.py
    __pycache__  bep_pcb  conftest.py  dea   fep1_actel  psmc       test_nonload_cmds.py

    # Run all the 1PDEAAT tests only
    [~]$ py.test -s acis_thermal_check/tests/psmc

Running Specific Test Types
+++++++++++++++++++++++++++

If you only want to run certain types of tests for a particular model, you
can call ``py.test`` on the file containing those tests:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/dea
    __init__.py  answers             test_dea_acis.py  test_dea_viols.py
    __pycache__  dea_test_spec.json  test_dea_kadi.py

    # Run the ACIS state builder tests only for 1DEAMZT
    [~]$ py.test -s acis_thermal_check/tests/dea/test_dea_acis.py

    # Run the kadi state builder tests only for 1DEAMZT
    [~]$ py.test -s acis_thermal_check/tests/dea/test_dea_kadi.py

    # Run the violation tests only for 1DEAMZT
    [~]$ py.test -s acis_thermal_check/tests/dea/test_dea_viols.py

    # Run the non-load tests
    [~]$ py.test -s acis_thermal_check/tests/test_nonload_cmds.py

What Happens if Some or All of the Tests Fail? 
++++++++++++++++++++++++++++++++++++++++++++++

If you get errors or failures, you can investigate them by running with the 
``--test_root`` option (see above) and comparing the contents of the 
``temperatures.dat``, ``states.dat``, or ``validation_data.pkl`` files against
those in the "gold standard" answers. For example, if I wanted to investigate
failures in the 1DPAMZT model, I would first run with the ``--test_root`` option:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ py.test -s acis_thermal_check/tests/dpa --test_root=./test_dpa_outputs

    # list the output directory
    [~]$ ls test_dpa_outputs
    acis  kadi  non_load  pred_only  valid_only  viols

    # list the contents of the acis state builder tests
    [~]$ ls test_dpa_outputs/acis
    AUG1322A  DEC0825A  FEB0626A  JAN2624A  JUN0820A
    MAY0521A  MAY1123A  OCT2722A  SEP1922A

    # list the contents of the acis state builder tests for dpa
    [~]$ ls test_dpa_outputs/acis/AUG1322A/dpa
    1dpamzt.png             ccd_count_valid.png     index.rst             roll.png
    states.dat              validation_data.pkl     1dpamzt_valid.png     CR225_1108.backstop.hist
    pitch_valid.png         roll_valid.png          temperatures.dat      validation_quant.csv
    1dpamzt_valid_hist.png  html4css1.css           pitch_valid_hist.png  roll_valid_hist.png
    tscpos_valid.png        acis_thermal_check.css  index.html            pow_sim.png
    run.dat                 tscpos_valid_hist.png

    # now check the "gold standard" answers
    [~]$ ls acis_thermal_check/tests/dpa/answers
    AUG1322A  DEC0825A_viol.json  JAN2624A  MAY0521A  OCT2722A   SEP1922A
    DEC0825A  FEB0626A            JUN0820A  MAY1123A  pred_only  valid_only

    # Check the answers for the AUG1322A load for either the ACIS or kadi tests
    [~]$ ls acis_thermal_check/tests/dpa/answers/AUG1322A
    states.dat  temperatures.dat  validation_data.pkl

You can use Python or a diffing tool to check the ``states.dat`` or 
``temperatures.dat`` files, and you can use python to check the 
``validation_data.pkl`` file.

If you want to check the violations tests, then look at the values in the (say)
``DEC0825A_viol.json`` file and compare them to the ``index.rst`` file generated
under the ``viols`` directory where you specified the ``--test_root``:

.. code-block:: text

    # Check for the violations JSON file for DEC0825A
    [~]$ ls acis_thermal_check/tests/dpa/answers
    AUG1322A  DEC0825A_viol.json  JAN2624A  MAY0521A  OCT2722A   SEP1922A
    DEC0825A  FEB0626A            JUN0820A  MAY1123A  pred_only  valid_only

    # Check for the index.rst file run by the violations test
    [~]$ ls test_dpa_outputs/viols
    DEC0825A
    
    [~]$ ls test_dpa_outputs/viols/DEC0825A/dpa
    1dpamzt.png             ccd_count_valid.png     index.rst             roll.png
    states.dat              validation_data.pkl     1dpamzt_valid.png     CR342_0101.backstop.hist
    pitch_valid.png         roll_valid.png          temperatures.dat      validation_quant.csv
    1dpamzt_valid_hist.png  html4css1.css           pitch_valid_hist.png  roll_valid_hist.png
    tscpos_valid.png        acis_thermal_check.css  index.html            pow_sim.png
    run.dat                 tscpos_valid_hist.png

Updating the "Gold Standard" Answers
====================================

New "gold standard" answers for a given model may need to be generated for two
reasons. First, you may be making a new model and need to generate the initial 
set of answers. Second, if you are updating code and the regression tests failed
to pass for one or more models, but the failures are understood and they are due
to changes you made which need to become part of the software (such as a bugfix
or a feature enhancement), then the "gold standard" answers need to be updated.

To generate new answers for all of the models, go to the root of the 
``acis_thermal_check`` directory that you are working in, and run ``py.test`` 
with the ``--answer_store`` argument like so:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ py.test -s acis_thermal_check --answer_store

This will overwrite the old answers, but since they are also under git version 
control you will be able to check any differences before committing the new
answers. 

If you want to overwrite the answers for a single model, simply run the same
command, but specify the ``tests`` subdirectory appropriate to the model you
want to update:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/
    __init__.py  acisfp   cea          data  dpa         fep1_mong  regression_testing.py
    __pycache__  bep_pcb  conftest.py  dea   fep1_actel  psmc       test_nonload_cmds.py

    [~]$ py.test -s acis_thermal_check/tests/dpa --answer_store

.. _test_model_spec:

The Model Specification for Tests
=================================

A model specification file in JSON format is set aside for testing, and can be
different from the one currently in use for thermal models. It should only be
updated sparingly, usually if there are major changes to the structure of a
model.

If you need to update the model specification file, simply replace the current
version of the file in its respective directory:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/acisfp
    __init__.py  acisfp_test_spec.json  test_acisfp_acis.py         test_acisfp_kadi.py      test_acisfp_viols.py
    __pycache__  answers                test_acisfp_acis_obsids.py  test_acisfp_non_load.py

where in this case ``acisfp_test_spec.json`` is the file you want to replace. 

.. _adding_new_test_loads:

Adding New Loads for the Prediction and Validation Tests
========================================================

The tests of the prediction and validation outputs for the thermal models
run on a series of past loads. These are stored in a ``test_loads`` dictionary
in the ``regression_testing.py`` file in the ``acis_thermal_check/tests`` 
directory:

.. code-block:: python

    # Loads for regression testing
    test_loads = {
        "normal": ["JUN0820A", "SEP1922A", "DEC0825A"],
        "interrupt": [
            "MAY0521A",
            "AUG1322A",
            "OCT2722A",
            "MAY1123A",
            "JAN2624A",
            "FEB0626A",
        ],
    }
    all_loads = test_loads["normal"] + test_loads["interrupt"]

    hrc_loads = {"normal": ["SEP1922A", "SEP2622A"]}

    run_starts = {
        "AUG1322A": "2022:225:05:00:00.000",
        "JAN2624A": "2024:026:12:31:52.403",
        "OCT2722A": "2022:300:12:00:00.000",
    }

    now_times = {"JAN2624A": "2024:026:00:00:00"}

    nlets = {"AUG1322A", "JAN2624A"}

Note that the dictionary is split up into two lists, one for ``"normal"`` loads
and another for ``"interrupt"`` loads, the latter including loads which begin
after an interrupt of any kind, including safing actions, radiation replans, ToOs,
etc. If you want to add new loads to the list to be tested, simply add them to
either the ``"normal"`` or ``"interrupt"`` list as appropriate. There is a special
set of loads for the HRC cea model, which are specified in the ``hrc_loads``
dictionary.

Note also that there are a few dictionaries below those for the loads that are
supplementary and necessary for certain loads:

* ``run_starts``: This is a dictionary of load week / start time pairs that
  indicate what the value of the ``run_start`` parameter should be for this
  load test. This is especially sometimes necessary in the case where there
  is a non-load event in the command history before the load in question
  and one wants to set the start time to be sure to include or exclude it,
  depending on the needs of the test.
* ``now_times``: Similarly, this dictionary sets the "now time" (see above)
  for a subset of loads to control what non-load states are assumed to be
  included. If a load does not appear in this dictionary, the "now time" is
  set to one day before the time specified in the ``run_start`` parameter.
* ``nlets``: The standard NLET file in use for creating histories may not
  always be the "correct" one for the test load in question, since at the time
  the model was originally run for the load review the contents of the NLET file
  at that time may not have included events which happened later. If you want to
  recreate the situation at the time the model was originally run as precisely as
  possible, specify the name of the load in the ``nlets`` set and add the NLET file
  to the ``acis_thermal_check/tests/data/nlets`` directory, with the naming convention
  ``"TEST_NLET_{load_name}.txt"``, where ``"load_name"`` is of the form``"MAR0617A"``.
