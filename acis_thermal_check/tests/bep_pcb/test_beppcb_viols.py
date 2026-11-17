from acis_thermal_check.apps.bep_pcb_check import BEPPCBCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_DEC0825A_viols(answer_store, test_root):
    answer_data = tests_path / "bep_pcb/answers/DEC0825A_viol.json"
    beppcb_rt = RegressionTester(BEPPCBCheck, test_root=test_root, sub_dir="viols")
    beppcb_rt.check_violation_reporting(
        "DEC0825A",
        answer_data,
        answer_store=answer_store,
    )
