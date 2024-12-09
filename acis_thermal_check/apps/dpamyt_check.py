#!/usr/bin/env python

"""
========================
1dpamyt_check
========================

This code generates backstop load review outputs for checking the ACIS
DPA temperature 1DPAMYT.  It also generates 1DPAMYT model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

import sys

import matplotlib
from chandra_limits import DPAMYTLimit

from acis_thermal_check import ACISThermalCheck, get_options

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
matplotlib.use("Agg")


class DPAMYTCheck(ACISThermalCheck):
    _limit_class = DPAMYTLimit

    def __init__(self):
        valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]

        # Specify the temperature where only those temps greater
        # than this temperature will be displayed on the histogram.
        hist_limit = [20.0]

        # Call the superclass' __init__ with the arguments
        super().__init__("1dpamyt", "dpamyt", valid_limits, hist_limit)

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Update to initialize the dpa0 pseudo-node. If 1dpamyt
        has an initial value (T_dpa) - which it does at
        prediction time (gets it from state0), then T_dpa0
        is set to that.  If we are running the validation,
        T_dpa is set to None so we use the dvals in model.comp

        NOTE: If you change the name of the dpa0 pseudo node you
              have to edit the new name into the if statement
              below.
        """
        if "dpa0" in model.comp:
            if state0 is None:
                T_dpa0 = model.comp["1dpamyt"].dvals
            else:
                T_dpa0 = state0["1dpamyt"]
            model.comp["dpa0"].set_data(T_dpa0, model.times)


def main():
    args = get_options()
    dpamyt_check = DPAMYTCheck()
    try:
        dpamyt_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
