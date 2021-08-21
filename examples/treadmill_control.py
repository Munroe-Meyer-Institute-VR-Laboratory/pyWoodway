from pywoodway.treadmill import Treadmill, find_treadmills
import time


port_sn = 'FTHCUWVAA'
port = find_treadmills(a_sn=port_sn)

if port is not None:
    print("Treadmill found on port", port[0].name)
    tm = Treadmill(port[0].name)
    print("Treadmill is set to 2.0 MPH")
    tm.set_speed(2.0)
    time.sleep(10)
    print("Treadmill speed:", tm.get_speed())
    print("Treadmill is set to -2.0 MPH")
    tm.set_speed(-2.0)
    time.sleep(10)
    print("Treadmill speed:", tm.get_speed())
    tm.stop_belt()
    print("Treadmill is stopped.")
    tm.close()
else:
    print("No treadmills found.")
