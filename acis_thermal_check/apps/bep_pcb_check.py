#!/usr/bin/env python

"""
========================
bep_pcb_check
========================

This code generates backstop load review outputs for checking the ACIS
BEP PCB temperature. It also generates BEP PCB model validation plots
comparing predicted values to telemetry for the previous three weeks.
"""

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
import matplotlib
matplotlib.use('Agg')

import sys
from acis_thermal_check import \
    DPABoardTempCheck, \
    get_options


class BEPPCBCheck(DPABoardTempCheck):
    def __init__(self):
        valid_limits = {'TMP_BEP_PCB': [(1, 2.0), (50, 1.0), (99, 2.0)],
                        'PITCH': [(1, 3.0), (99, 3.0)],
                        'TSCPOS': [(1, 2.5), (99, 2.5)]
                       }
        hist_limit = [20.0, 20.0] # First limit is >=, second limit is <=
        super(BEPPCBCheck, self).__init__("tmp_bep_pcb", "bep_pcb",
                                          valid_limits, hist_limit)


def main():
    args = get_options("bep_pcb")
    bep_pcb_check = BEPPCBCheck()
    try:
        bep_pcb_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == '__main__':
    main()
