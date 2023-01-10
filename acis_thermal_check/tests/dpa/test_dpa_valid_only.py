import pytest

from acis_thermal_check.apps.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_dpa_valid_only(answer_store, test_root):
    dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="valid_only")
    out_dir = dpa_rt.outdir / "dpa2019"
    dpa_rt.run_model(run_start="2019:300:12:50:00", out_dir=out_dir)
    answer_dir = tests_path / "dpa/answers/valid_only"
    filenames = ["validation_data.pkl"]
    if not answer_store:
        dpa_rt.compare_validation(answer_dir, out_dir, filenames)
    else:
        dpa_rt.copy_new_files(out_dir, answer_dir, filenames)
