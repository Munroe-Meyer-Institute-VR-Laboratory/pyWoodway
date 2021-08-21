from pywoodway.treadmill import SplitBelt, find_treadmills
import time


a_sn = 'FTHCUWVAA'
b_sn = 'FTHCUQ9IA'
a_port, b_port = find_treadmills(a_sn=a_sn, b_sn=b_sn)

if a_port is not None and b_port is not None:
    print("Split belt treadmill found on ports", a_port, "and", b_port)
    sb = SplitBelt(a_port, b_port)
    print("Belt A set to 2 MPH and belt B set to -2 MPH.")
    sb.set_speed(2.0, -2.0)
    time.sleep(10)
    print("Split belt speed:", sb.get_speeds())
    print("Belt A set to -2 MPH and belt B set to 2 MPH.")
    sb.set_speed(-2.0, 2.0)
    time.sleep(10)
    print("Split belt speed:", sb.get_speeds())
    sb.stop_belts()
    print("Split belt is stopped.")
    sb.close()
else:
    print("Split belt treadmill was not found.")
