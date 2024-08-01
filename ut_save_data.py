from phidget_interface import *

pif = PhidgetInterface()
pif.set_file_name("TGest")
pif.connect()
time.sleep(2)
pif.save_data()
pif.disconnect()

