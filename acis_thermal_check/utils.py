import logging
from pathlib import Path, PurePath

import matplotlib.pyplot as plt
import numpy as np
import Ska.Numpy
import Ska.Sun
from Ska.Matplotlib import cxctime2plotdate
from xija.limits import get_limit_color

TASK_DATA = Path(PurePath(__file__).parent / "..").resolve()

mylog = logging.getLogger("acis_thermal_check")

thermal_blue = "blue"
thermal_red = "red"


def calc_pitch_roll(times, ephem, states):
    """Calculate the normalized sun vector in body coordinates.
    Shamelessly copied from Ska.engarchive.derived.pcad but
    modified to use commanded states quaternions

    Parameters
    ----------
    times : NumPy array of times in seconds
    ephem : orbitephem and solarephem info
    states : commanded states NumPy recarray

    Returns
    -------
    3 NumPy arrays: time, pitch and roll
    """
    from Ska.engarchive.derived.pcad import arccos_clip, qrotate

    idxs = Ska.Numpy.interpolate(
        np.arange(len(states)), states["tstart"], times, method="nearest"
    )
    states = states[idxs]

    chandra_eci = np.array(
        [ephem["orbitephem0_x"], ephem["orbitephem0_y"], ephem["orbitephem0_z"]]
    )
    sun_eci = np.array(
        [ephem["solarephem0_x"], ephem["solarephem0_y"], ephem["solarephem0_z"]]
    )
    sun_vec = -chandra_eci + sun_eci
    est_quat = np.array([states["q1"], states["q2"], states["q3"], states["q4"]])

    sun_vec_b = qrotate(est_quat, sun_vec)  # Rotate into body frame
    magnitude = np.sqrt((sun_vec_b**2).sum(axis=0))
    magnitude[magnitude == 0.0] = 1.0
    sun_vec_b = sun_vec_b / magnitude  # Normalize

    pitch = np.degrees(arccos_clip(sun_vec_b[0, :]))
    roll = np.degrees(np.arctan2(-sun_vec_b[1, :], -sun_vec_b[2, :]))

    return pitch, roll


def config_logging(outdir, verbose):
    """
    Set up file and console logger.
    See http://docs.python.org/library/logging.html#logging-to-multiple-destinations
    Logs to the console and to run.dat.

    Parameters
    ----------
    outdir : Path
        The location of the directory which the model outputs
        are being written to.
    verbose : integer
        Indicate how verbose we want the logger to be.
        (0=quiet, 1=normal, 2=debug)
    """
    # Disable auto-configuration of root logger by adding a null handler.
    # This prevents other modules (e.g. Chandra.cmd_states) from generating
    # a streamhandler by just calling logging.info(..).
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    rootlogger = logging.getLogger()
    rootlogger.addHandler(NullHandler())

    logger = logging.getLogger("acis_thermal_check")
    logger.setLevel(logging.DEBUG)

    # Set numerical values for the different log levels
    loglevel = {0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}.get(
        verbose, logging.INFO
    )

    formatter = logging.Formatter("%(name)-3s: [%(levelname)-9s] %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(loglevel)
    logger.addHandler(console)

    logfile = outdir / "run.dat"

    filehandler = logging.FileHandler(filename=logfile, mode="w")
    filehandler.setFormatter(formatter)
    # Set the file loglevel to be at least INFO,
    # but override to DEBUG if that is requested at the
    # command line
    filehandler.setLevel(logging.INFO)
    if loglevel == logging.DEBUG:
        filehandler.setLevel(logging.DEBUG)
    logger.addHandler(filehandler)


class PlotDate:
    _color = None
    _color2 = None
    """
    Plot quantities with a date x-axis, on the left
    y-axis and optionally another on the right y-axis.

    Parameters
    ----------
    fig_id : integer
        The ID for this particular figure.
    x : NumPy array
        Times in seconds since the beginning of the mission for
        the left y-axis quantity.
    y : NumPy array
        Quantity to plot against the times on the left x-axis.
    x2 : NumPy array
        Times in seconds since the beginning of the mission for
        the right y-axis quantity.
    y2 : NumPy array
        Quantity to plot against the times on the right y-axis.
    yy : NumPy array, optional
        A second quantity to plot against the times on the
        left x-axis. Default: None
    xmin : float, optional
        The left-most value of the x-axis.
    xmax : float, optional
        The right-most value of the x-axis.
    ylim : 2-tuple, optional
        The limits for the left y-axis.
    ylim2 : 2-tuple, optional
        The limits for the right y-axis.
    xlabel : string, optional
        The label of the x-axis.
    ylabel : string, optional
        The label for the left y-axis.
    ylabel2 : string, optional
        The label for the right y-axis.
    linewidth : float, optional
        The linewidth for the left y-axis.
    linewidth2 : float, optional
        The linewidth for the right y-axis.
    title : string, optional
        The title for the plot.
    figsize : 2-tuple of floats
        Size of plot in width and height in inches.
    """

    def __init__(
        self,
        fig_id,
        x,
        y,
        x2=None,
        y2=None,
        yy=None,
        xmin=None,
        xmax=None,
        ylim=None,
        ylim2=None,
        xlabel="",
        ylabel="",
        ylabel2="",
        linewidth=2,
        linewidth2=2,
        title="",
        figsize=(12, 6),
        load_start=None,
        width=None,
    ):
        # Convert times to dates
        xt = cxctime2plotdate(x)
        fig = plt.figure(fig_id, figsize=figsize)
        fig.clf()
        ax = fig.add_subplot(1, 1, 1)
        # Plot left y-axis
        ax.plot(xt, y, linestyle="-", linewidth=linewidth, color=self._color, zorder=10)
        if yy is not None:
            ax.plot(xt, yy, linestyle="--", linewidth=linewidth, color=self._color2)
        if xmin is None:
            xmin = min(xt)
        if xmax is None:
            xmax = max(xt)
        ax.set_xlim(xmin, xmax)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()
        ax.set_zorder(10)
        ax.set_axisbelow(True)

        # Plot right y-axis

        if x2 is not None and y2 is not None:
            ax2 = ax.twinx()
            xt2 = cxctime2plotdate(x2)
            ax2.plot(xt2, y2, linestyle="-", linewidth=linewidth2, color="magenta")
            ax2.set_xlim(xmin, xmax)
            if ylim2:
                ax2.set_ylim(*ylim2)
            ax2.set_ylabel(ylabel2, color="magenta")
            ax2.xaxis.set_visible(False)
        else:
            ax2 = None

        if load_start is not None:
            # Add a vertical line to mark the start time of the load
            ax.axvline(load_start, linestyle="-", color="g", zorder=2, linewidth=2.0)

        Ska.Matplotlib.set_time_ticks(ax)
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation_mode("anchor")
            label.set_rotation(30)
            label.set_horizontalalignment("right")
        if ax2 is not None:
            [label.set_color("magenta") for label in ax2.yaxis.get_ticklabels()]
        ax.tick_params(which="major", axis="x", length=6)
        ax.tick_params(which="minor", axis="x", length=3)
        fig.subplots_adjust(bottom=0.22, right=0.87)
        # The next several lines ensure that the width of the axes
        # of all the weekly prediction plots are the same
        if width is not None:
            w2, _ = fig.get_size_inches()
            lm = fig.subplotpars.left * width / w2
            rm = fig.subplotpars.right * width / w2
            fig.subplots_adjust(left=lm, right=rm)

        ax.patch.set_visible(False)

        self.fig = fig
        self.ax = ax
        self.ax2 = ax2
        self.filename = None

    def add_limit_line(self, limit, label, ls="-"):
        """
        Add a horizontal line for a given limit to the plot.

        Parameters
        ----------
        limit : ACISLimit object
            Contains information about the value of the limit
            and the color it should be plotted with.
        label : string
            The label to give the line.
        ls : string, optional
            The line style for the limit line. Default: "-"
        """
        self.ax.axhline(
            limit.value,
            linestyle=ls,
            linewidth=2.0,
            color=limit.color,
            label=label,
            zorder=2.0,
        )


class PredictPlot(PlotDate):
    _color = thermal_blue
    _color2 = thermal_blue


def get_options(opts=None, use_acis_opts=True):
    """
    Construct the argument parser for command-line options for running
    predictions and validations for a load. Sets up the parser and
    defines default options. This function should be used by the specific
    thermal model checking tools.

    Parameters
    ----------
    opts: dictionary
        A (key, value) dictionary of additional options for the parser. These
        may be defined by the thermal model checking tool if necessary.
    use_acis_opts : boolean, optional
        Whether or not to include ACIS-specific options. Default: True
    """
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.set_defaults()
    parser.add_argument(
        "--outdir",
        default="out",
        help="Output directory. If it does not "
        "exist it will be created. Default: 'out'",
    )
    parser.add_argument(
        "--backstop_file",
        help="Path to the backstop file. If a directory, "
        "the backstop file will be searched for within "
        "this directory. Default: None",
    )
    parser.add_argument(
        "--oflsdir",
        help="Path to the directory containing the backstop "
        "file (legacy argument). If specified, it will "
        "override the value of the backstop_file "
        "argument. Default: None",
    )
    parser.add_argument(
        "--model-spec",
        help="Model specification file. Defaults to the one included with "
        "the model package.",
    )
    parser.add_argument(
        "--days", type=float, default=21.0, help="Days of validation data. Default: 21"
    )
    parser.add_argument(
        "--run-start",
        help="Reference time to replace run start time "
        "for regression testing. The default is to "
        "use the current time. Default: None",
    )
    parser.add_argument(
        "--interrupt",
        help="Set this flag if this is an interrupt load.",
        action="store_true",
    )
    parser.add_argument(
        "--traceback", action="store_false", help="Enable tracebacks. Default: True"
    )
    parser.add_argument(
        "--pred-only", action="store_true", help="Only make predictions. Default: False"
    )
    parser.add_argument(
        "--verbose", type=int, default=1, help="Verbosity (0=quiet, 1=normal, 2=debug)"
    )
    parser.add_argument(
        "--T-init",
        type=float,
        help="Starting temperature (degC). Default is to compute it from telemetry.",
    )
    if use_acis_opts:
        parser.add_argument(
            "--state-builder",
            default="acis",
            help="StateBuilder to use (kadi|acis). Default: acis",
        )
        parser.add_argument(
            "--nlet_file",
            default="/data/acis/LoadReviews/NonLoadTrackedEvents.txt",
            help="Full path to the Non-Load Event Tracking file that should be "
            "used for this model run.",
        )
    parser.add_argument("--version", action="store_true", help="Print version")

    if opts is not None:
        for opt_name, opt in opts:
            parser.add_argument(f"--{opt_name}", **opt)

    args = parser.parse_args()

    args.outdir = Path(args.outdir)

    if args.oflsdir is not None:
        args.backstop_file = args.oflsdir

    if args.pred_only and args.backstop_file is None:
        raise RuntimeError("You turned off both prediction and validation!!")

    return args


def make_state_builder(name, args, hrc_states=False):
    """
    Take the command-line arguments and use them to construct
    a StateBuilder object which will be used for the thermal
    prediction and validation.

    Parameters
    ----------
    name : string
        The identifier for the state builder to be used.
    args : ArgumentParser arguments
        The arguments to pass to the StateBuilder subclass.
    hrc_states : boolean, optional
        Whether or not to add HRC-specific states. Default: False
    """
    # Import the dictionary of possible state builders. This
    # dictionary is located in state_builder.py
    from acis_thermal_check.state_builder import state_builders

    builder_class = state_builders[name]

    # Build the appropriate state_builder depending upon the
    # value of the passed in parameter "name" which was
    # originally the --state-builder="kadi"|"acis" input argument
    #
    # Instantiate the Kadi History Builder: KadiStateBuilder
    if name == "kadi":
        state_builder = builder_class(
            interrupt=args.interrupt,
            backstop_file=args.backstop_file,
            logger=mylog,
            hrc_states=hrc_states,
        )

    # Instantiate the ACIS OPS History Builder: ACISStateBuilder
    elif name == "acis":
        # Create a state builder using the ACIS Ops backstop history
        # modules and send in some of the switches from the model invocation
        # argument list.  Also send the value of --run-start
        state_builder = builder_class(
            interrupt=args.interrupt,
            backstop_file=args.backstop_file,
            nlet_file=args.nlet_file,
            outdir=args.outdir,
            verbose=args.verbose,
            logger=mylog,
        )
    else:
        raise RuntimeError(f"No such state builder with name {name}!")

    return state_builder


def paint_perigee(perigee_passages, plots):
    """
    This function draws vertical dashed lines for radzone entry and
    exit (black) and perigee (red)

    Parameters
    ==========
    perigee_passages : dict of lists
        Lists of times for radzone entry, exit, and perigee
    plots : dict of plots
        the plots to add the lines to
    """
    for plot in plots.values():
        for key in ["entry", "perigee", "exit"]:
            color = "black" if key == "perigee" else "red"
            for time in perigee_passages[key]:
                xpos = cxctime2plotdate([time])[0]
                plot.ax.axvline(xpos, linestyle=":", color=color, linewidth=2.0)


class ChandraLimit:
    def __init__(self, value, color):
        self.value = value
        self.color = color


def get_acis_limits(msid, model_spec, limits_map=None):
    """
    Given a MSID and a model specification (JSON or dict),
    return the values and line colors of the limits specified
    in the file.

    Parameters
    ----------
    msid : string
        The MSID to get the limits for.
    model_spec : string or dict
        The xija model specification. If a string, it is
        assumed to be a JSON file to be read in
    limits_map : dict, optional
        If supplied, this will change the keys of the output
        dict, which are normally the limit names in the model
        specification, with other names, e.g. replaces
        "odb.caution.high" with "yellow_hi". Default: None

    Returns
    -------
    A dict of dicts, with each dict corresponding to the value of the
    limit and the color of the line on plots.
    """
    import json

    if msid == "fptemp_11":
        msid = "fptemp"
    if limits_map is None:
        limits_map = {}
    if not isinstance(model_spec, dict):
        model_spec = json.load(open(model_spec, "r"))
    json_limits = model_spec["limits"][msid]
    limits = {}
    for k, v in json_limits.items():
        if k == "unit":
            continue
        key = limits_map.get(k, k)
        limits[key] = ChandraLimit(v, get_limit_color(k))
    return limits
