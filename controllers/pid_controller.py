class PIDController:
    def __init__(self, kp, ki, kd, i_limit, out_limit, sampling_time):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_limit = i_limit
        self.out_limit = out_limit
        self.error = 0.0
        self.prev_error = 0.0

        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        self.sampling_time = sampling_time

    def update(self, feedback, target):
        self.error = target - feedback
        self.p_term = self.kp * self.error
        self.i_term = self.i_term + self.ki * self.error
        self.d_term = self.kd * (self.error - self.prev_error)/self.sampling_time

        # Avoid integral term saturation and result in low response
        if self.i_term > self.i_limit:
            self.i_term = self.i_limit
        elif self.i_term < -self.i_limit:
            self.i_term = -self.i_limit

        return max(-self.out_limit, min(self.p_term + self.i_term + self.d_term, self.out_limit))

    def clear_errors(self):
        self.error = 0.0
        self.prev_error = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0

    def set_pid_params(self, kp, ki, kd, i_limit, out_limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_limit = i_limit
        self.out_limit = out_limit

    def get_pid_params(self):
        return [self.kp, self.ki, self.kd, self.i_limit, self.out_limit]