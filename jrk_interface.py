from serial import Serial


class JRKInterface:
    current_target = [0, 0]
    feedback = [0, 0]

    def __init__(self):
        self.current_target = [0, 0]

