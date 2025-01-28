#!/usr/bin/env python

import shutil
from argparse import ArgumentParser
from pathlib import Path

model_choices = ["DPA", "DEA", "PSMC", "FP"]

base_path = Path("/proj/web-cxc/htdocs/acis")
load_path = Path("/data/acis/LoadReviews")


def main():
    parser = ArgumentParser()
    parser.set_defaults()
    parser.add_argument(
        "model",
        type=str,
        help="The model to copy",
    )

    parser.add_argument(
        "load",
        type=str,
        help="The load name to copy. Must be 8 characters, e.g. 'JAN2725A'",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files."
    )
    parser.add_argument(
        "--dry_run", action="store_true", help="Show what would have been done."
    )

    args = parser.parse_args()

    if len(args.load) != 8:
        raise ValueError("Load name must be 8 characters, e.g. 'JAN2725A'")

    load_name = args.load.upper()
    load_week, load_letter = load_name[:7], load_name[7].lower()

    load_dir = load_path / load_name
    if not load_dir.exists():
        raise ValueError(f"Load directory {load_dir} does not exist")

    if args.model == "all":
        models = model_choices
    else:
        models = args.model.split(",")

    for model in models:
        if model not in model_choices:
            raise ValueError(f"Model {model} is not a valid model!")
        model_dir = "out_fptemp" if model == "FP" else f"out_{model.lower()}"
        model_path = load_dir / model_dir
        if not model_path.exists():
            raise ValueError(f"Model directory {model_path} does not exist")
        copy_path = (
            base_path / f"{model}_thermPredic" / load_week / f"ofls{load_letter}"
        )
        if args.dry_run:
            print(f"Would copy {model_path} to {copy_path}.")
        else:
            shutil.copytree(model_path, copy_path, dirs_exist_ok=args.overwrite)
