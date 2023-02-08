#!/usr/bin/env python

"""
========================
cea_check
========================

This code generates backstop load review outputs for checking the HRC
CEA temperature 2CEAHVPT. It also generates CEA model validation
plots comparing predicted values to telemetry for the previous three
weeks.
"""

import sys

import matplotlib
from Ska.Matplotlib import pointpair

from acis_thermal_check import ACISThermalCheck, get_options, mylog
from acis_thermal_check.utils import PredictPlot

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
matplotlib.use("Agg")


class CEACheck(ACISThermalCheck):
    def __init__(self):
        valid_limits = {
            "2CEAHVPT": [(1, 2.0), (50, 1.0), (99, 2.0)],
            "PITCH": [(1, 3.0), (99, 3.0)],
            "TSCPOS": [(1, 2.5), (99, 2.5)],
        }
        hist_limit = [5.0]
        limits_map = {}
        other_telem = ["2imonst", "2sponst", "2s2onst", "1dahtbon"]
        super().__init__(
            "2ceahvpt",
            "cea",
            valid_limits,
            hist_limit,
            limits_map=limits_map,
            other_telem=other_telem,
            other_map={"1dahtbon": "dh_heater"},
        )

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
        mylog.info("Checking for limit violations")

        temp = temps[self.name]
        times = self.predict_model.times

        # Only check this violation when HRC is on
        mask = self.predict_model.comp["2imonst_on"].dvals
        mask |= self.predict_model.comp["2sponst_on"].dvals
        hi_viols = self._make_prediction_viols(
            times,
            temp,
            load_start,
            self.limits["planning_hi"].value,
            "planning",
            "max",
            mask=mask,
        )
        viols = {
            "hi": {
                "name": f"Hot ({self.limits['planning_hi'].value} C)",
                "type": "Max",
                "values": hi_viols,
            },
        }
        return viols

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Update to initialize the cea0 pseudo-node. If 2ceahvpt
        has an initial value (T_cea) - which it does at
        prediction time (gets it from state0), then T_cea0
        is set to that.  If we are running the validation,
        T_cea is set to None so we use the dvals in model.comp
        """
        for node in ["cea0", "cea1"]:
            if state0 is None:
                T_cea = model.comp["2ceahvpt"].dvals
            else:
                T_cea = state0["2ceahvpt"]
            model.comp[node].set_data(T_cea, model.times)
        model.comp["2ps5aon_on"].set_data(True)
        model.comp["2ps5bon_on"].set_data(False)
        model.comp["2imonst_on"].set_data(states["hrc_i"] == "ON", state_times)
        model.comp["2sponst_on"].set_data(states["hrc_s"] == "ON", state_times)
        model.comp["2s2onst_on"].set_data(states["hrc_15v"] == "ON", state_times)
        model.comp["224pcast_off"].set_data(states["hrc_15v"] == "ON", state_times)
        model.comp["215pcast_off"].set_data(states["hrc_15v"] == "ON", state_times)

    def _make_state_plots(self, plots, num_figs, w1, plot_start, states, load_start):
        # Make a plot of ACIS HRC states
        plots["hrc"] = PredictPlot(
            fig_id=num_figs + 1,
            title="HRC States",
            xlabel="Date",
            x=pointpair(states["tstart"], states["tstop"]),
            y=pointpair(states["hrc_i"]),
            yy=pointpair(states["hrc_s"]),
            ylabel="HRC-I/S",
            x2=pointpair(states["tstart"], states["tstop"]),
            y2=pointpair(states["hrc_15v"]),
            ylabel2="HRC 15 V",
            linewidth2=4.0,
            xmin=plot_start,
            width=w1,
            load_start=load_start,
        )
        plots["hrc"].ax.lines[0].set_label("HRC-I")
        plots["hrc"].ax.lines[1].set_label("HRC-S")
        plots["hrc"].ax.legend(fancybox=True, framealpha=0.5, loc=2)
        plots["hrc"].filename = "hrc.png"

        num_figs += 1
        super()._make_state_plots(plots, num_figs, w1, plot_start, states, load_start)


def main():
    args = get_options(use_acis_opts=False)
    cea_check = CEACheck()
    try:
        cea_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
