
class Airplane:
    def __init__(self, name, min_velocity, max_velocity, ceiling, flight_time):
        self.name = name
        self.min_velocity = min_velocity
        self.max_velocity = max_velocity
        self.ceiling = ceiling
        self.flight_time = flight_time

    def getName(self):
        return self.name

    def getAvgVelocity(self):
        return 10 * (self.min_velocity + self.max_velocity) / 72

    def getVelocity(self):
        return 10 * self.max_velocity / 36, 10 * self.min_velocity / 36

    def getCeiling(self):
        return self.ceiling

    def getFlightTime(self):
        return self.flight_time


class Camera:
    def __init__(self, name, mat_size1, mat_size2, pixel_size, canal, focal_distance, duty_cycle, weight):
        self.name = name
        self.mat_size1 = mat_size1
        self.mat_size2 = mat_size2
        self.pixel_size = pixel_size
        self.canal = canal
        self.focal_distance = focal_distance
        self.duty_cycle = duty_cycle
        self.weight = weight

    def getPixelSize(self):
        return self.pixel_size

    def getFocalDistance(self):
        return self.focal_distance


