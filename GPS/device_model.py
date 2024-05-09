import threading
import time
import serial
from serial import SerialException
from GPS.protocol_resolver import ProtocolResolver


class DataProcessor:
    onVarChanged = []
    def onOpen(self, deviceModel):
        pass

    def onClose(self):
        pass

    @staticmethod
    def onUpdate(*args):
        for fun in DataProcessor.onVarChanged:
            fun(*args)


class SerialConfig:
    portName = ''
    baud = 9600

class DeviceModel:

    deviceName = "Device"           # Device Name
    ADDR = 0x50                     # Device ID
    deviceData = {}                 # Device Data
    isOpen = False                  # Is Device Port Opened?
    serialPort = None               # Serial Port Object
    serialConfig = SerialConfig()   # Serial Config Class
    dataUpdateListener = ""         # Listening Function
    dataProcessor = DataProcessor()
    protocolResolver = ProtocolResolver()

    def setDeviceData(self, key, value):
        self.deviceData[key] = value

    def getDeviceData(self, key):
        if key in self.deviceData:
            return self.deviceData[key]
        else:
            return None

    def removeDeviceData(self, key):
        if key in self.deviceData:
            del self.deviceData[key]

    def readDataThread(self, threadName,):
        while True:
            if self.isOpen:
                try:
                    tlen = self.serialPort.inWaiting()
                    if tlen > 0:
                        data = self.serialPort.read(tlen)
                        self.onDataRecieved(data)
                except Exception as e:
                    print(e)
            else:
                time.sleep(0.1)
                break

    def openDevice(self):
        try:
            self.serialPort = serial.Serial(self.serialConfig.portName, self.serialConfig.baud, timeout=0.5)
            self.isOpen = True
            t = threading.Thread(target=self.readDataThread, args=("Data-Received-Thread",))
            t.start()
        except SerialException:
            print("Failed to open Serial.")

    def closeDevice(self):
        if self.serialPort is not None:
            self.serialPort.close()
        self.isOpen = False

    def onDataRecieved(self, data):
        if self.protocolResolver is not None:
            self.protocolResolver.passiveReceiveData(data, self)

    def get_int(self,dataBytes):
        #return -(data & 0x8000) | (data & 0x7fff)
        return  int.from_bytes(dataBytes, "little", signed=True)

    def get_unint(self,dataBytes):
        return  int.from_bytes(dataBytes, "little")


    def sendData(self, data):
        if self.protocolResolver is not None:
            self.protocolResolver.sendData(data, self)

    def readReg(self, regAddr,regCount):
        if self.protocolResolver is not None:
            return self.protocolResolver.readReg(regAddr,regCount, self)
        else:
            return None

    def writeReg(self, regAddr,sValue):
        if self.protocolResolver is not None:
            self.protocolResolver.writeReg(regAddr,sValue, self)

    def unlock(self):
        if self.protocolResolver is not None:
            self.protocolResolver.unlock(self)

    def save(self):
        if self.protocolResolver is not None:
            self.protocolResolver.save(self)

    def accelerationCalibration(self):
        if self.protocolResolver is not None:
            self.protocolResolver.accelerationCalibration(self)

    def beginFieldCalibration(self):
        if self.protocolResolver is not None:
            self.protocolResolver.beginFieldCalibration(self)

    def endFieldCalibration(self):
        if self.protocolResolver is not None:
            self.protocolResolver.endFieldCalibration(self)

    def sendProtocolData(self, data):
        if self.protocolResolver is not None:
            self.protocolResolver.sendData(data, self)