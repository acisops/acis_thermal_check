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

"ACIS" State Builder Tests
++++++++++++++++++++++++++


SQL State Builder Tests
+++++++++++++++++++++++

The SQL state builder tests run the same prediction and validation comparisons
as the ACIS state builder tests, except using the SQL state builder which 

Violations Tests
++++++++++++++++

A model specification file in JSON format is set aside for testing, and can be
different from the one currently in use for thermal models. It should only be
updated sparingly, usually if there are major changes to the structure of a 
model.

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

    [~]$ py.test -s acis_thermal_check/tests/psmc

What Happens if Some or All of the Tests Fail? 
++++++++++++++++++++++++++++++++++++++++++++++

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

If you get errors or failures, you can investigate them by 

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

Updating the Model Specification File
=====================================

If you need to update the model specification file, simply replace the current
version of the file in its respective directory:

.. code-block:: text

    [~]$ cd ~/Source/acis_thermal_check

    [~]$ ls acis_thermal_check/tests/acisfp
    __init__.py  acisfp_test_spec.json  test_acisfp_acis.py  test_acisfp_viols.py
    __pycache__  answers                test_acisfp_sql.py