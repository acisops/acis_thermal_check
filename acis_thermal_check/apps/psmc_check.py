#!/usr/bin/env python

"""
========================
psmc_check
========================

This code generates backstop load review outputs for checking the ACIS
PSMC temperature 1PDEAAT.  It also generates PSMC model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

import sys

import matplotlib
from chandra_limits import PSMCLimit

from acis_thermal_check import ACISThermalCheck, get_options

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation

matplotlib.use("Agg")


class PSMCCheck(ACISThermalCheck):
    _limit_class = PSMCLimit

    def __init__(self):
        valid_limits = [(1, 2.5), (50, 1.0), (99, 5.5)]
        hist_limit = [30.0, 40.0]
        super().__init__(
            "1pdeaat",
            "psmc",
            valid_limits,
            hist_limit,
            other_telem=["1dahtbon"],
            other_map={"1dahtbon": "dh_heater"},
        )

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        # 1PIN1AT is broken, so we set its initial condition
        # using an offset, which makes sense based on historical
        # data
        if state0 is None:
            T_pin1at = model.comp["1pdeaat"].dvals - 10.0
        else:
            T_pin1at = state0["1pdeaat"] - 10.0
        model.comp["pin1at"].set_data(T_pin1at, model.times)


def main():
    args = get_options()
    psmc_check = PSMCCheck()
    try:
        psmc_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
