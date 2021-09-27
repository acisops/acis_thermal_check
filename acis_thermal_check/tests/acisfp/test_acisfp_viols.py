from acis_thermal_check.scripts.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, tests_path


def test_DEC0919A_viols(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/DEC0919A_viol.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='viols')
    fp_rt.check_violation_reporting("DEC0919A", answer_data,
                                    answer_store=answer_store)


def test_SEP1321A_viols(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/SEP1321A_viol.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='viols')
    fp_rt.check_violation_reporting("SEP1321A", answer_data,
                                    answer_store=answer_store)


def test_JUN1421A_viols(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/JUN1421A_viol.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='viols')
    fp_rt.check_violation_reporting("JUN1421A", answer_data,
                                    answer_store=answer_store)
