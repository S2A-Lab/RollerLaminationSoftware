class PIDController:
    def __init__(self, Kp, Ki, Kd, Ka):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Ka = Ka
        self.error = 0.0
        self.prev_error = 0.0

    def update(self, error):
        self.prev_error = error
        self.error = error
