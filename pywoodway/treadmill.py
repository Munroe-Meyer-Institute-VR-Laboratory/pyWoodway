import serial
from serial.tools import list_ports


class TreadmillCommands:
    START_BELT_TIMER = 160
    DISENGAGE_BELT = 162
    SET_SPEED = 163
    SET_ELEVATION = 164
    START_BELT = 169
    AUTO_STOP = 170
    TEST_COMMS = 192
    GET_SPEED = 193
    GET_ELEVATION = 194
    GET_FW_REV = 195


class TreadmillReturns:
    START_BELT_TIMER = b'\xb0'
    DISENGAGE_BELT = 0xB2
    SET_SPEED = b'\xb3'
    SET_ELEVATION = 0xB4
    START_BELT = b'\xb9'
    AUTO_STOP = b'\xba'
    MASTER_TIMEOUT = 0xBD
    INVALID_DATA = 0xBE
    INVALID_COMMAND = 0xBF
    TEST_COMMS = b'\xd0'
    GET_SPEED = b'\xd1'
    GET_ELEVATION = 0xD2
    GET_FW_REV = 0xD3


# 'FTHCUWVAA' - comport A
# 'FTHCUQ9IA' - comport B
def find_treadmills(a_sn=None, b_sn=None):
    ports = list_ports.comports()
    a_port, b_port = None, None
    found_ports = []
    for port in ports:
        if a_sn is not None:
            if port.serial_number == a_sn:
                a_port = port
                continue
        if b_sn is not None:
            if port.serial_number == b_sn:
                b_port = port
                continue
    if a_port is not None:
        found_ports.append(a_port)
    if b_port is not None:
        found_ports.append(b_port)
    return found_ports


class Treadmill:
    def __init__(self, comport):
        self.comport = serial.Serial(comport, baudrate=4800, stopbits=1)
        if self.test_treadmill():
            self.stop_belt()
        self.forward = False
        self.reverse = False
        self.sending = False

    def close(self):
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.close()

    def test_treadmill(self):
        if self.comport is not None:
            if self.comport.isOpen():
                command = bytearray()
                command.append(TreadmillCommands.TEST_COMMS)
                print(command)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.TEST_COMMS:
                    print("State:", self.comport.read(1))
                    return True
                else:
                    print("Something went wrong, code:", return_code)
                    return False

    def get_fw_rev(self):
        raise NotImplemented

    def start_belt(self, timer):
        if self.comport is not None:
            if self.comport.isOpen():
                if timer:
                    command = bytearray()
                    command.append(TreadmillCommands.START_BELT_TIMER)
                    self.comport.write(command)
                    return_code = self.comport.read(1)
                    if return_code == TreadmillReturns.START_BELT_TIMER:
                        return True
                    else:
                        print("Something went wrong, code:", return_code)
                        return False
                else:
                    command = bytearray()
                    command.append(TreadmillCommands.START_BELT)
                    self.comport.write(command)
                    return_code = self.comport.read(1)
                    if return_code == TreadmillReturns.START_BELT:
                        return True
                    else:
                        print("Something went wrong, code:", return_code)
                        return False

    def set_speed(self, mph):
        if self.comport is not None:
            if self.comport.isOpen():
                if isinstance(mph, float):
                    command = bytearray()
                    command.append(TreadmillCommands.SET_SPEED)
                    if mph > 0.0:
                        self.forward = True
                        self.reverse = False
                        command.append(ord('0'))
                    else:
                        self.forward = False
                        self.reverse = True
                        command.append(ord('3'))
                    if mph < 10.0:
                        command.append(ord('0'))
                    mph_digits = [ord(i) for i in str(mph)]
                    for digit in mph_digits:
                        if digit != 46:
                            command.append(digit)
                    self.comport.write(command)
                    return_code = self.comport.read(1)
                    if return_code == TreadmillReturns.SET_SPEED:
                        return True
                    else:
                        print("Something went wrong, code:", return_code)
                        return False
                else:
                    raise ValueError("Parameter invalid - mph must be a float!")

    def get_speed(self):
        if self.comport is not None:
            if self.comport.isOpen():
                command = bytearray()
                command.append(TreadmillCommands.GET_SPEED)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.GET_SPEED:
                    speed_bytes = self.comport.read(4)
                    speed = float((speed_bytes[1] - 48) * 10.0) + \
                            float((speed_bytes[2] - 48)) + \
                            float((speed_bytes[3] - 48) / 10.0)
                    if speed_bytes[0] == 51:
                        speed = -speed
                    return speed
                else:
                    print("Something went wrong, code:", return_code)
                    return False

    def set_elevation(self, elevation):
        raise NotImplemented

    def get_elevation(self):
        raise NotImplemented

    def stop_belt(self):
        if self.comport is not None:
            if self.comport.isOpen():
                command = bytearray()
                command.append(TreadmillCommands.AUTO_STOP)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.AUTO_STOP:
                    return True
                else:
                    print("Something went wrong, code:", return_code)
                    return False

    def disengage_belt(self):
        raise NotImplemented


class SplitBelt:
    def __init__(self, comport_a, comport_b):
        self.belt_a = Treadmill(comport_a)
        self.belt_b = Treadmill(comport_b)

    def start_belts(self, start_a, a_timer, start_b, b_timer):
        success = False
        if start_a:
            if self.belt_a.start_belt(a_timer):
                success = True
            else:
                return False
        if start_b:
            if self.belt_b.start_belt(b_timer):
                success = True
            else:
                return False
        return success

    def set_speed(self, a_mph, b_mph):
        if self.belt_a.set_speed(a_mph):
            if self.belt_b.set_speed(b_mph):
                return True
        return False

    def stop_belts(self, a_stop, b_stop):
        if a_stop:
            self.belt_a.stop_belt()
        if b_stop:
            self.belt_b.stop_belt()
