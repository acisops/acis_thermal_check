#!/usr/bin/env python

"""
========================
cea_check
========================

This code generates backstop load review outputs for checking the HRC
CEA temperature 1DPAMZT.  It also generates CEA model validation
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
    get_options, \
    mylog


class CEACheck(ACISThermalCheck):
    def __init__(self):
        valid_limits = {'2CEAHVPT': [(1, 2.0), (50, 1.0), (99, 2.0)],
                        'PITCH': [(1, 3.0), (99, 3.0)],
                        'TSCPOS': [(1, 2.5), (99, 2.5)]
                        }
        hist_limit = [5.0]
        limits_map = {}
        super(CEACheck, self).__init__("2ceahvpt", "cea", valid_limits,
                                       hist_limit, limits_map=limits_map)

    def make_prediction_viols(self, temps, states, load_start):
        """
        Find limit violations where predicted temperature is above the
        specified limits.

        Parameters
        ----------
        temps : dict of NumPy arrays
            NumPy arrays corresponding to the modeled temperatures
        states : NumPy record array
            Commanded states
        load_start : float
            The start time of the load, used so that we only report
            violations for times later than this time for the model
            run.
        """
        mylog.info('Checking for limit violations')

        temp = temps[self.name]
        times = self.predict_model.times

        # Only check this violation when HRC is on
        mask = self.predict_model.comp['2imonst_on'].dvals
        mask |= self.predict_model.comp['2sponst_on'].dvals
        hi_viols = self._make_prediction_viols(
            times, temp, load_start, self.limits["planning_hi"].value,
            "planning", "max", mask=mask)
        viols = {"hi":
                     {"name": f"Hot ({self.limits['planning_hi'].value} C)",
                      "type": "Max",
                      "values": hi_viols}
                 }
        return viols

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Update to initialize the cea0 pseudo-node. If 1dpamzt
        has an initial value (T_cea) - which it does at
        prediction time (gets it from state0), then T_cea0 
        is set to that.  If we are running the validation,
        T_cea is set to None so we use the dvals in model.comp

        NOTE: If you change the name of the dpa0 pseudo node you
              have to edit the new name into the if statement
              below.
        """
        if 'cea0' in model.comp:
            if state0 is None:
                T_cea0 = model.comp["2ceahvpt"].dvals
            else:
                T_cea0 = state0["2ceahvpt"]
            model.comp['cea0'].set_data(T_cea0, model.times)
        model.comp["2ps5aon_on"].set_data(True)
        model.comp["2ps5bon_on"].set_data(False)
        model.comp["2imonst_on"].set_data(states["hrc_i"] == "ON", state_times)
        model.comp["2sponst_on"].set_data(states["hrc_s"] == "ON", state_times)
        model.comp["2s2onst_on"].set_data(states["hrc_15v"] == "ON", state_times)
        model.comp["224pcast_off"].set_data(states["hrc_15v"] == "ON", state_times)
        model.comp["215pcast_off"].set_data(states["hrc_15v"] == "ON", state_times)


def main():
    args = get_options()
    cea_check = CEACheck()
    try:
        cea_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == '__main__':
    main()