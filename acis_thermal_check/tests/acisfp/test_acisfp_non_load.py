from acis_thermal_check.apps.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_acisfp_non_load(test_root, caplog):
    rt = RegressionTester(
        ACISFPCheck, test_root=test_root, sub_dir="non_load", caplog=caplog
    )
    out_dir = rt.outdir / "acisfp_kadi"
    rt.run_model(
        load_week=None,
        run_start="2024:024:00:00:00",
        set_time_now="2024:025:20:00:00",
        interrupt=True,
        out_dir=out_dir,
        state_builder="kadi",
    )
    out_dir = rt.outdir / "acisfp_nonload"
    rt.run_model(
        load_week=None,
        run_start="2024:024:00:00:00",
        set_time_now="2024:025:12:00:00",
        interrupt=True,
        out_dir=out_dir,
        state_builder="kadi",
        non_load_events=tests_path
        / "data/non_loads"
        / "test_non_load_events_JAN2624A.txt",
    )
