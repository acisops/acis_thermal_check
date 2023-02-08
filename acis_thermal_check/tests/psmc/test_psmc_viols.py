from acis_thermal_check.apps.psmc_check import PSMCCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_FEB1020A_viols(answer_store, test_root):
    answer_data = tests_path / "psmc/answers/FEB1020A_viol.json"
    psmc_rt = RegressionTester(PSMCCheck, test_root=test_root, sub_dir="viols")
    psmc_rt.check_violation_reporting(
        "FEB1020A",
        answer_data,
        answer_store=answer_store,
    )
