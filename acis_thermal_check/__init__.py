import ska_helpers

__version__ = ska_helpers.get_version(__package__)

from acis_thermal_check.acis_obs import acis_filter, fetch_ocat_data
from acis_thermal_check.main import ACISThermalCheck, DPABoardTempCheck
from acis_thermal_check.utils import get_options, mylog


def test(*args, **kwargs):
    # Run py.test unit tests.
    import testr

    return testr.test(*args, **kwargs)
