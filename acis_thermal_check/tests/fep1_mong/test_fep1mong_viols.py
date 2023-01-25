from acis_thermal_check.apps.fep1_mong_check import FEP1MongCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_JUL3019A_viols(answer_store, test_root):
    answer_data = tests_path / "fep1_mong/answers/JUL2919A_viol.json"
    fm_rt = RegressionTester(FEP1MongCheck, test_root=test_root, sub_dir="viols")
    fm_rt.check_violation_reporting("JUL2919A", answer_data, answer_store=answer_store)
