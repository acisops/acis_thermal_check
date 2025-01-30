#!/usr/bin/env python

import shutil
from argparse import ArgumentParser
from pathlib import Path

model_choices = ["dpa", "dea", "psmc", "fp"]

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
        "location",
        type=str,
        help="The location of the model files to copy",
    )
    parser.add_argument(
        "load",
        type=str,
        help="The load name. Must be 8 characters, e.g. 'JAN2725A'",
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
    load_year = f"20{load_week[-2:]}"

    load_dir = load_path / load_year / load_week / f"ofls{load_letter}"
    if not load_dir.exists():
        raise ValueError(f"Load directory {load_dir} does not exist")

    if args.model not in model_choices:
        raise ValueError(f"Model {args.model} is not a valid model!")

    location = Path(args.location)
    if not location.exists():
        raise ValueError(f"Model location {location} does not exist!")

    copy_path = (
        base_path
        / f"{args.model.upper()}_thermPredic"
        / load_week
        / f"ofls{load_letter}"
    )
    if not copy_path.exists() and not args.dry_run:
        copy_path.mkdir(parents=True)
    if args.dry_run:
        print(f"Would copy {location} to {copy_path}.")
    else:
        shutil.copytree(location, copy_path, dirs_exist_ok=args.overwrite)
