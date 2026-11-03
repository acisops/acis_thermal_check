from acis_thermal_check.apps.psmc_check import PSMCCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_DEC0825A_viols(answer_store, test_root):
    answer_data = tests_path / "psmc/answers/DEC0825A_viol.json"
    psmc_rt = RegressionTester(PSMCCheck, test_root=test_root, sub_dir="viols")
    psmc_rt.check_violation_reporting(
        "DEC0825A",
        answer_data,
        answer_store=answer_store,
    )
