from Backend.Interfaces.interface_jrk import *

jif = JRKInterface()

jif.connect(get_ports()[0].device, 115200)
jif.set_target_position(10, 10)
