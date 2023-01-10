from acis_thermal_check.apps.fep1_actel_check import FEP1ActelCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_JUL2919A_viols(answer_store, test_root):
    answer_data = tests_path / "fep1_actel/answers/JUL2919A_viol.json"
    fa_rt = RegressionTester(FEP1ActelCheck, test_root=test_root, sub_dir="viols")
    fa_rt.check_violation_reporting("JUL2919A", answer_data, answer_store=answer_store)
