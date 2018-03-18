from printers import *


class RecordingPrinter(BasePrinter):
    def __init__(self, filename, separator=','):
        self.separator = separator
        self.printed_header = False
        self.data_points = []

    def print_data_header(self, t):
        pass

    def print_data(self, t, date):
        effective_power = t.voltage * t.current * t.power_factor
        data_point = (date, effective_power)
        self.data_points.append(data_point)

    def read_data_points(self):
        ret = self.data_points
        self.data_points = []
        return ret

