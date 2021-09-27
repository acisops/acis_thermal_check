#!/usr/bin/env python

"""
========================
fep1_mong_check
========================

This code generates backstop load review outputs for checking the ACIS
FEP1 Mongoose temperature. It also generates FEP1 Mongoose model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
import matplotlib
matplotlib.use('Agg')

import sys
from acis_thermal_check import \
    DPABoardTempCheck, \
    get_options


class FEP1MongCheck(DPABoardTempCheck):
    def __init__(self):
        valid_limits = {'TMP_FEP1_MONG': [(1, 2.0), (50, 1.0), (99, 2.0)],
                        'PITCH': [(1, 3.0), (99, 3.0)],
                        'TSCPOS': [(1, 2.5), (99, 2.5)]
                       }
        hist_limit = [25.0, 20.0]  # First limit is >=, second limit is <=
        super(FEP1MongCheck, self).__init__("tmp_fep1_mong", "fep1_mong", 
                                            valid_limits, hist_limit)


def main():
    args = get_options("fep1_mong")
    fep1_mong_check = FEP1MongCheck()
    try:
        fep1_mong_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == '__main__':
    main()
