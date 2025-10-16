import pytest

from acis_thermal_check.apps.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


@pytest.mark.filterwarnings("ignore:Ignoring specified arguments in this call")
def test_FEB2122_acis_obsids(answer_store, test_root, caplog):
    answer_data = tests_path / "acisfp/answers/FEB2122A_acis_obsids.json"
    fp_rt = RegressionTester(
        ACISFPCheck, test_root=test_root, sub_dir="acis_obsids", caplog=caplog
    )
    fp_rt.check_acis_obsids("FEB2122A", answer_data, answer_store=answer_store)


@pytest.mark.filterwarnings("ignore:Ignoring specified arguments in this call")
def test_FEB2822_acis_obsids(answer_store, test_root, caplog):
    answer_data = tests_path / "acisfp/answers/FEB2822A_acis_obsids.json"
    fp_rt = RegressionTester(
        ACISFPCheck, test_root=test_root, sub_dir="acis_obsids", caplog=caplog
    )
    fp_rt.check_acis_obsids("FEB2822A", answer_data, answer_store=answer_store)


@pytest.mark.filterwarnings("ignore:Ignoring specified arguments in this call")
def test_MAR0722_acis_obsids(answer_store, test_root, caplog):
    answer_data = tests_path / "acisfp/answers/MAR0722A_acis_obsids.json"
    fp_rt = RegressionTester(
        ACISFPCheck, test_root=test_root, sub_dir="acis_obsids", caplog=caplog
    )
    fp_rt.check_acis_obsids("MAR0722A", answer_data, answer_store=answer_store)
