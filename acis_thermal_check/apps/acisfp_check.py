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

import sys

import matplotlib
import numpy as np
from astropy.table import Table
from chandra_limits import ACISFPLimit
from cxotime import CxoTime
from ska_matplotlib import cxctime2plotdate

from acis_thermal_check import ACISThermalCheck, get_options, mylog
from acis_thermal_check.utils import PredictPlot, paint_perigee

# Matplotlib setup
# Use Agg backend for command-line (non-interactive) operation
matplotlib.use("Agg")


class ACISFPCheck(ACISThermalCheck):
    _limit_class = ACISFPLimit

    def __init__(self):
        valid_limits = [(1, 2.0), (50, 1.0), (99, 2.0)]
        hist_limit = [(-120.0, -100.0)]
        super().__init__(
            "fptemp",
            "acisfp",
            valid_limits,
            hist_limit,
            other_telem=["1dahtbon"],
            other_map={"1dahtbon": "dh_heater", "fptemp_11": "fptemp"},
        )
        # Create an empty observation list which will hold the results. This
        # list contains all ACIS and all ECS observations.
        self.acis_and_ecs_obs = []

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
        #    any states information like vid_board or ccd count
        #    any pseudo-MSIDs such as 1cbat (because the node does not reflect the MSID)
        #    any single value initializations you think ought to be made.
        #    - e.g. fptemp in this case since it's what you are looking for.

        # For each item in the Commanded States data structure which matters to us,
        # insert the values in the commanded states data structure into the model:
        #
        # Telemetry doesn't have to be pushed in - the model handles that. But
        # items in the states array have to be manually shoved in.
        #
        # pitch comes from the telemetry

        # Input quaternions explicitly for calculating Earth heating
        for i in range(1, 5):
            name = f"aoattqt{i}"
            state_name = f"q{i}"
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

        if "215pcast_off" in model.comp:
            # Set the HRC 15 volt state
            # NOTE: Because of an error in AP, the correct state is 215PCAST=OFF,
            # which indicates that the HRC 15V is ON.
            model.comp["215pcast_off"].set_data(states["hrc_15v"] == "ON", state_times)

    def make_prediction_plots(
        self, outdir, states, temps, load_start, upper_limit, lower_limit
    ):
        """
        Make plots of the thermal prediction as well as associated
        commanded states.

        Parameters
        ----------
        outdir : Path
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
        ylim = [(-120, -79), (-120, -119), (-120.0, -103.5)]
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
            # Draw the planning limit line on the plot (broken up
            # according to condition)
            upper_limit.plot(
                fig_ax=(plots[name].fig, plots[name].ax),
                lw=3,
                zorder=2,
                use_colors=True,
                show_changes=False,
            )
            # Draw the yellow limit line on the plot
            plots[name].add_limit_line(self.limits["yellow_hi"], lw=3)
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

            # Make the legend on the temperature plot
            plots[name].ax.legend(
                bbox_to_anchor=(0.15, 0.99),
                loc="lower left",
                ncol=4,
                fontsize=12,
            )

            # Build the file name
            filename = (
                f"{self.msid.lower()}M{-int(ylim[i][0])}toM{-int(ylim[i][1])}.png"
            )
            plots[name].filename = filename

        self._make_state_plots(plots, 3, w1, plot_start, states, load_start)

        # Now plot any perigee passages that occur between xmin and xmax
        # for eachpassage in perigee_passages:
        paint_perigee(self.perigee_passages, plots)

        plots["default"] = plots[f"{self.name}_3"]

        # Now write all the plots after possible
        # customizations have been made
        for key, plot in plots.items():
            if key != self.msid:
                outfile = outdir / plot.filename
                mylog.info("Writing plot file %s", outfile)
                plot.fig.savefig(outfile)

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
        # Extract the prediction violations and the limit objects
        viols, upper_limit, lower_limit = super().make_prediction_viols(
            temps, states, load_start
        )

        # Store the obsid table
        obs_table = self.limit_object.acis_obs_info.as_table()
        # use only the obsids after the load start
        idxs = np.where(CxoTime(obs_table["start_science"]).secs > load_start)[0]
        self.acis_and_ecs_obs = obs_table[idxs]
        # for each violation, add the exposure time to the violation
        # so we can record it on the page
        for v in viols["hi"]:
            idx = np.where(self.acis_and_ecs_obs["obsid"] == v["obsid"])[0]
            if idx.size == 0:
                continue
            row = self.acis_and_ecs_obs[idx[0]]
            start_science = CxoTime(row["start_science"]).secs + row["bias_time"]
            stop_science = CxoTime(row["stop_science"]).secs
            v["exp_time"] = (stop_science - start_science) * 1.0e-3
        return viols, upper_limit, lower_limit

    def write_temps(self, outdir, times, temps):
        """
        Write the states record array to the file "temperatures.dat"
        and the Earth solid angles to "earth_solid_angles.dat".

        Parameters
        ----------
        outdir : Path
            The directory the file will be written to.
        times : NumPy array
            Times in seconds from the start of the mission
        temps : NumPy array
            Temperatures in Celsius
        """
        super().write_temps(outdir, times, temps)
        outfile = outdir / "earth_solid_angles.dat"
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
    obs_list,
    plots,
    msid,
    ypos,
    endcapstart,
    endcapstop,
    textypos,
    fontsize,
    plot_start,
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

        if obsid > 60000:
            # ECS observations during the science orbit are colored blue
            color = "blue"
        else:
            # Color all ACIS-S observations green; all ACIS-I
            # observations red
            if in_fp == "ACIS-I":
                color = "red"
            else:
                color = "green"

        obsid_txt = str(obsid)
        # If this is an ECS measurement in the science orbit mark
        # it as such
        if obsid > 60000:
            obsid_txt += " (ECS)"

        # Convert the start and stop times into the Ska-required format
        tstart, tstop = CxoTime(
            [eachobservation["start_science"], eachobservation["stop_science"]],
        )
        obs_start, obs_stop = cxctime2plotdate([tstart, tstop])

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
                obs_start,
                endcapstart,
                endcapstop,
                color=color,
                zorder=2,
                linewidth=2.0,
            )
            plots[msid].ax.vlines(
                obs_stop,
                endcapstart,
                endcapstop,
                color=color,
                zorder=2,
                linewidth=2.0,
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
