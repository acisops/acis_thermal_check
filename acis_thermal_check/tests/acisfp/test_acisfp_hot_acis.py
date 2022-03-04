from acis_thermal_check.apps.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, tests_path


def test_FEB2122_hot_acis(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/FEB2122A_hot_acis.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='hot_acis')
    fp_rt.check_hot_acis_reporting("FEB2122A", answer_data,
                                   answer_store=answer_store)


def test_FEB2822_hot_acis(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/FEB2822A_hot_acis.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='hot_acis')
    fp_rt.check_hot_acis_reporting("FEB2822A", answer_data,
                                    answer_store=answer_store)


def test_MAR0722_hot_acis(answer_store, test_root):
    answer_data = tests_path / "acisfp/answers/MAR0722A_hot_acis.json"
    fp_rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='hot_acis')
    fp_rt.check_hot_acis_reporting("MAR0722A", answer_data,
                                   answer_store=answer_store)
