from interfaces.interface_jrk import *

jif = JRKInterface()

jif.connect(get_ports()[0].device, 115200)
jif.send_target(10, 10)
