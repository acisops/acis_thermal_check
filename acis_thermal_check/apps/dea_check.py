#!/usr/bin/env python

"""

========================
dea_check
========================

This code generates backstop load review outputs for checking the ACIS
DEA temperature 1DEAMZT.  It also generates DEA model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

import sys

import matplotlib
from chandra_limits import DEALimit

from acis_thermal_check import ACISThermalCheck, get_options

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation

matplotlib.use("Agg")


class DEACheck(ACISThermalCheck):
    _limit_class = DEALimit

    def __init__(self):
        valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]
        hist_limit = [20.0]
        super().__init__("1deamzt", "dea", valid_limits, hist_limit)

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Update to initialize the dea0 pseudo-node. If 1dpamzt
        has an initial value (T_dea) - which it does at
        prediction time (gets it from state0), then T_dea0
        is set to that.  If we are running the validation,
        T_dea is set to None so we use the dvals in model.comp

        NOTE: If you change the name of the dea0 pseudo node you
              have to edit the new name into the if statement
              below.
        """
        if "dea0" in model.comp:
            if state0 is None:
                T_dea0 = model.comp["1deamzt"].dvals
            else:
                T_dea0 = state0["1deamzt"]
            model.comp["dea0"].set_data(T_dea0, model.times)


def main():
    args = get_options()
    dea_check = DEACheck()
    try:
        dea_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
