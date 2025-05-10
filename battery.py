class IoTBatteryLinear:

    def __init__(self, SoC_0, A, acceleration_factor):
        self.SoC = SoC_0
        self.A = A * acceleration_factor
    
    def drain(self, t):
        # this time is in hour
        self.SoC -= self.A * (t / 3600.0)
        if self.SoC < 0:
            self.SoC = 0
