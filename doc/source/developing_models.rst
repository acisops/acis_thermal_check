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

The beginning part of the script should contain the following:

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
    
    # Matplotlib setup
    # Use Agg backend for command-line (non-interactive) operation
    import matplotlib
    matplotlib.use('Agg')
    
    import sys
    from acis_thermal_check import \
        ACISThermalCheck, \
        get_options

This includes the required imports and a beginning comment about what the
script is for, the latter of which should be modified for your model case. 

Subclassing ``ACISThermalCheck``
++++++++++++++++++++++++++++++++

The bulk of the script is contained in a subclass of the ``ACISThermalCheck``
class that is model-specific. This subclass will contain information specific
to the model. In the case of the 1DPAMZT model, this class is called 
``DPACheck``. 

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

If your model has special limits in the JSON model specification file which are 
not included in this default set:

.. code-block:: python

    {
        "odb.caution.high",
        "odb.caution.low",
        "safety.caution.high",
        "safety.caution.low",
        "planning.warning.high",
        "planning.warning.low"
    }

You must include them in a special dictionary ``limits_map`` which will be passed
to the ``ACISThermalCheck`` subclass. This dictionary maps the name of the limit
in the JSON file to something shorter (and perhaps more descriptive). All limits 
can then be accessed using the ``self.limits`` dictionary, which for each element 
has a dictionary which specifies the numerical ``value`` of the limit and the
``color`` which should be used on plots. Examples of how this is used are shown
below. In this case, the 1DPAMZT model has a limit at +12 :math:$^\circ$C which
is only applied when 0 FEPs are on. This is the ``"planning.caution.low"`` limit,
which is renamed to ``"zero_feps"`` in this case. 

The example of this class definition for the 1DPAMZT model is shown here. Both
limit objects that were created are passed to the ``__init__`` of the superclass.

.. code-block:: python

    class DPACheck(ACISThermalCheck):
        def __init__(self):
            # Specify the validation limits 
            valid_limits = {'1DPAMZT': [(1, 2.0), (50, 1.0), (99, 2.0)],
                            'PITCH': [(1, 3.0), (99, 3.0)],
                            'TSCPOS': [(1, 2.5), (99, 2.5)]
                            }
            # Specify the validation histogram limits
            hist_limit = [20.0]
            # Add the "zero_feps" limit
            limits_map = {
                "planning.caution.low": "zero_feps"
            }
            # Call the superclass' __init__ with the arguments
            super(DPACheck, self).__init__("1dpamzt", "dpa", valid_limits,
                                           hist_limit, limits_map=limits_map)

Custom Violations Checking and Plotting
+++++++++++++++++++++++++++++++++++++++

The ``ACISThermalCheck`` class has three methods which can be used
to customize plots for a specific model: ``custom_prediction_viols``,
``custom_prediction_plots``, and ``custom_validation_plots``. For the
``ACISThermalCheck`` superclass, these methods are all stubs unless
you override them in your subclass. 

``custom_prediction_viols`` allows you to add new violations of 
limits to check. This is done by calling the internal method
``_make_prediction_viols`` and telling it the following information, 
where we reference the example below for adding the "zero FEPs" limit
to the 1DPAMZT model:

* The limit value itself, in this case +12 :math:$^\circ$C, stored
  in ``self.limits["zero_feps"].value`` as shown below. 
* The name of the limit, which in this case is ``"zero-feps"``.
* Which type of temperature limit this is, (in this case) ``"min"`` or 
  ``"max"``. 
* Optionally, a limit may only apply in certain circumstances. This one
  only applies when zero FEPs are on, so we compute a ``mask`` from the 
  model values when the ``fep_count`` is zero and we also pass that in.

After that, we have to add the violation structure which is returned
from ``_make_prediction_viols`` to the ``viols`` dict (see below), and 
we are done. 

.. code-block:: python

    def custom_prediction_viols(self, times, temp, viols, load_start):
        """
        Custom handling of limit violations. This is for checking the
        +12 degC violation if all FEPs are off. 

        Parameters
        ----------
        times : NumPy array
            The times for the predicted temperatures
        temp : NumPy array
            The predicted temperatures
        viols : dict
            Dictionary of violations information to add to
        load_start : float
            The start time of the load, used so that we only report
            violations for times later than this time for the model
            run.
        """
        # Only check this violation when all FEPs are off
        mask = self.predict_model.comp['fep_count'].dvals == 0
        zf_viols = self._make_prediction_viols(
            times, temp, load_start, self.limits["zero_feps"].value,
            "zero-feps", "min", mask=mask)
        viols["zero_feps"] = {
            "name": f"Zero FEPs ({self.limits['zero_feps'].value} C)",
            "type": "Min",
            "values": zf_viols
        }

We also want to show this limit on the plot for the 1DPAMZT model. For this,
we use the ``custom_prediction_plots`` method of the ``ACISThermalCheck``
class. This gives us access to all of the prediction plots which will appear
on the thermal model webpage. 

The ``plots`` dict that is the sole argument to ``custom_prediction_plots``
contains ``PredictPlot`` objects for the temperature being modeled as well
as other quantities. Each of these ``PredictPlot`` objects has Matplotlib 
``Figure`` and ``AxesSubplot`` instances attached for further annotating or
adjusting plots, as well as the plot filename. To add a limit line, call the
``add_limit_line`` method of the ``PredictPlot`` object. An example for this 
is done to add the zero-FEPs line for the 1DPAMZT model is shown here:

.. code-block:: python

    def custom_prediction_plots(self, plots):
        """
        Customization of prediction plots.

        Parameters
        ----------
        plots : dict of dicts
            Contains the hooks to the plot figures, axes, and filenames
            and can be used to customize plots before they are written,
            e.g. add limit lines, etc.
        """
        plots[self.name].add_limit_line(self.limits["zero_feps"], 
                                        "Zero FEPs", ls='--')

Something similar can be done for the validation plots in 
``custom_validation_plots``, except here the input ``plots`` structure is 
a bit different. Each item of ``plots`` is a dict has two sub-dicts, 
``"lines"`` and ``"hist"``, the former for the actual model vs. data
comparison and the latter for the histogram of model-data error. In practice, 
you will only need to worry about the first, as shown below. 

.. code-block:: python

    def custom_validation_plots(self, plots):
        """
        Customization of validation plots.

        Parameters
        ----------
        plots : dict of dicts
            Contains the hooks to the plot figures, axes, and filenames
            and can be used to customize plots before they are written,
            e.g. add limit lines, etc.
        """
        plots["1dpamzt"]['lines']['ax'].axhline(
            self.limits["zero_feps"].value, linestyle='--', zorder=-8,
            color=self.limits["zero_feps"].color, linewidth=2, 
            label="Zero FEPs")

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
        T_dpa is set to None so we use the dvals in model.comp

        NOTE: If you change the name of the dpa0 pseudo node you
              have to edit the new name into the if statement
              below.
        """
        if 'dpa0' in model.comp:
            if state0 is None:
                T_dpa0 = model.comp["1dpamzt"].dvals
            else:
                T_dpa0 = state0["1dpamzt"]
            model.comp['dpa0'].set_data(T_dpa0, model.times)

Note that the method requires the ``XijaModel model`` object, the array of 
``state_times``, the commanded ``states`` array, the ephemeris ``MSIDSet`` 
``ephem``, and the ``state0`` dictionary providing the initial state. These
are all defined and set up in ``ACISThermalCheck``, so the model developer 
does not need to do this. The ``_calc_model_supp`` method must have this 
exact signature. 

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
        args = get_options("dpa") # collect the arguments
        dpa_check = DPACheck() # create an instance of the subclass
        try:
            dpa_check.run(args) # run the model using the arguments
        except Exception as msg:
            # handle any errors
            if args.traceback:
                raise
            else:
                print("ERROR:", msg)
                sys.exit(1)
    
    # This ensures main() is called when run from the command line
    if __name__ == '__main__':
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
    
    # Matplotlib setup
    # Use Agg backend for command-line (non-interactive) operation
    import matplotlib
    matplotlib.use('Agg')
    
    import sys
    from acis_thermal_check import \
        ACISThermalCheck, \
        get_options
    
    
    class DPACheck(ACISThermalCheck):
        def __init__(self):
            valid_limits = {'1DPAMZT': [(1, 2.0), (50, 1.0), (99, 2.0)],
                            'PITCH': [(1, 3.0), (99, 3.0)],
                            'TSCPOS': [(1, 2.5), (99, 2.5)]
                            }
            hist_limit = [20.0]
            limits_map = {
                "planning.caution.low": "zero_feps"
            }
            super(DPACheck, self).__init__("1dpamzt", "dpa", valid_limits,
                                           hist_limit, limits_map=limits_map)
    
        def custom_prediction_viols(self, times, temp, viols, load_start):
            """
            Custom handling of limit violations. This is for checking the
            +12 degC violation if all FEPs are off. 
    
            Parameters
            ----------
            times : NumPy array
                The times for the predicted temperatures
            temp : NumPy array
                The predicted temperatures
            viols : dict
                Dictionary of violations information to add to
            load_start : float
                The start time of the load, used so that we only report
                violations for times later than this time for the model
                run.
            """
            # Only check this violation when all FEPs are off
            mask = self.predict_model.comp['fep_count'].dvals == 0
            zf_viols = self._make_prediction_viols(
                times, temp, load_start, self.limits["zero_feps"].value,
                "zero-feps", "min", mask=mask)
            viols["zero_feps"] = {
                "name": f"Zero FEPs ({self.limits['zero_feps'].value} C)",
                "type": "Min",
                "values": zf_viols
            }
    
        def custom_prediction_plots(self, plots):
            """
            Customization of prediction plots.
    
            Parameters
            ----------
            plots : dict of dicts
                Contains the hooks to the plot figures, axes, and filenames
                and can be used to customize plots before they are written,
                e.g. add limit lines, etc.
            """
            plots[self.name].add_limit_line(self.limits["zero_feps"], 
                                            "Zero FEPs", ls='--')
    
        def custom_validation_plots(self, plots):
            """
            Customization of validation plots.
    
            Parameters
            ----------
            plots : dict of dicts
                Contains the hooks to the plot figures, axes, and filenames
                and can be used to customize plots before they are written,
                e.g. add limit lines, etc.
            """
            plots["1dpamzt"]['lines']['ax'].axhline(
                self.limits["zero_feps"].value, linestyle='--', zorder=-8,
                color=self.limits["zero_feps"].color, linewidth=2, 
                label="Zero FEPs")
    
        def _calc_model_supp(self, model, state_times, states, ephem, state0):
            """
            Update to initialize the dpa0 pseudo-node. If 1dpamzt
            has an initial value (T_dpa) - which it does at
            prediction time (gets it from state0), then T_dpa0 
            is set to that.  If we are running the validation,
            T_dpa is set to None so we use the dvals in model.comp
    
            NOTE: If you change the name of the dpa0 pseudo node you
                  have to edit the new name into the if statement
                  below.
            """
            if 'dpa0' in model.comp:
                if state0 is None:
                    T_dpa0 = model.comp["1dpamzt"].dvals
                else:
                    T_dpa0 = state0["1dpamzt"]
                model.comp['dpa0'].set_data(T_dpa0, model.times)
    
    
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
    
    
    if __name__ == '__main__':
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
    'console_scripts': [
        'dea_check = acis_thermal_check.apps.dea_check:main',
        'dpa_check = acis_thermal_check.apps.dpa_check:main',
        'psmc_check = acis_thermal_check.apps.psmc_check:main',
        'acisfp_check = acis_thermal_check.apps.acisfp_check:main',
        'fep1_mong_check = acis_thermal_check.apps.fep1_mong_check:main',
        'fep1_actel_check = acis_thermal_check.apps.fep1_actel_check:main',
        'bep_pcb_check = acis_thermal_check.apps.bep_pcb_check:main'
    ]
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
    beppcb/
    data/
    dea/
    dpa/
    fep1actel/
    fep1mong/
    psmc/

The ``data`` directory is used to store test NLET files and other items needed
for tests. Inside the test directory for your model, it should look like this
(again using the 1DPAMZT model as an example):

.. code-block:: text

    answers/
    __init__.py
    dpa_test_spec.json
    test_dpa_acis.py
    test_dpa_kadi.py
    test_dpa_viols.py

The ``__init__.py`` file should be empty, and the ``answers`` directory should
initially be empty. The rest of the files will be described in turn. 

directory, a model specification file, and three Python scripts for testing.
These include a script which tests the "ACIS" state builder, another which
tests the legacy "SQL" state builder, and another which checks for violations.
All of these scripts make use of a ``RegressionTester`` class which handles all
of the testing. 

The ACIS state builder test script ``test_dpa_acis.py`` makes use of a 
``RegressionTester`` object, which handles all of the testing machinery. This 
runs the models using the ``run_models`` method, called with the ACIS state builder, 
and then runs prediction and validation tests. The script itself is shown below. 
Note that both functions ``test_prediction`` and ``test_validation`` take an extra 
argument, ``answer_store``, which is a boolean used to determine whether or not the 
tests should be run or new answers should be generated. The use of this argument is 
explained in :ref:`test_suite`.

.. code-block:: python

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import \
        RegressionTester, all_loads
    import pytest
    
    
    @pytest.fixture(autouse=True, scope='module')
    def dpa_rt(test_root):
        # ACIS state builder tests
        rt = RegressionTester(DPACheck, test_root=test_root, sub_dir='acis')
        rt.run_models(state_builder='acis')
        return rt
    
    
    # Prediction tests
    
    @pytest.mark.parametrize('load', all_loads)
    def test_prediction(dpa_rt, answer_store, load):
        dpa_rt.run_test("prediction", load, answer_store=answer_store)
    
    
    # Validation tests
    
    @pytest.mark.parametrize('load', all_loads)
    def test_validation(dpa_rt, answer_store, load):
        dpa_rt.run_test("validation", load, answer_store=answer_store)
    
The kadi state builder tests in ``test_dpa_kadi.py`` are nearly identical 
to the ACIS ones, but in this case the answers are not generated if 
``answer_store=True``. We assume that the two state builder methods should 
generate the same answers, and this is a test of that. This example script 
is shown below:

.. code-block:: python

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import \
        RegressionTester, all_loads
    import pytest
    
    
    @pytest.fixture(autouse=True, scope='module')
    def dpa_rt(test_root):
        # kadi state builder tests
        rt = RegressionTester(DPACheck, test_root=test_root, sub_dir='kadi')
        rt.run_models(state_builder='kadi')
        return rt
    
    
    # Prediction tests
    
    @pytest.mark.parametrize('load', all_loads)
    def test_prediction(dpa_rt, answer_store, load):
        if not answer_store:
            dpa_rt.run_test("prediction", load)
        else:
            pass
    
    
    # Validation tests
    
    @pytest.mark.parametrize('load', all_loads)
    def test_validation(dpa_rt, answer_store, load):
        if not answer_store:
            dpa_rt.run_test("validation", load)
        else:
            pass

Finally, tests of thermal violation flagging should also be generated. These 
tests check if violations of planning limits during model predictions are
flagged appropriately. They test a single load, and require a new JSON file 
to be stored in the (for this example) ``acis_thermal_check/tests/dpa/answers`` 
subdirectory which contain the details of the test. For this, you need to 
select a load, and then create a JSON file which contains the ``run_start`` 
for the model (this is to ensure reproducibility) and new ``limits`` for the 
model run, to ensure that a violation actually occurs. These should be set a 
few degrees lower than the real limits. For the 1DPAMZT model, the file is named 
``JUL3018A_viol.json`` and looks like this:

.. code-block:: json

    {
        "run_start": "2018:205:00:42:38.816",
        "limits": {
            "yellow_hi": 37.2,
            "plan_limit_hi": 35.2
        }
    }

The JUL3018A load was selected for this test. The script to run this test looks
like this:

.. code-block:: python

    from acis_thermal_check.apps.dpa_check import DPACheck
    from acis_thermal_check.tests.regression_testing import \
        RegressionTester, tests_path
    
    
    def test_JUL3018A_viols(answer_store, test_root):
        answer_data = tests_path / "dpa/answers/JUL3018A_viol.json"
        dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir='viols')
        dpa_rt.check_violation_reporting("JUL3018A", answer_data,
                                         answer_store=answer_store)

After the test is run with the ``--answer_store`` flag set 
(see :ref:`test_suite`), the JSON file will look like this:

.. code-block:: json

    {
        "datestarts": [
            "2018:212:16:23:26.816",
            "2018:213:14:42:46.816",
            "2018:215:04:09:34.816"
        ],
        "datestops": [
            "2018:212:17:29:02.816",
            "2018:213:16:10:14.816",
            "2018:215:05:15:10.816"
        ],
        "temps": [
            "35.89",
            "35.89",
            "35.72"
        ],
        "run_start": "2018:205:00:42:38.816",
        "limits": {
            "yellow_hi": 37.2,
            "planning_hi": 35.2
        },
        "duration": [
            "3.94",
            "5.25",
            "3.94"
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
