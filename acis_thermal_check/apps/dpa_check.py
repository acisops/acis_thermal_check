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
