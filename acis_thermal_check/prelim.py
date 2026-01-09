from argparse import ArgumentParser

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import requests
import xija
from astropy.table import Table
from cxotime import CxoTime
from kadi.commands.states import get_states, interpolate_states
from xija.get_model_spec import get_xija_model_spec

state_msid_map = {
    "Time": "time",
    "FPTEMP Prediction (degC)": "fptemp",
    "1PDEAAT Prediction (Deg C)": "1pdeaat",
    "1DPAMZT Prediction (degC)": "1dpamzt",
    "1DEAMZT Prediction (degC)": "1deamzt",
    "Solid Angle (str)": "earth_solid_angle",
    "1CBAT Prediction (degC)": "1cbat",
    "SIM_PX Prediction (degC)": "sim_px",
    "Pitch (deg)": "pitch",
    "Roll (deg)": "roll",
    "Sim Pos (steps)": "sim_z",
    "FEP Count": "fep_count",
    "CCD Count": "ccd_count",
    "Video Board": "vid_board",
    "Clocking": "clocking",
    "DH Heater": "dh_heater",
    "DPA0 Prediction (degF)": "dpa0",
    "DEA0 Prediction (degC)": "dea0",
    "15V Power State": "hrc_15v",
    "24V Power State": "hrc_24v",
    "HRC-I On State": "hrc_i",
    "HRC-S On State": "hrc_s",
    "PIN1AT Prediction (Deg C)": "pin1at",
    "2CEAHVPT Prediction (degC)": "2ceahvpt",
    "CEA0 Prediction (degC)": "cea0",
    "CEA1 Prediction (degC)": "cea1",
}

msid_model_map = {
    "fptemp": "acisfp",
    "1pdeaat": "psmc",
    "1dpamzt": "dpa",
    "1deamzt": "dea",
}

model_deps = {
    "fptemp": ["ACISFP", "CEA"],
    "1pdeaat": ["1PDEAAT", "ACISFP"],
    "1dpamzt": ["ACISDPA"],
    "1deamzt": ["ACISDEA"],
}

main_model_comps = [
    "pitch",
    "roll",
    "sim_z",
    "ccd_count",
    "fep_count",
    "vid_board",
    "clocking",
    "dh_heater",
    "1cbat",
    "sim_px",
    "dea0",
    "dpa0",
    "1pin1at",
]


base_url = "https://occweb.cfa.harvard.edu/occweb/FOT/mission_planning/PRODUCTS/prelims"


def get_prelim_data(msid, load_name, local=False):
    year = f"20{load_name[-2:]}"
    if local:
        prefix = f"/data/mpcrit1/mplogs/{year}/{load_name}/thermal"
    else:
        prefix = f"{base_url}/{year}/{load_name}/prelim"
    all_t = Table()
    for name in model_deps[msid]:
        fileobj = f"{prefix}/{load_name}_{name}_prelim.txt"
        if not local:
            u = requests.get(fileobj)
            if not u.ok:
                raise RuntimeError(f"Reading {fileobj} failed!!")
            fileobj = u.text
        t = Table.read(
            fileobj,
            format="ascii",
            data_start=1,
            delimiter="\t",
        )
        for col in t.colnames:
            if col in state_msid_map:
                newcol = state_msid_map[col]
                if newcol in all_t.colnames:
                    continue
                data = t[col].data
                if newcol.startswith("hrc"):
                    data = np.char.upper(data)
                all_t[newcol] = data
    states = get_states(
        all_t["time"][0],
        all_t["time"][-1],
        state_keys=["eclipse"],
        merge_identical=False,
    )
    all_t["eclipse"] = interpolate_states(states, all_t["time"])["eclipse"]
    return all_t


def make_prelim_model(msid, t, times, chandra_models_version=None):
    model_spec, _ = get_xija_model_spec(
        msid_model_map[msid], version=chandra_models_version
    )
    model = xija.XijaModel(
        msid, start=t["time"][0], stop=t["time"][-1], model_spec=model_spec
    )
    model.comp[msid].set_data(t[msid][0])
    for key in main_model_comps:
        if key in model.comp:
            model.comp[key].set_data(t[key], times.secs)
    if "dpa_power" in model.comp:
        model.comp["dpa_power"].set_data(0.0)
    if "eclipse" in model.comp:
        model.comp["eclipse"].set_data(t["eclipse"] != "DAY", times.secs)
    if msid == "fptemp":
        # fix ESA
        esa_comp = model.comp["earthheat__fptemp"]
        esa = (
            t["earth_solid_angle"]
            * 7.5
            / (esa_comp.k + esa_comp.k2 * esa_comp.earth_phase)
        )
        model.comp["earthheat__fptemp"].set_data(esa, times.secs)
        # Set the HRC 15 volt state
        # NOTE: Because of an error in AP, the correct state is 215PCAST=OFF,
        # which indicates that the HRC 15V is ON.
        model.comp["215pcast_off"].set_data(t["hrc_15v"] == "ON", times.secs)
    if msid == "2ceahvpt":
        # Set the HRC states
        model.comp["2ps5aon_on"].set_data(True)
        model.comp["2ps5bon_on"].set_data(False)
        model.comp["2imonst_on"].set_data(t["hrc_i"] == "ON", times.secs)
        model.comp["2sponst_on"].set_data(t["hrc_s"] == "ON", times.secs)
        model.comp["2s2onst_on"].set_data(t["hrc_15v"] == "ON", times.secs)
        model.comp["224pcast_off"].set_data(t["hrc_24v"] == "ON", times.secs)
        model.comp["215pcast_off"].set_data(t["hrc_15v"] == "ON", times.secs)
    model.make()
    model.calc()
    return model


def main():
    parser = ArgumentParser(description="Rerun preliminary thermal model")
    parser.add_argument("load_name", type=str, help="The load name, e.g. AUG1825")
    parser.add_argument("msid", type=str, help="The MSID to model, e.g. fptemp")
    parser.add_argument(
        "--chandra_models_version",
        type=str,
        help="The chandra_models version, e.g. 3.68.0",
    )
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    t = get_prelim_data(args.msid, args.load_name, local=args.local)

    times = CxoTime(t["time"])

    model = make_prelim_model(
        args.msid, t, times, chandra_models_version=args.chandra_models_version
    )

    model_times = CxoTime(model.times)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times.datetime, t[args.msid], label="Prelim Model", lw=4)
    ax.plot(model_times.datetime, model.comp[args.msid].mvals, label="Model Rerun")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y:%j:%H"))
    ax.set_xlabel("Date")
    ax.set_ylabel(rf"{args.msid.upper()} ($^\circ$C)")
    ax.legend()
    fig.autofmt_xdate()
    fig.savefig(f"prelim_{args.msid}.png")
