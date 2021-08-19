import serial


class TreadmillCommands:
    START_BELT_TIMER = 0xA0
    DISENGAGE_BELT = 0xA2
    SET_SPEED = 0xA3
    SET_ELEVATION = 0xA4
    START_BELT = 0xA9
    AUTO_STOP = 0xAA
    TEST_COMMS = 0xC0
    GET_SPEED = 0xC1
    GET_ELEVATION = 0xC2
    GET_FW_REV = 0xC3


class TreadmillReturns:
    START_BELT = 0xB0
    DISENGAGE_BELT = 0xB2
    SET_SPEED = 0xB3
    SET_ELEVATION = 0xB4
    AUTO_STOP = 0xBA
    MASTER_TIMEOUT = 0xBD
    INVALID_DATA = 0xBE
    INVALID_COMMAND = 0xBF
    TEST_COMMS = 0xD0
    GET_SPEED = 0xD1
    GET_ELEVATION = 0xD2
    GET_FW_REV = 0xD3


class Treadmill:
    def __init__(self, comport):
        self.comport = serial.Serial(comport=comport, baudrate=4800, stopbits=1)

    def start_belt(self, timer):
        raise NotImplemented

    def set_speed(self, mph):
        raise NotImplemented

    def set_elevation(self, elevation):
        raise NotImplemented

    def stop_belt(self):
        raise NotImplemented

    def disengage_belt(self):
        raise NotImplemented


class SplitBelt:
    def __init__(self, comport_a, comport_b):
        self.belt_a = Treadmill(comport_a)
        self.belt_b = Treadmill(comport_b)