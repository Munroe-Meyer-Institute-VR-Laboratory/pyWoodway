from pywoodway.treadmill import Treadmill, find_treadmills


port_sn = 'FTHCUWVAA'
port = find_treadmills(a_sn=port_sn)


if port is not None:
    tm = Treadmill(port.name)
