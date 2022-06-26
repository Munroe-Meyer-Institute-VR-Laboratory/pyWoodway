import serial
from serial.tools import list_ports


class TreadmillCommands:
    """
    The command set for a Woodway treadmill.
    """
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
    """
    The return commands from a Woodway treadmill.
    """
    START_BELT_TIMER = b'\xb0'
    DISENGAGE_BELT = b'\xb2'
    SET_SPEED = b'\xb3'
    SET_ELEVATION = b'\xb4'
    START_BELT = b'\xb9'
    AUTO_STOP = b'\xba'
    MASTER_TIMEOUT = b'\xbd'
    INVALID_DATA = b'\xbe'
    INVALID_COMMAND = b'\xbf'
    TEST_COMMS = b'\xd0'
    GET_SPEED = b'\xd1'
    GET_ELEVATION = b'\xd2'
    GET_FW_REV = b'\xd3'


# 'FTHCUWVAA' - comport A
# 'FTHCUQ9IA' - comport B
def find_treadmills(a_sn=None, b_sn=None):
    """
    Searches available COM ports for the corresponding serial numbers for the A and B treadmill.
    Plug in your treadmill belts, navigate to the 'Device Manager', and look in the properties of the treadmill
    COM port for the serial number of the FTDI chip of your treadmill.
    :param a_sn: str: serial number for the A treadmill
    :param b_sn: str: serial number for the B treadmill
    :return: np-list: contains the COM ports, first is A, second is B.
    """
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
    """
    Class object to control a single treadmill belt. Should be compatible with all Woodway treadmills.
    """

    def __init__(self, comport):
        """
        Connects to the comport specified, stops the treadmill, and sets the control variables.
        :param comport: str: name of comport to connect to.
        """
        self.comport = serial.Serial(comport, baudrate=4800, stopbits=1)
        if self.test_treadmill():
            self.stop_belt()
        self.running = False
        self.forward = False
        self.reverse = False
        self.sending = False
        self.treadmill_state = None
        self.last_error = None

    def close(self):
        """
        Closes the comport, if it's open.
        :return: None.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.close()

    def test_treadmill(self):
        """
        Sends the test comms command and prints the returned value.
        :return: bool: True if comms are good, False if not.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                command = bytearray()
                command.append(TreadmillCommands.TEST_COMMS)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.TEST_COMMS:
                    self.treadmill_state = self.comport.read(1)
                    return True
                else:
                    self.last_error = (return_code, f"Test Treadmill Command {command}")
                    return False

    def get_fw_rev(self):
        """
        Gets the firmware revision of the treadmill.
        :return: int: firmware revision, False if command fails.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                command = bytearray()
                command.append(TreadmillCommands.GET_FW_REV)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.GET_FW_REV:
                    fw_bytes = self.comport.read(4)
                    fw_rev = (fw_bytes[0] << 24) | (fw_bytes[1] << 16) | (fw_bytes[2] << 8) | fw_bytes[3]
                    return fw_rev
                else:
                    self.last_error = (return_code, f"Get FW Rev {command}")
                    return False

    def start_belt(self, timer):
        """
        Engages power to the belt, starts communication timer if timer is True.
        :param timer: bool: Sends the start belt command with timeout if True/
        :return: bool: True if belt starts, False if it fails.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                if timer:
                    command = bytearray()
                    command.append(TreadmillCommands.START_BELT_TIMER)
                    self.comport.write(command)
                    return_code = self.comport.read(1)
                    if return_code == TreadmillReturns.START_BELT_TIMER:
                        self.running = True
                        return True
                    else:
                        self.last_error = (return_code, f"Start Belt Timer {command}")
                        return False
                else:
                    command = bytearray()
                    command.append(TreadmillCommands.START_BELT)
                    self.comport.write(command)
                    return_code = self.comport.read(1)
                    if return_code == TreadmillReturns.START_BELT:
                        self.running = True
                        return True
                    else:
                        self.last_error = (return_code, f"Start Belt Timer {command}")
                        return False

    def set_speed(self, mph):
        """
        Sets the speed of the treadmill.  If treadmill is engaged, the belt will start moving.
        :param mph: float: speed of the belt in MPH, max speed is 29.9.
        :return: True if successful, False if failed, raises ValueError if parameter is not valid.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                if isinstance(mph, float):
                    if mph > 29.9:
                        raise ValueError("Set speed is too high, speed must be below 29.9 MPH.")
                    else:
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
                            if digit not in [46, 45]:
                                command.append(digit)
                        self.comport.write(command)
                        return_code = self.comport.read(1)
                        if return_code == TreadmillReturns.SET_SPEED:
                            return True
                        else:
                            self.last_error = (return_code, f"Set Belt Speed {command}")
                            return False
                else:
                    raise ValueError("Parameter invalid - mph must be a float!")

    def get_speed(self):
        """
        Gets the current speed of the treadmill.  The treadmill has a ramp up, so it may take a few seconds, to reach
        the set speed.
        :return: True if successful, False if failed.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
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
                    self.last_error = (return_code, f"Get Belt Speed {command}")
                    return False

    def set_elevation(self, elevation):
        """
        Sets the inclination of the treadmill in units of percentage.  Max value is 29.9%.
        :param elevation: float: Elevation in percentage, must be below 29.9%
        :return: bool: True if successful, False if failed, raises ValueError if elevation is invalid.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                if isinstance(elevation, float):
                    if elevation > 29.9:
                        raise ValueError("Over elevation, max inclination is 29.9%.")
                    else:
                        command = bytearray()
                        command.append(TreadmillCommands.SET_ELEVATION)
                        if elevation < 100.0:
                            command.append(ord('0'))
                        if elevation < 10.0:
                            command.append(ord('0'))
                        elevation_digits = [ord(i) for i in str(elevation)]
                        for digit in elevation_digits:
                            if digit != 46:
                                command.append(digit)
                        self.comport.write(command)
                        return_code = self.comport.read(1)
                        if return_code == TreadmillReturns.SET_ELEVATION:
                            return True
                        else:
                            self.last_error = (return_code, f"Set Belt Elevation {command}")
                            return False
                else:
                    raise ValueError("Elevation must be a float.")

    def get_elevation(self):
        """
        Gets the current elevation of the treadmill, the elevation has a ramp up time, so it may take a short period
        to get to set elevation.
        :return: float: current elevation of treadmill belt.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                command = bytearray()
                command.append(TreadmillCommands.GET_ELEVATION)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.GET_ELEVATION:
                    elevation_bytes = self.comport.read(4)
                    elevation = float((elevation_bytes[0] - 48) * 100.0) + \
                                float((elevation_bytes[1] - 48) * 10.0) + \
                                float((elevation_bytes[2] - 48)) + \
                                float((elevation_bytes[3] - 48) / 10.0)
                    return elevation
                else:
                    self.last_error = (return_code, f"Get Elevation {command}")
                    print(self.last_error)
                    return False

    def is_connected(self):
        """
        Check if treadmill is connected
        :return: True if connected, False if disconnected
        """
        if self.comport is not None:
            if self.comport.isOpen():
                return True
        return False

    def stop_belt(self):
        """
        Stops the motion of the belt, sets the current inclination and speed to zero.
        :return: bool: True if successful, False if failed.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                command = bytearray()
                command.append(TreadmillCommands.AUTO_STOP)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.AUTO_STOP:
                    self.running = False
                    return True
                else:
                    self.last_error = (return_code, f"Stop Belt {command}")
                    return False

    def disengage_belt(self):
        """
        Disengages power to the belt.
        :return: bool: True if successful, False if failed.
        """
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.flushInput()
                self.comport.flushOutput()
                command = bytearray()
                command.append(TreadmillCommands.DISENGAGE_BELT)
                self.comport.write(command)
                return_code = self.comport.read(1)
                if return_code == TreadmillReturns.DISENGAGE_BELT:
                    self.running = False
                    return True
                else:
                    self.last_error = (return_code, f"Disengage Belt {command}")
                    return False


class SplitBelt:
    """
    Class to control the Woodway split belt treadmill.  Wraps two instances of the Treadmill class.
    """

    def __init__(self, comport_a, comport_b):
        """
        Initializes the A and B belt comports.
        :param comport_a: str: comport connected to A belt.
        :param comport_b: str: comport connected to B belt.
        """
        self.belt_a = Treadmill(comport_a)
        self.belt_b = Treadmill(comport_b)

    def start_belts(self, start_a, a_timer, start_b, b_timer):
        """
        Start individual belts and with timers.
        :param start_a: bool: start belt A
        :param a_timer: bool: start belt A timer
        :param start_b: bool: start belt B
        :param b_timer: bool: start belt B timer
        :return: bool: True if successful, False if failed.
        """
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
        """
        Sets the speed of the belts.
        :param a_mph: float: speed of belt A in MPH, max is 29.9 MPH.
        :param b_mph: float: speed of belt B in MPH, max is 29.9 MPH.
        :return: bool: True if successful, False if failed.
        """
        self.belt_a.set_speed(a_mph)
        self.belt_b.set_speed(b_mph)
        return False

    def stop_belts(self):
        """
        Stops the belts.
        :return: None.
        """
        self.belt_a.stop_belt()
        self.belt_b.stop_belt()

    def get_speeds(self):
        """
        Gets the speed of the belts.
        :return: np-list: First element is belt A speed, second element is belt B speed
        """
        return [self.belt_a.get_speed(), self.belt_b.get_speed()]

    def set_elevations(self, elevation):
        """
        Sets the elevation of both belts
        :param elevation:
        :return:
        """
        self.belt_a.set_elevation(elevation)
        # self.belt_b.set_elevation(b_elevation)

    def get_elevations(self):
        """
        Gets the elevation of the belts.
        :return: np-list: First element is belt A elevation, second element is belt B elevation
        """
        return self.belt_a.get_elevation()  # [self.belt_a.get_elevation(), self.belt_b.get_elevation()]

    def get_fw_revs(self):
        """
        Gets the firmware revision of the belts.
        :return: np-list: First element is belt A revision, second element is belt B revision
        """
        return [self.belt_a.get_fw_rev(), self.belt_b.get_fw_rev()]

    def is_connected(self):
        """
        Check if split belt is connected
        :return: tuple: First element is belt a status, second element is belt b status
        """
        connections = []
        if self.belt_a.is_connected():
            connections.append(True)
        else:
            connections.append(False)
        if self.belt_b.is_connected():
            connections.append(True)
        else:
            connections.append(False)
        return connections[0], connections[1]

    def close(self):
        """
        Closes the comports of the two belts
        :return: None.
        """
        self.belt_a.close()
        self.belt_b.close()
