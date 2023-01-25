from acis_thermal_check.apps.cea_check import CEACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_SEP1922A_viols(answer_store, test_root):
    answer_data = tests_path / "cea/answers/SEP1922A_viol.json"
    cea_rt = RegressionTester(CEACheck, test_root=test_root, sub_dir="viols")
    cea_rt.check_violation_reporting(
        "SEP1922A", answer_data, answer_store=answer_store, state_builder="kadi"
    )
