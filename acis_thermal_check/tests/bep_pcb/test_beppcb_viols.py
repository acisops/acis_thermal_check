from acis_thermal_check.apps.bep_pcb_check import BEPPCBCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_JUL2919A_viols(answer_store, test_root):
    answer_data = tests_path / "bep_pcb/answers/JUL2919A_viol.json"
    beppcb_rt = RegressionTester(BEPPCBCheck, test_root=test_root, sub_dir="viols")
    beppcb_rt.check_violation_reporting("JUL2919A", answer_data, answer_store=answer_store)
