#!/usr/bin/env python

"""
========================
multi_model_check
========================

This code runs one or more of the ``acis_thermal_check`` model checking
tools (``dpa_check``, ``dea_check``, ``psmc_check``, etc.) using the same
set of command-line arguments, writing each model's outputs to its own
subdirectory of a single output directory. It then writes a top-level
index page linking to each model's own report page, using each model's
prediction plot as the link.
"""

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path, PurePath

from cxotime import CxoTime

from acis_thermal_check.utils import TASK_DATA, mylog

# Mapping of model name to the acis_thermal_check.apps module that implements
# it, and the candidate prediction-plot filenames to look for in its output
# directory, in priority order. Most models always write a single, fixed
# "<msid>.png" file. The ACIS FP model ("acisfp") is an exception: it names
# its main prediction plot after the y-axis limits of the plot, which differ
# depending on whether a backstop file was given (the normal "weekly load"
# case, which yields "fptempM120toM103.png") or not (a prediction-only run
# with no backstop file, which yields "fptempM120toM79.png").
MODELS = {
    "dpa": ("1dpamzt", "dpa_check", ("1dpamzt.png",)),
    "dea": ("1deamzt", "dea_check", ("1deamzt.png",)),
    "psmc": ("1pdeaat", "psmc_check", ("1pdeaat.png",)),
    "acisfp": (
        "fptemp",
        "acisfp_check",
        ("fptempM120toM103.png", "fptempM120toM79.png", "fptempM120toM119.png"),
    ),
}


def find_plot_file(model_outdir, candidates):
    """
    Return the first of ``candidates`` that exists in ``model_outdir``,
    or ``None`` if none of them were written.
    """
    for candidate in candidates:
        plot_file = model_outdir / candidate
        if plot_file.exists():
            return plot_file
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Any other argument accepted by the individual model scripts "
        "(e.g. --backstop_file, --interrupt, --state-builder, "
        "--non_load_events, --T-init, etc.) is forwarded to every model run "
        "unchanged, except for --outdir, which is used here to construct a "
        "per-model subdirectory.",
    )
    parser.add_argument(
        "--outdir",
        default="out",
        help="Output directory. A subdirectory will be created within it "
        "for each model, and a combined index page will be written to it. "
        "If it does not exist it will be created. Default: 'out'",
    )
    head_path = Path("/proj/web-cxc/htdocs/acis/Thermal/tests")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Store outputs in an ACIS-ops web-accessible directory.",
    )
    args, remaining = parser.parse_known_args()
    if args.web:
        args.outdir = head_path / f"{date.today().year}" / args.outdir
    else:
        args.outdir = Path(args.outdir)
    return args, remaining


def run_model(model_name, remaining_args, top_outdir):
    """
    Run a single model's checking script as a subprocess, writing its
    outputs to a subdirectory of ``top_outdir`` named ``out_<model_name>``.

    Returns
    -------
    (bool, Path)
        Whether the run succeeded, and the output directory used for
        this model.
    """
    _, module_name, _ = MODELS[model_name]
    outdir_name = "fptemp" if model_name == "acisfp" else model_name
    model_outdir = top_outdir / f"out_{outdir_name}"
    model_outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        f"acis_thermal_check.apps.{module_name}",
        f"--outdir={model_outdir}",
        *remaining_args,
    ]
    mylog.info("Running %s -> %s", model_name, model_outdir)
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0, model_outdir


def write_index(top_outdir, results):
    """
    Write a top-level reST/HTML index page linking to each model's own
    report, using the model's prediction plot as the link.

    Parameters
    ----------
    top_outdir : Path
        The top-level output directory.
    results : list of (model_name, success, model_outdir)
        The outcome of each model run, in the order the models were run.
    """
    import docutils.writers.html4css1
    from docutils.core import publish_file

    # Copy the same stylesheets used by the individual model reports so
    # that this combined index page matches their look.
    dirname = PurePath(docutils.writers.html4css1.__file__).parent
    shutil.copy2(dirname / "html4css1.css", top_outdir)
    shutil.copy2(
        TASK_DATA / "acis_thermal_check/templates/acis_thermal_check.css",
        top_outdir,
    )

    lines = [
        "=============================================",
        f"ACIS Thermal Check: {top_outdir.name}",
        "=============================================",
        "",
        f"Run Time: {CxoTime.now().yday}",
        "---------------------------------------------",
        "",
        ".. raw:: html",
        "",
    ]

    html = [
        "<style>",
        "body { margin: 0 auto; }",
        (
            ".model-grid { display: grid; "
            "grid-template-columns: repeat(2, 1fr); gap: 24px; "
            "max-width: 1100px; margin: 1em auto; justify-content: center; }"
        ),
        ".model-box { text-align: center; }",
        ".model-title { font-weight: bold; margin-bottom: 6px; }",
        (
            ".model-box img { border: 3px solid #888888; padding: 4px; "
            "max-width: 100%; height: auto; }"
        ),
        ".model-failed { color: red; font-weight: bold; margin-top: 6px; }",
        "</style>",
        '<div class="model-grid">',
    ]
    for model_name, success, model_outdir in results:
        _, _, plot_candidates = MODELS[model_name]
        title = MODELS[model_name][0].upper()
        plot_file = find_plot_file(model_outdir, plot_candidates)
        index_file = model_outdir / "index.html"
        rel_index = f"{model_outdir.name}/index.html"

        html.append('<div class="model-box">')
        html.append(f'<div class="model-title">{title}</div>')
        if plot_file is not None:
            rel_plot = f"{model_outdir.name}/{plot_file.name}"
            img_tag = f'<img src="{rel_plot}" alt="{title}">'
            if index_file.exists():
                html.append(f'<a href="{rel_index}">{img_tag}</a>')
            else:
                html.append(img_tag)
            if not success:
                html.append('<div class="model-failed">FAILED</div>')
        else:
            html.append('<div class="model-failed">FAILED</div>')
        html.append("</div>")
    html.append("</div>")

    lines.extend("    " + line for line in html)
    lines.append("")

    rst_file = top_outdir / "index.rst"
    rst_file.write_text("\n".join(lines) + "\n")

    stylesheet_path = str(top_outdir / "acis_thermal_check.css")
    publish_file(
        source_path=str(rst_file),
        destination_path=str(top_outdir / "index.html"),
        writer="html",
        settings_overrides={"stylesheet_path": stylesheet_path},
    )


def main():
    args, remaining = parse_args()

    if not args.outdir.exists():
        args.outdir.mkdir(parents=True)

    results = []
    any_failed = False
    for model_name in MODELS:
        success, model_outdir = run_model(model_name, remaining, args.outdir)
        results.append((model_name, success, model_outdir))
        if not success:
            any_failed = True
            mylog.warning("Model %s FAILED", model_name)

    write_index(args.outdir, results)

    mylog.info("Wrote combined index to %s", args.outdir / "index.html")
    if args.web:
        print(
            f"Installed pages to https://cxc.harvard.edu/acis/Thermal/tests/{date.today().year}/{args.outdir.name}/."
        )
    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
