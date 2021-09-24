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

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
import matplotlib
matplotlib.use('Agg')

from acis_thermal_check import \
    ACISThermalCheck, \
    get_options
import os
import sys

model_path = os.path.abspath(os.path.dirname(__file__))


class PSMCCheck(ACISThermalCheck):
    def __init__(self):
        valid_limits = {'1PDEAAT': [(1, 2.5), (50, 1.0), (99, 5.5)],
                        'PITCH': [(1, 3.0), (99, 3.0)],
                        'TSCPOS': [(1, 2.5), (99, 2.5)]
                       }
        hist_limit = [30., 40.]
        super(PSMCCheck, self).__init__("1pdeaat", "psmc", valid_limits,
                                        hist_limit, other_telem=['1dahtbon'],
                                        other_map={'1dahtbon': 'dh_heater'})

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        # 1PIN1AT is broken, so we set its initial condition
        # using an offset, which makes sense based on historical
        # data
        if state0 is None:
            T_pin1at = model.comp["1pdeaat"].dvals - 10.0
        else:
            T_pin1at = state0["1pdeaat"] - 10.0
        model.comp['pin1at'].set_data(T_pin1at, model.times)


def main():
    args = get_options("psmc", model_path)
    psmc_check = PSMCCheck()
    try:
        psmc_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == '__main__':
    main()
