.. _developing-models:

Developing a New Thermal Model for Use with ``acis_thermal_check``
------------------------------------------------------------------

To develop a new thermal model for use with ``acis_thermal_check``, the 
following steps should be followed. A new model needs the following:

* A subclass of the ``ACISThermalCheck`` class, e.g. ``DPACheck``.
* This subclass should have information about model validation limits,
  histogram limits, and a method called ``_calc_model_supp`` which implements
  additional model components specific to this model. 
* Testing needs to be set up. 

Developing a new thermal model to use with ``acis_thermal_check`` is fairly
straightforward. What is typically only needed is to provide the model-specific 
elements such as the limits for validation, and the code which is called to load
model-specific data into the ``xija`` model. There will also need to be some mainly 
boilerplate driver code which collects command line arguments and runs everything. 
Finally, one will need to set up testing. 

In the following, we will use the application ``dpa_check`` as a guide 
on how to create a model and run it with ``acis_thermal_check``. 

The Model Script
================

The following describes how one designs the Python script that uses
``acis_thermal_check`` to run a particular model. This script should be placed
in the ``acis_thermal_check/acis_thermal_check/apps`` directory. We will be 
using the ``dpa_check.py`` script as an example.

Front Matter
++++++++++++

The beginning part of the script should contain something like the following:

.. code-block:: python

    #!/usr/bin/env python

    """
    ========================
    dpa_check
    ========================

    This code generates backstop load review outputs for checking the ACIS
    DPA temperature 1DPAMZT.  It also generates DPA model validation
    plots comparing predicted values to telemetry for the previous three
    weeks.
    """

    import sys

    import matplotlib
    from chandra_limits import DPALimit

    from acis_thermal_check import ACISThermalCheck, get_options

    # Matplotlib setup
    # Use Agg backend for command-line (non-interactive) operation
    matplotlib.use("Agg")

This includes the required imports and a beginning comment about what the
script is for, the latter of which should be modified for your model case. 

Subclassing ``ACISThermalCheck``
++++++++++++++++++++++++++++++++

The bulk of the script is contained in a subclass of the ``ACISThermalCheck``
class that is model-specific. This subclass will contain information specific
to the model. In the case of the 1DPAMZT model, this class is called 
``DPACheck``. 

All ``ACISThermalCheck`` subclasses need a their corresponding ``_limit_class``
attribute defined, which should be set to the subclass of the ``chandra_limits``
``ThermalLimit`` class used for this particular MSID. In this case, the subclass
is ``DPALimit``. See the ``chandra_limits`` `documentation <https://sot.github.io/chandra_limits>`_
for more details.

This class definition will require an ``__init__`` method which takes no 
arguments beyond ``self``. Inside it, validation limits for various MSIDs should
be specified, which correspond to limits on the differences between the data and
the model. Violations of these limits will be flagged in the validation report 
on the web page. For each MSID, the violation limits are given as a list of 
tuples, where the first item in each tuple is the percentile of the distribution
of the model error, and the second item is the amount of allowed error 
corresponding to that percentile. These are specified in the ``valid_limits`` 
dictionary, which is defined in ``__init__``.

Also, the histograms produced as a part of the validation report do not 
display the histogram for all temperatures, but only for those temperatures 
greater than a lower limit, which is contained in the ``hist_limit`` list. This
should also be defined in ``__init__``. 

The example of this class definition for the 1DPAMZT model is shown here. Both
limit objects that were created are passed to the ``__init__`` of the superclass.

.. code-block:: python

    class DPACheck(ACISThermalCheck):
        _limit_class = DPALimit
        _flag_cold_viols = True

        def __init__(self):
            valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]
            hist_limit = [20.0]
            super().__init__(
                "1dpamzt",
                "dpa",
                valid_limits,
                hist_limit,
            )

The ``_calc_model_supp`` Method
+++++++++++++++++++++++++++++++

The subclass of the ``ACISThermalCheck`` class will probably require a 
``_calc_model_supp`` method to be defined. For the default ``ACISThermalCheck``
class, this method does nothing. But in the case of each individual model, it 
will set up states, components, or nodes which are specific to that model.
The example of how to set up this method for the 1DPAMZT model is shown below:

.. code-block:: python

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Update to initialize the dpa0 pseudo-node. If 1dpamzt
        has an initial value (T_dpa) - which it does at
        prediction time (gets it from state0), then T_dpa0
        is set to that.  If we are running the validation,
        T_dpa is set to None, so we use the dvals in model.comp

        NOTE: If you change the name of the dpa0 pseudo node you
              have to edit the new name into the if statement
              below.
        """
        if "dpa0" in model.comp:
            if state0 is None:
                T_dpa0 = model.comp["1dpamzt"].dvals
            else:
                T_dpa0 = state0["1dpamzt"]
            model.comp["dpa0"].set_data(T_dpa0, model.times)

Note that the method requires this exact signature: ``XijaModel model``
object, the array of ``state_times``, the commanded ``states`` array, the
ephemeris ``MSIDSet`` ``ephem``, and the ``state0`` dictionary providing
the initial state.

``main`` Function
+++++++++++++++++

The ``main`` function is called when the model script is run from the command
line. What it needs to do is gather the command-line arguments using the 
``get_options`` function, create an instance of the subclass of the 
``ACISThermalCheck`` we created above, and then call that instance's ``run``
method using the arguments. It's also a good idea to run the model within a 
``try...except`` block in case any exceptions are raised, because then we 
can control whether or not the traceback is printed to screen via the 
``--traceback`` command-line argument.

.. code-block:: python

    def main():
        args = get_options() # collect the arguments
        dpa_check = DPACheck() # create an instance of the subclass
        try:
            dpa_check.run(args) # run the model using the arguments
        except Exception as msg:
            if args.traceback:
                raise
            else:
                print("ERROR:", msg)
                sys.exit(1)

    # This ensures main() is called when run from the command line
    if __name__ == "__main__":
        main()

The Full Script
+++++++++++++++

For reference, the full script containing all of these elements in the case 
of the 1DPAMZT model is shown below:

.. code-block:: python

    #!/usr/bin/env python

    """
    ========================
    dpa_check
    ========================

    This code generates backstop load review outputs for checking the ACIS
    DPA temperature 1DPAMZT.  It also generates DPA model validation
    plots comparing predicted values to telemetry for the previous three
    weeks.
    """

    import sys

    import matplotlib
    from chandra_limits import DPALimit

    from acis_thermal_check import ACISThermalCheck, get_options

    # Matplotlib setup
    # Use Agg backend for command-line (non-interactive) operation
    matplotlib.use("Agg")


    class DPACheck(ACISThermalCheck):
        _limit_class = DPALimit
        _flag_cold_viols = True

        def __init__(self):
            valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]
            hist_limit = [20.0]
            super().__init__(
                "1dpamzt",
                "dpa",
                valid_limits,
                hist_limit,
            )

        def _calc_model_supp(self, model, state_times, states, ephem, state0):
            """
            Update to initialize the dpa0 pseudo-node. If 1dpamzt
            has an initial value (T_dpa) - which it does at
            prediction time (gets it from state0), then T_dpa0
            is set to that.  If we are running the validation,
            T_dpa is set to None, so we use the dvals in model.comp

            NOTE: If you change the name of the dpa0 pseudo node you
                  have to edit the new name into the if statement
                  below.
            """
            if "dpa0" in model.comp:
                if state0 is None:
                    T_dpa0 = model.comp["1dpamzt"].dvals
                else:
                    T_dpa0 = state0["1dpamzt"]
                model.comp["dpa0"].set_data(T_dpa0, model.times)


    def main():
        args = get_options()
        dpa_check = DPACheck()
        try:
            dpa_check.run(args)
        except Exception as msg:
            if args.traceback:
                raise
            else:
                print("ERROR:", msg)
                sys.exit(1)


    if __name__ == "__main__":
        main()

Setting Up An Entry Point
=========================

We need to tell the ``acis_thermal_check`` package that there needs to be a new
command-line script installed which corresponds to this model. The way to do that
is to edit the ``entry_points`` dictionary in the ``setup.py`` file in the 
top-level ``acis_thermal_check`` directory. We need to simply add a new entry to
the ``console_scripts`` list, following the same convention as those which already
exist:

.. code-block:: python

    entry_points = {
        "console_scripts": [
            "dea_check = acis_thermal_check.apps.dea_check:main",
            "dpa_check = acis_thermal_check.apps.dpa_check:main",
            "dpamyt_check = acis_thermal_check.apps.dpamyt_check:main",
            "psmc_check = acis_thermal_check.apps.psmc_check:main",
            "acisfp_check = acis_thermal_check.apps.acisfp_check:main",
            "fep1_mong_check = acis_thermal_check.apps.fep1_mong_check:main",
            "fep1_actel_check = acis_thermal_check.apps.fep1_actel_check:main",
            "bep_pcb_check = acis_thermal_check.apps.bep_pcb_check:main",
            "cea_check = acis_thermal_check.apps.cea_check:main",
            "copy_model_outputs = acis_thermal_check.apps.copy_model_outputs:main",
        ],
    }

What this does is tell the installer that we want to make an executable wrapper 
for the script that can be run from the command line. It does this for you, so 
you just need to make sure it points to the correct script name. 

Testing Scripts and Data
========================

The ``acis_thermal_check`` testing suite checks prediction and validation
outputs against previously generated "gold standard" answers for a number of 
previously run loads, as well as checking to make sure violations are 
appropriately flagged. 

First, within the ``acis_thermal_check/tests/`` directory, there should be
a subdirectory for the model in question, given an identifying name. The current
subdirectories in this directory are:

.. code-block:: text

    acisfp/
    bep_pcb/
    cea/
    data/
    dea/
    dpa/
    fep1_actel/
    fep1_mong/
    psmc/

The ``data`` directory is used to store test NLET files and other items needed
for tests. Inside the test directory for your model, it should look something
like this (again using the 1DPAMZT model as an example):

.. code-block:: text

    answers/
    __init__.py
    dpa_test_spec.json
    test_dpa_acis.py
    test_dpa_kadi.py
    test_dpa_non_load.py
    test_dpa_pred_only.py
    test_dpa_valid_only.py
    test_dpa_viols.py

The ``__init__.py`` file should be empty, and the ``answers`` directory should
initially be empty. The rest of the files will be described in turn. 

The test script ``test_dpa_acis.py`` makes use of a ``RegressionTester`` object, which
handles all of the testing machinery. This will run the models called with the
``ACISStateBuilder`` class, and then runs prediction and validation tests, which are
parameterized by ``pytest`` to run on a set of load weeks which are contained in the
``all_loads`` list imported at the top of the script. The script itself is shown below.
Note that both functions ``test_prediction`` and ``test_validation`` take an extra argument,
``answer_store``, which is used to determine whether or not the tests should be run or new
answers should be generated. The use of this argument is explained in :ref:`test_suite`.

.. code-block:: python

    import pytest

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


    @pytest.fixture(autouse=True, scope="module")
    def dpa_rt(test_root):
        # ACIS state builder tests
        rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="acis")
        return rt


    # Prediction tests


    @pytest.mark.parametrize("load", all_loads)
    def test_prediction(dpa_rt, answer_store, load):
        dpa_rt.run_test("prediction", load, "acis", answer_store=answer_store)


    # Validation tests


    @pytest.mark.parametrize("load", all_loads)
    def test_validation(dpa_rt, answer_store, load):
        dpa_rt.run_test("validation", load, "acis", answer_store=answer_store)


The tests in ``test_dpa_kadi.py`` are identical to the ACIS ones, except that they use
the ``KadiStateBuilder`` class. We assume that the two state builder methods should
generate the same answers. This example script is shown below:

.. code-block:: python

    import pytest

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


    @pytest.fixture(autouse=True, scope="module")
    def dpa_rt(test_root):
        # kadi state builder tests
        rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="kadi")
        return rt


    # Prediction tests


    @pytest.mark.parametrize("load", all_loads)
    def test_prediction(dpa_rt, answer_store, load):
        dpa_rt.run_test("prediction", load, "kadi", answer_store=answer_store)


    # Validation tests


    @pytest.mark.parametrize("load", all_loads)
    def test_validation(dpa_rt, answer_store, load):
        dpa_rt.run_test("validation", load, "kadi", answer_store=answer_store)

Finally, tests of thermal violation flagging should also be generated. These 
tests check if violations of planning limits during model predictions are
flagged appropriately. They test a single load, and require a new JSON file 
to be stored in the (for this example) ``acis_thermal_check/tests/dpa/answers`` 
subdirectory which contain the details of the test. For this, you need to 
select a load, and then create a JSON file which contains the ``run_start`` 
for the model (this is to ensure reproducibility) and new ``limits`` for the 
model run, to ensure that a violation actually occurs. These should be set a 
few degrees lower than the real limits. For the 1DPAMZT model, the file is named 
``DEC0825A_viol.json`` and should initially look like this:

.. code-block:: json

    {
        "run_start": "2025:342:01:01:51.789",
        "limits": {
            "odb.caution.high": 37.2,
            "planning.warning.high": 35.2
        }
    }

The DEC0825A load was selected for this test. The script to run this test looks
like this:

.. code-block:: python

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


    def test_DEC0825A_viols(answer_store, test_root):
        answer_data = tests_path / "dpa/answers/DEC0825A_viol.json"
        dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="viols")
        dpa_rt.check_violation_reporting("DEC0825A", answer_data, answer_store=answer_store)

After the test is run with the ``--answer_store`` flag set (see :ref:`test_suite`), the
JSON file will look like this:

.. code-block:: json

    {
        "datestarts": [
            "2025:342:14:38:54.816",
            "2025:343:01:12:10.816",
            "2025:346:08:01:42.816",
            "2025:346:02:27:15.453"
        ],
        "datestops": [
            "2025:342:15:28:06.816",
            "2025:343:01:53:41.383",
            "2025:346:13:02:10.425",
            "2025:346:02:27:35.262"
        ],
        "temps": [
            "36.13",
            "35.97",
            "39.33",
            "10.48"
        ],
        "run_start": "2025:342:01:01:51.789",
        "limits": {
            "odb.caution.high": 37.2,
            "planning.warning.high": 35.2
        },
        "duration": [
            "2.95",
            "2.49",
            "18.03",
            "0.02"
        ]
    }

Note that the start and stop times of the violations and the values of the
maximum temperatures themselves have been added to the JSON file. These are
the values which will be tested, as well as whether or not the page flags a
violation. 

The ``dpa_test_spec.json`` file is a special model specification file used
for testing. For more information about this, see :ref:`test_suite`.

The first set of answers for the tests should also be committed. To do this,
see :ref:`test_suite`.

Finally, the test answer directory for your new model needs to be added
to the ``MANIFEST.in`` file at the top of the ``acis_thermal_check`` package,
which contains a list of data files and file wildcards that need to be 
installed along with the package. 

.. code-block:: none

    include acis_thermal_check/tests/dpa/answers/*
