from pathlib import Path

from acis_thermal_check.apps.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_dpa_pred_only(answer_store, test_root):
    dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="pred_only")
    out_dir = dpa_rt.outdir / "dpa2024"
    dpa_rt.run_model(
        run_start="2024:300:12:50:00",
        out_dir=out_dir,
        state_builder="kadi",
        pred_only=True,
    )
    answer_dir = tests_path / "dpa/answers/pred_only"
    filenames = ["temperatures.dat", "states.dat"]
    assert not Path(answer_dir / "validation_data.pkl").exists()
    if not answer_store:
        dpa_rt.compare_prediction(answer_dir, out_dir, filenames)
    else:
        dpa_rt.copy_new_files(out_dir, answer_dir, filenames)
