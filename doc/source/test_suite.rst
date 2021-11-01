.. _test_suite:

Using the ``acis_thermal_check`` Regression Testing Framework
-------------------------------------------------------------

``acis_thermal_check`` includes a regression test fremework which allows one to
develop tests for a given thermal model against a set of "gold standard" model 
outputs for a number of load weeks. This section describes the test suite, how 
to run it, how to add new loads for testing, and how to update the gold standard
model answers.

An Overview of ``acis_thermal_check`` Regression Testing
========================================================

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

The different types of tests will now be detailed:

ACIS State Builder Tests
++++++++++++++++++++++++

The ACIS state builder constructs a history of commands and states prior to the
load using the ``backstop_history`` package. There are two basic kinds of tests 
that are run for the ACIS state builder: prediction tests and validation tests.
These are run for a number of previous load scenarios. For a given load, the 
prediction tests check the values in the ``temperatures.dat`` and ``states.dat``
files produced by the model run against those in the "gold standard" versions of 
these files. The validation tests check the values in the ``validation_data.pkl``
file produced by the model run against the ones in the "gold standard" version of
this file. 

kadi State Builder Tests
++++++++++++++++++++++++

The kadi state builder tests run the same prediction and validation comparisons
as the ACIS state builder tests, except using the kadi state builder which 
constructs the history prior to the start of the load using commands from the 
kadi database. 

Violations Tests
++++++++++++++++

Violations tests set up a thermal model run which is guaranteed to violate thermal
limits, often by setting those limits lower than their real values. It then checks
that the violations which occur are the expected ones, including the start and stop
times for the violations, the maximum or minimum temperatures for the violations,
and (in the case of the focal plane model) the obsids. The "gold standard" answers
for these tests are stored in a JSON file.

The Model Specification for Tests
=================================

A model specification file in JSON format is set aside for testing, and can be
different from the one currently in use for thermal models. It should only be
updated sparingly, usually if there are major changes to the structure of a 
model. For directions on how to update, see :ref:`update_model_spec`.

Running the Entire ``acis_thermal_check`` Test Suite
====================================================

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
=============================================

If you only want to run the tests for a particular model, simply run the same
command, but specify the ``tests`` subdirectory appropriate to the model you
want to test:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/
    __init__.py  acisfp  conftest.py  dea  fep1actel  psmc
    __pycache__  beppcb  data         dpa  fep1mong   regression_testing.py

    # Run all the 1PDEAAT tests only
    [~]$ py.test -s acis_thermal_check/tests/psmc

Running Specific Test Types
===========================

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

What Happens if Some or All of the Tests Fail? 
==============================================

Most warnings when running the tests are normal and benign. At this current time,
they typically look like this:

.. code-block:: text

    ../../miniconda3/envs/ska/lib/python3.8/site-packages/ipyparallel/client/view.py:8
    /Users/jzuhone/miniconda3/envs/ska/lib/python3.8/site-packages/ipyparallel/client/view.py:8: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
    import imp

    acis_thermal_check/tests/dpa/test_dpa_acis.py::test_prediction[MAR0617A]
    <frozen importlib._bootstrap>:219: RuntimeWarning: numpy.ufunc size changed, may indicate binary incompatibility. Expected 192 from C header, got 216 from PyObject

Any other warnings should be reported at the 
`acis_thermal_check issues page <https://github.com/acisops/acis_thermal_check>`_.

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
    acis  kadi  viols

    # list the contents of the acis state builder tests
    [~]$ ls test_dpa_outputs/acis
    APR0217B  AUG3017A  JUL3117B  MAR0817B  MAR1517B  SEP0417A
    AUG2517C  JUL2717A  MAR0617A  MAR1117A  MAR2017E  SEP0917C

    # list the contents of the acis state builder tests for 
    [~]$ ls test_dpa_outputs/acis/APR0217B
    1dpamzt.png               index.rst             states.dat
    1dpamzt_valid.png         pitch_valid.png       temperatures.dat
    1dpamzt_valid_hist.png    pitch_valid_hist.png  tscpos_valid.png
    acis_thermal_check.css    pow_sim.png           tscpos_valid_hist.png
    ccd_count_valid.png       roll.png              validation_data.pkl
    CR092_0107.backstop.hist  roll_valid.png        validation_quant.csv
    html4css1.css             roll_valid_hist.png
    index.html                run.dat

    # now check the "gold standard" answers
    [~]$ ls acis_thermal_check/tests/dpa/answers
    APR0217B  AUG3017A  JUL3018A_viol.json  MAR0617A  MAR1117A  MAR2017E  SEP0917C
    AUG2517C  JUL2717A  JUL3117B            MAR0817B  MAR1517B  SEP0417A
    
    # Check the answers for the APR0217B load for either the ACIS or kadi tests
    [~]$ ls acis_thermal_check/tests/dpa/answers/APR0217B
    states.dat  temperatures.dat  validation_data.pkl

You can use Python or a diffing tool to check the ``states.dat`` or 
``temperatures.dat`` files, and you can use python to check the 
``validation_data.pkl`` file.

If you want to check the violations tests, then look at the values in the (say)
``JUL3018A_viol.json`` file and compare them to the ``index.rst`` file generated
under the ``viols`` directory where you specified the ``--test_root``:

.. code-block:: text

    # Check for the violations JSON file for JUL3018A
    [~]$ ls acis_thermal_check/tests/dpa/answers
    APR0217B  AUG3017A  JUL3018A_viol.json  MAR0617A  MAR1117A  MAR2017E  SEP0917C
    AUG2517C  JUL2717A  JUL3117B            MAR0817B  MAR1517B  SEP0417A

    # Check for the index.rst file run by the violations test
    [~]$ ls test_dpa_outputs/viols
    JUL3018A
    
    [~]$ ls test_dpa_outputs/viols/JUL3018A
    1dpamzt.png               index.rst             states.dat
    1dpamzt_valid.png         pitch_valid.png       temperatures.dat
    1dpamzt_valid_hist.png    pitch_valid_hist.png  tscpos_valid.png
    acis_thermal_check.css    pow_sim.png           tscpos_valid_hist.png
    ccd_count_valid.png       roll.png              validation_data.pkl
    CR211_1004.backstop.hist  roll_valid.png        validation_quant.csv
    html4css1.css             roll_valid_hist.png
    index.html                run.dat

Updating the "Gold Standard" Answers
====================================

New "gold standard" answers for a given model may need to be generated for two
reasons. First, you may be making a new model and need to generate the initial 
set of answers. Second, if you are updating ACIS code and the regression tests 
failed to pass for one or more models, but the failures are understood and they 
are due to changes you made which need to become part of the software (such as 
a bugfix or a feature enhancement), then the "gold standard" answers need to be
updated. 

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
    __init__.py  acisfp  conftest.py  dea  fep1actel  psmc
    __pycache__  beppcb  data         dpa  fep1mong   regression_testing.py

    [~]$ py.test -s acis_thermal_check/tests/dpa --answer_store

.. _update_model_spec:

Updating the Model Specification File
=====================================

If you need to update the model specification file, simply replace the current
version of the file in its respective directory:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/acisfp
    __init__.py  acisfp_test_spec.json  test_acisfp_acis.py  test_acisfp_viols.py
    __pycache__  answers                test_acisfp_sql.py

where in this case ``acisfp_test_spec.json`` is the file you want to replace. 