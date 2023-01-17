#!/usr/bin/env python

"""
========================
fep1_actel_check
========================

This code generates backstop load review outputs for checking the ACIS
FEP1 Actel temperature. It also generates FEP1 Actel model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

import sys

import matplotlib

from acis_thermal_check import DPABoardTempCheck, get_options

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
matplotlib.use("Agg")


class FEP1ActelCheck(DPABoardTempCheck):
    def __init__(self):
        valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]
        hist_limit = [25.0, 20.0]  # First limit is >=, second limit is <=
        super().__init__("tmp_fep1_actel", "fep1_actel", valid_limits, hist_limit)


def main():
    args = get_options()
    fep1_actel_check = FEP1ActelCheck()
    try:
        fep1_actel_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
