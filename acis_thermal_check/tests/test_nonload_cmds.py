import pytest

from acis_thermal_check.state_builder import (
    acis_ecs_event,
    maneuver_event,
)


def test_maneuver_event():
    cmds = maneuver_event("2026:290:13:00:00", (150.0, 20.0, 0.0))
    assert list(cmds["tlmsid"]) == [
        "AONMMODE",
        "AONM2NPE",
        "AOUPTARQ",
        "AOMANUVR",
    ]
    assert cmds["date"][0] == "2026:290:13:00:00.000"


def test_maneuver_event_bad_att():
    with pytest.raises(ValueError, match="3-element"):
        maneuver_event("2026:290:13:00:00", (1.0, 2.0))


def test_acis_cti_event():
    cmds = acis_ecs_event("2026:291:00:00:00", "1_ECS3B", 24)
    assert list(cmds["tlmsid"]) == [
        "OORMPEN",
        "AA00000000",
        "WSPOW00000",
        "WSPOW08C0E",
        "WT00DA4014",
        "XTZ0000005",
        "RS_0000001",
        "RH_0000001",
        "AA00000000",
        "AA00000000",
        "WSPOW0002A",
        "RS_0000001",
        "OORMPDS",
    ]
