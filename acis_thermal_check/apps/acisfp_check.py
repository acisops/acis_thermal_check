#!/usr/bin/env python

"""
========================
dpa_check
========================

This code generates backstop load review outputs for checking the ACIS
focal plane temperature: FP_TEMP11. It also generates FP_TEMP11 model
validation plots comparing predicted values to telemetry for the
previous three weeks.
"""

import os
import sys

import matplotlib
from astropy.table import Table
from cxotime import CxoTime
from Ska.Matplotlib import cxctime2plotdate

from acis_thermal_check import ACISThermalCheck, get_options, mylog

#
# Import ACIS-specific observation extraction, filtering
# and attribute support routines.
#
from acis_thermal_check.acis_obs import (
    acis_filter,
    find_obsid_intervals,
    hrc_science_obs_filter,
)
from acis_thermal_check.utils import PredictPlot, paint_perigee

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
matplotlib.use("Agg")


class ACISFPCheck(ACISThermalCheck):
    def __init__(self):
        valid_limits = {"PITCH": [(1, 3.0), (99, 3.0)], "TSCPOS": [(1, 2.5), (99, 2.5)]}
        hist_limit = [(-120.0, -100.0)]
        limits_map = {
            "planning.data_quality.high.acisi": "acis_i",
            "planning.data_quality.high.aciss": "acis_s",
            "planning.data_quality.high.aciss_hot": "acis_hot",
            "planning.data_quality.high.cold_ecs": "cold_ecs",
            "planning.warning.high": "planning_hi",
            "safety.caution.high": "yellow_hi",
        }
        super().__init__(
            "fptemp",
            "acisfp",
            valid_limits,
            hist_limit,
            other_telem=["1dahtbon"],
            other_map={"1dahtbon": "dh_heater", "fptemp_11": "fptemp"},
            limits_map=limits_map,
        )
        # Create an empty observation list which will hold the results. This
        # list contains all ACIS and all ECS observations.
        self.acis_and_ecs_obs = []
        self.acis_hot_obs = []

    def _calc_model_supp(self, model, state_times, states, ephem, state0):
        """
        Create and run the Thermal Model for the Focal Plane temperature.

        Given: Model name (some string)
               Commanded States collected by make_week_predict
               start time
               Stop Time
               T_acisfp
               T_acisfp_times
        """
        # Start by creating the basic modeling framework for a XIJA Thermal Model
        # Give it some name, start and stop time and the name of the JSON file
        # --------------
        # THERMAL_MODEL
        # --------------

        # Now set any data values for the components of your model
        # What you have to push in manually are:
        #       any states information like vid_board or ccd count
        #       any pseudo-MSID's such as 1cbat (because the node does not reflect the MSID)
        #       any single value initializations you think ought to be made.
        #         - e.g. fptemp in this case since it's what you are looking for.

        # For each item in the Commanded States data structure which matters to us,
        # insert the values in the commanded states data structure into the model:
        #
        # Telemetry doesn't have to be pushed in - the model handles that.But items in the states
        # array have to be manually shoved in.
        #
        # pitch comes from the telemetry

        # Input quaternions explicitly for calculating Earth heating
        for i in range(1, 5):
            name = "aoattqt{}".format(i)
            state_name = "q{}".format(i)
            model.comp[name].set_data(states[state_name], state_times)

        # Input ephemeris explicitly for calculating Earth heating
        for axis in "xyz":
            name = f"orbitephem0_{axis}"
            model.comp[name].set_data(ephem[name], model.times)
            name = f"solarephem0_{axis}"
            if name in model.comp:
                model.comp[name].set_data(ephem[name], model.times)

        # Set some initial values. You do this because some
        # of these values may not be set at the actual start time.
        model.comp["dpa_power"].set_data(0.0)
        model.comp["1cbat"].set_data(-53.0)
        model.comp["sim_px"].set_data(-120.0)

    def make_prediction_plots(self, outdir, states, temps, load_start):
        """
        Make plots of the thermal prediction as well as associated
        commanded states.

        Parameters
        ----------
        outdir : string
            The path to the output directory.
        states : NumPy record array
            Commanded states
        temps : dict of NumPy arrays
            Dictionary of temperature arrays
        load_start : float
            The start time of the load in seconds from the beginning of the
            mission.
        """
        times = self.predict_model.times

        # Gather perigee passages
        self._gather_perigee(times[0], load_start + 86400.0)

        """
        Next we need to find all the ACIS-S observations within the start/stop
        times so that we can paint those on the plots as well. We will get
        those from the commanded states data structure called "states"
        """

        # create an empty dictionary called plots to contain the returned
        # figures, axes 1 and axes 2 of the PredictPlot class
        plots = {}

        # Start time of loads being reviewed expressed in units for plotdate()
        load_start = cxctime2plotdate([load_start])[0]
        # Value for left side of plots
        plot_start = max(load_start - 2.0, cxctime2plotdate([times[0]])[0])

        w1 = None
        # Make plots of FPTEMP and pitch vs time, looping over
        # three different temperature ranges
        ylim = [(-120, -79), (-120, -119), (-120.0, -107.5)]
        ypos = [-110.0, -119.35, -116]
        capwidth = [2.0, 0.1, 0.4]
        textypos = [-108.0, -119.3, -115.7]
        fontsize = [12, 9, 9]
        for i in range(3):
            name = f"{self.name}_{i+1}"
            plots[name] = PredictPlot(
                fig_id=i + 1,
                x=times,
                y=temps[self.name],
                x2=self.predict_model.times,
                y2=self.predict_model.comp["pitch"].mvals,
                xlabel="Date",
                ylabel=r"Temperature ($^\circ$C)",
                ylabel2="Pitch (deg)",
                xmin=plot_start,
                ylim=ylim[i],
                ylim2=(40, 180),
                figsize=(12, 7.142857142857142),
                width=w1,
                load_start=load_start,
            )
            plots[name].ax.set_title(self.msid.upper(), loc="left", pad=10)
            # Draw a horizontal line indicating cold ECS cutoff
            plots[name].add_limit_line(self.limits["cold_ecs"], "Cold ECS", ls="--")
            # Draw a horizontal line showing the ACIS-I cutoff
            plots[name].add_limit_line(self.limits["acis_i"], "ACIS-I", ls="--")
            # Draw a horizontal line showing the ACIS-S cutoff
            plots[name].add_limit_line(self.limits["acis_s"], "ACIS-S", ls="--")
            # Draw a horizontal line showing the hot ACIS-S cutoff
            plots[name].add_limit_line(self.limits["acis_hot"], "Hot ACIS-S", ls="--")
            # Draw a horizontal line showing the planning warning limit
            plots[name].add_limit_line(self.limits["planning_hi"], "Planning", ls="-")
            # Draw a horizontal line showing the safety caution limit
            plots[name].add_limit_line(self.limits["yellow_hi"], "Yellow", ls="-")
            # Get the width of this plot to make the widths of all the
            # prediction plots the same
            if i == 0:
                w1, _ = plots[name].fig.get_size_inches()

            # Now draw horizontal lines on the plot running from start to stop
            # and label them with the Obsid
            draw_obsids(
                self.acis_and_ecs_obs,
                plots,
                name,
                ypos[i],
                ypos[i] - 0.5 * capwidth[i],
                ypos[i] + 0.5 * capwidth[i],
                textypos[i],
                fontsize[i],
                plot_start,
            )

            # These next lines are dummies so we can get the obsids in the legend
            plots[name].ax.errorbar(
                [0.0, 0.0],
                [1.0, 1.0],
                xerr=1.0,
                lw=2,
                xlolims=True,
                color="blue",
                capsize=4,
                capthick=2,
                label="Cold ECS",
            )
            plots[name].ax.errorbar(
                [0.0, 0.0],
                [1.0, 1.0],
                xerr=1.0,
                lw=2,
                xlolims=True,
                color="red",
                capsize=4,
                capthick=2,
                label="ACIS-I",
            )
            plots[name].ax.errorbar(
                [0.0, 0.0],
                [1.0, 1.0],
                xerr=1.0,
                lw=2,
                xlolims=True,
                color="green",
                capsize=4,
                capthick=2,
                label="ACIS-S",
            )
            plots[name].ax.errorbar(
                [0.0, 0.0],
                [1.0, 1.0],
                xerr=1.0,
                lw=2,
                xlolims=True,
                color="saddlebrown",
                capsize=4,
                capthick=2,
                label="Hot ACIS-S",
            )

            # Make the legend on the temperature plot
            plots[name].ax.legend(
                bbox_to_anchor=(0.15, 0.99), loc="lower left", ncol=4, fontsize=12
            )

            # Build the file name
            filename = (
                f"{self.msid.lower()}" f"M{-int(ylim[i][0])}toM{-int(ylim[i][1])}.png"
            )
            plots[name].filename = filename

        self._make_state_plots(plots, 3, w1, plot_start, states, load_start)

        # Now plot any perigee passages that occur between xmin and xmax
        # for eachpassage in perigee_passages:
        paint_perigee(self.perigee_passages, plots)

        plots["default"] = plots[f"{self.name}_3"]

        # Now write all the plots after possible
        # customizations have been made
        for key in plots:
            if key != self.msid:
                outfile = os.path.join(outdir, plots[key].filename)
                mylog.info("Writing plot file %s" % outfile)
                plots[key].fig.savefig(outfile)

        return plots

    def make_prediction_viols(self, temps, states, load_start):
        """
        Find limit violations where predicted temperature is above the
        red minus margin.

        MSID is a global

        acis_and_ecs_obs contains all ACIS and ECS observations.

        We will create a list of ECS-ONLY runs, and a list of all
        ACIS science runs without ECS runs. These two lists will
        be used to assess the categories of violations:

            1) Any ACIS-I observation that violates the -114 red limit
               is a violation and a load killer
                 - science_viols

            2) Any ACIS-S observation that violates the -112 red limit
               is a violation and a load killer
                 - science_viols

        """
        # extract the OBSID's from the commanded states. NOTE: this contains all
        # observations including ECS runs and HRC observations
        observation_intervals = find_obsid_intervals(states, load_start)

        # Filter out any HRC science observations BUT keep ACIS ECS observations
        self.acis_and_ecs_obs = hrc_science_obs_filter(observation_intervals)

        times = self.predict_model.times

        mylog.info(
            f"MAKE VIOLS Checking for limit violations in "
            f"{len(self.acis_and_ecs_obs)} total science observations"
        )

        viols = {}

        # ------------------------------------------------------
        #   Create subsets of all the observations
        # ------------------------------------------------------
        # Now divide out observations by ACIS-S and ACIS-I
        ACIS_I_obs, ACIS_S_obs, ACIS_hot_obs, sci_ecs_obs = acis_filter(
            self.acis_and_ecs_obs
        )

        temp = temps[self.name]

        # ---------------------------------------------------------------
        # Planning - Collect any -84 C violations. These are load killers
        # ---------------------------------------------------------------

        hi_viols = self._make_prediction_viols(
            times, temp, load_start, self.limits["planning_hi"].value, "planning", "max"
        )
        viols = {
            "hi": {
                "name": f"Planning High ({self.limits['planning_hi'].value} C)",
                "type": "Max",
                "values": hi_viols,
            }
        }

        acis_i_limit = self.limits["acis_i"].value
        acis_s_limit = self.limits["acis_s"].value
        acis_hot_limit = self.limits["acis_hot"].value
        cold_ecs_limit = self.limits["cold_ecs"].value

        # ------------------------------------------------------------
        # ACIS-I - Collect any -112 C violations of any non-ECS ACIS-I
        # science run. These are load killers
        # ------------------------------------------------------------

        mylog.info(f"ACIS-I Science ({acis_i_limit} C) violations")

        # Create the violation data structure.
        acis_i_viols = self.search_obsids_for_viols(
            "ACIS-I", acis_i_limit, ACIS_I_obs, temp, times, load_start
        )

        viols["ACIS_I"] = {
            "name": f"ACIS-I ({acis_i_limit} C)",
            "type": "Max",
            "values": acis_i_viols,
        }

        # ------------------------------------------------------------
        # ACIS-S - Collect any -111 C violations of any non-ECS ACIS-S
        # science run. These are load killers
        # ------------------------------------------------------------

        mylog.info(f"ACIS-S Science ({acis_s_limit} C) violations")

        acis_s_viols = self.search_obsids_for_viols(
            "ACIS-S", acis_s_limit, ACIS_S_obs, temp, times, load_start
        )
        viols["ACIS_S"] = {
            "name": f"ACIS-S ({acis_s_limit} C)",
            "type": "Max",
            "values": acis_s_viols,
        }

        # ------------------------------------------------------------
        # ACIS-S Hot - Collect any -109 C violations of any non-ECS ACIS-S
        # science run which can run hot. These are load killers
        # ------------------------------------------------------------
        #
        mylog.info(f"ACIS-S Science ({acis_hot_limit} C) violations")

        acis_hot_viols = self.search_obsids_for_viols(
            "Hot ACIS-S", acis_hot_limit, ACIS_hot_obs, temp, times, load_start
        )
        viols["ACIS_S_hot"] = {
            "name": f"ACIS-S Hot ({acis_hot_limit} C)",
            "type": "Max",
            "values": acis_hot_viols,
        }

        # ------------------------------------------------------------
        # Science Orbit ECS -119.5 violations; -119.5 violation check
        # ------------------------------------------------------------
        mylog.info(f"Science Orbit ECS ({cold_ecs_limit} C) violations")

        ecs_viols = self.search_obsids_for_viols(
            "Science Orbit ECS", cold_ecs_limit, sci_ecs_obs, temp, times, load_start
        )

        viols["ecs"] = {
            "name": f"Science Orbit ECS ({cold_ecs_limit} C)",
            "type": "Min",
            "values": ecs_viols,
        }

        # Store all obsids which can go to -109 C
        for obs in ACIS_hot_obs:
            self.acis_hot_obs.append(obs)

        return viols

    def search_obsids_for_viols(
        self, limit_name, limit, observations, temp, times, load_start
    ):
        """
        Given a planning limit and a list of observations, find those time intervals
        where the temp gets warmer than the planning limit and identify which
        observations (if any) include part or all of those intervals.
        """
        viols_list = []

        # Run through all observations
        for eachobs in observations:
            # Get the observation start science and stop science times, and obsid
            obs_tstart = eachobs["start_science"]
            obs_tstop = eachobs["tstop"]
            # If the observation is in this load, let's look at it
            if obs_tstart > load_start:
                idxs = (times >= obs_tstart) & (times <= obs_tstop)
                viols = self._make_prediction_viols(
                    times[idxs], temp[idxs], load_start, limit, limit_name, "max"
                )
                # If we have flagged any violations, record the obsid for each
                # and add them to the list
                if len(viols) > 0:
                    for viol in viols:
                        viol["obsid"] = str(eachobs["obsid"])
                    viols_list += viols

        # Finished - return the violations list
        return viols_list

    def write_temps(self, outdir, times, temps):
        """
        Write the states record array to the file "temperatures.dat"
        and the Earth solid angles to "earth_solid_angles.dat".

        Parameters
        ----------
        outdir : string
            The directory the file will be written to.
        times : NumPy array
            Times in seconds from the start of the mission
        temps : NumPy array
            Temperatures in Celsius
        """
        super().write_temps(outdir, times, temps)
        outfile = os.path.join(outdir, "earth_solid_angles.dat")
        mylog.info(f"Writing Earth solid angles to {outfile}")
        e = self.predict_model.comp["earthheat__fptemp"].dvals
        efov_table = Table(
            [times, CxoTime(times).date, e],
            names=["time", "date", "earth_solid_angle"],
            copy=False,
        )
        efov_table["time"].format = "%.2f"
        efov_table["earth_solid_angle"].format = "%.3e"
        efov_table.write(outfile, format="ascii", delimiter="\t", overwrite=True)


def draw_obsids(
    obs_list, plots, msid, ypos, endcapstart, endcapstop, textypos, fontsize, plot_start
):
    """
    This function draws visual indicators across the top of the plot showing
    which observations are ACIS; whether they are ACIS-I (red), ACIS-S (green),
    or ECS (blue); when they start and stop; and whether or not any observation
    is sensitive to the focal plane temperature. The list of observations sensitive
    to the focal plane is found by reading the fp_sensitive.dat file that is
    located in each LR directory and is created by the LR script.

    The caller supplies:
               Options from the Command line supplied by the user at runtime
               The plot dictionary
               The MSID used to index into the plot dictionary (superfluous but required)
               The position on the Y axis you'd like these indicators to appear
               The Y position of the bottom of the end caps
               The Y position of the top of the end caps
               The starting position of the OBSID number text
               The font size
               The left time of the plot in plot_date units
    """
    # Now run through the observation list
    for eachobservation in obs_list:
        # extract the obsid

        obsid = eachobservation["obsid"]
        in_fp = eachobservation["instrument"]
        hot_acis = eachobservation["hot_acis"]

        if obsid > 60000:
            # ECS observations during the science orbit are colored blue
            color = "blue"
        else:
            # Color all ACIS-S observations green; all ACIS-I
            # observations red
            if in_fp == "ACIS-I":
                color = "red"
            else:
                color = "saddlebrown" if hot_acis else "green"

        obsid_txt = str(obsid)
        # If this is an ECS measurement in the science orbit mark
        # it as such
        if obsid > 60000:
            obsid_txt += " (ECS)"

        # Convert the start and stop times into the Ska-required format
        obs_start = cxctime2plotdate([eachobservation["tstart"]])
        obs_stop = cxctime2plotdate([eachobservation["tstop"]])

        if in_fp.startswith("ACIS-") or obsid > 60000:
            # For each ACIS Obsid, draw a horizontal line to show
            # its start and stop
            plots[msid].ax.hlines(
                ypos,
                obs_start,
                obs_stop,
                linestyle="-",
                color=color,
                zorder=2,
                linewidth=2.0,
            )

            # Plot vertical end caps for each obsid to visually show start/stop
            plots[msid].ax.vlines(
                obs_start, endcapstart, endcapstop, color=color, zorder=2, linewidth=2.0
            )
            plots[msid].ax.vlines(
                obs_stop, endcapstart, endcapstop, color=color, zorder=2, linewidth=2.0
            )

            # Now print the obsid in the middle of the time span,
            # above the line, and rotate 90 degrees.

            obs_time = obs_start + (obs_stop - obs_start) / 2
            if obs_time > plot_start:
                # Now plot the obsid.
                plots[msid].ax.text(
                    obs_time,
                    textypos,
                    obsid_txt,
                    color=color,
                    va="bottom",
                    ma="left",
                    rotation=90,
                    zorder=2,
                    fontsize=fontsize,
                )


def main():
    args = get_options()
    acisfp_check = ACISFPCheck()
    try:
        acisfp_check.run(args)
    except Exception as msg:
        if args.traceback:
            raise
        else:
            print("ERROR:", msg)
            sys.exit(1)


if __name__ == "__main__":
    main()
