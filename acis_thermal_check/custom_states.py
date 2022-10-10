from kadi.commands.states import FixedTransition


class Hrc15vOn_Transition(FixedTransition):
    """HRC 15V ON"""

    command_attributes = {"tlmsid": "215PCAON"}
    state_keys = ["hrc_15v"]
    transition_key = "hrc_15v"
    transition_val = "ON"


class Hrc15vOff_Transition(FixedTransition):
    """HRC 15V OFF"""

    command_attributes = {"tlmsid": "215PCAOF"}
    state_keys = ["hrc_15v"]
    transition_key = "hrc_15v"
    transition_val = "OFF"


class HrcIOn_Transition(FixedTransition):
    """HRC-I ON"""

    command_attributes = {"tlmsid": "COENASX", "coenas1": 89}
    state_keys = ["hrc_i"]
    transition_key = "hrc_i"
    transition_val = "ON"


class HrcIOff_Transition(FixedTransition):
    """HRC-I OFF"""

    command_attributes = {"tlmsid": "215PCAOF", }
    state_keys = ["hrc_i"]
    transition_key = "hrc_i"
    transition_val = "OFF"


class HrcSOn_Transition(FixedTransition):
    """HRC-S ON"""

    command_attributes = {"tlmsid": "COENASX", "coenas1": 90}
    state_keys = ["hrc_s"]
    transition_key = "hrc_s"
    transition_val = "ON"


class HrcSOff_Transition(FixedTransition):
    """HRC-S OFF"""

    command_attributes = {"tlmsid": "215PCAOF", }
    state_keys = ["hrc_s"]
    transition_key = "hrc_s"
    transition_val = "OFF"
