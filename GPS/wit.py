import platform
from GPS.device_model import DeviceModel

keys = ["magX",
        "magY",
        "magZ",
        "lon",
        "lat",
        "Height",
        "Yaw",
        "Speed",
        "q1",
        "q2",
        "q3",
        "q4",
        "Chiptime",
        "accX",
        "accY",
        "accZ",
        "temperature",
        "gyroX",
        "gyroY",
        "gyroZ",
        "angleX",
        "angleY",
        "angleZ"
        ]

class Wit:

    def __init__(self):
        device = DeviceModel()

        if (platform.system().lower() == 'linux'):
            device.serialConfig.portName = "/dev/ttyUSB0"
        else:
            device.serialConfig.portName = "COM4"
        device.serialConfig.baud = 9600
        device.openDevice()
        self.readConfig(device)
        device.dataProcessor.onVarChanged.append(self.onUpdate)

        self.data = {}
        for key in keys:
            self.data[key] = None


    def readConfig(self, device):
        """
        :param device:
        :return:
        """

        tVals = device.readReg(0x02, 3)  # Read data content, return rate, communication rate
        if (len(tVals) > 0):
            print("Return results：" + str(tVals))
        else:
            print("No return")
        tVals = device.readReg(0x23, 2)  # Read the installation direction and algorithm
        if (len(tVals) > 0):
            print("Return results：" + str(tVals))
        else:
            print("No return")

    def onUpdate(self, deviceModel):
        for key in keys:
            self.data[key] = deviceModel.getDeviceData(key)

        """
        w = data["q1"]
        x = data["q2"]
        y = data["q3"]
        z = data["q4"]
    
        import math
        yaw = math.atan2((w*z+y*x), 1 - 2*(y**2+z**2))
        yaw_deg = math.degrees(yaw)
        """


if __name__ == "__main__":
    w = Wit()

    while True:

        lat = w.data["lat"]
        lon = w.data["lon"]
        yaw = w.data["Yaw"]
        velo = w.data["Speed"]

        print(f"Lat: {lat}, Lon: {lon}")
        print(f"Yaw: {yaw}")
        print(f"Speed: {velo}")
        print("")

