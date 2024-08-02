import numpy as np
class Timeseries:
    def __init__(self, filename):
        self.data = []
        self.timestamp = []
        self.__filename = filename

    def update_data(self, timestamp, data):
        self.data.append(data)
        self.timestamp.append(timestamp)

    def reset(self):
        self.__filename = ""
        self.timestamp = []
        self.data = []

    def set_filename(self, filename):
        self.__filename = filename

    def save_data(self):
        np.savetxt(self.__filename + ".csv", np.array([self.timestamp, self.data]).T, delimiter=",")