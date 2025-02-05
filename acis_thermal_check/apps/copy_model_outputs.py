#!/usr/bin/env python

import shutil
from argparse import ArgumentParser
from pathlib import Path

model_choices = ["dpa", "dea", "psmc", "acisfp"]

base_path = Path("/proj/web-cxc/htdocs/acis")
load_path = Path("/data/acis/LoadReviews")


def main():
    parser = ArgumentParser()
    parser.set_defaults()
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

    location = Path(args.location)
    if not location.exists():
        raise ValueError(f'Model location "{location}" does not exist!')

    rst_file = location / "index.rst"
    if not rst_file.exists():
        raise ValueError(f'Model index file "{rst_file}" does not exist!')

    with open(rst_file, "r") as f:
        lines = f.readlines()

    found_model_type = False
    for line in lines:
        words = line.strip().split()
        if "Temperatures Check" in line and len(words) == 3:
            model = words[0].lower()
            found_model_type = True
            break

    if not found_model_type:
        raise ValueError(f'Could not determine model from files in "{location}"!')

    if model not in model_choices:
        raise ValueError(
            f'Model "{model}" is not a valid model! Choices are {model_choices}'
        )

    print(f'Files to be copied are from a "{model}" model run.')

    model_str = "FP" if model == "acisfp" else model.upper()

    copy_path = (
        base_path / f"{model_str}_thermPredic" / load_week / f"ofls{load_letter}"
    )
    if not copy_path.exists() and not args.dry_run:
        copy_path.mkdir(parents=True)
    if args.dry_run:
        prefix = "Would have copied"
    else:
        prefix = "Copied"
        try:
            shutil.copytree(location, copy_path, dirs_exist_ok=args.overwrite)
        except FileExistsError:
            raise IOError(
                f"Files already exist in {copy_path} and --overwrite is not specified!"
            )
    print(f"{prefix} contents of {location} to {copy_path}.")


if __name__ == "__main__":
    main()
