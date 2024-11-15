# Uses jrk2cmd to send and receive data from the Jrk G2 over USB.
# Works with either Python 2 or Python 3.
#
# NOTE: The Jrk's input mode must be "Serial / I2C / USB".

import subprocess
import yaml


def jrk2cmd(*args):
    return subprocess.check_output(['jrk2cmd'] + list(args))


status = yaml.safe_load(jrk2cmd('-d', '00425280','-s', '--full'))
print(status)
feedback = status['Scaled feedback']
print("Feedback is {}.".format(feedback))

target = status['Target']
print("Target is {}.".format(target))

# jrk2cmd('-d', '00425280','--target', str(2800))