import time


class ProtocolResolver:
    TempBytes = []
    PackSize = 11
    gyroRange = 2000.0
    accRange = 16.0
    angleRange = 180.0
    TempFindValues = []

    def sendData(self, sendData, deviceModel):
        deviceModel.serialPort.write(sendData)

    def passiveReceiveData(self, data, deviceModel):
        global TempBytes

        for val in data:
            self.TempBytes.append(val)

            if self.TempBytes[0] != 0x55:
                del self.TempBytes[0]
                continue

            if len(self.TempBytes) > 1:
                if ((0 <= self.TempBytes[1] - 0x50 <= 11) or self.TempBytes[1] == 0x5f) is False:
                    del self.TempBytes[0]
                    continue

            if len(self.TempBytes) == self.PackSize:
                check_sum = 0
                for i in range(0, self.PackSize - 1):
                    check_sum += self.TempBytes[i]

                if check_sum & 0xff == self.TempBytes[self.PackSize - 1]:
                    if self.TempBytes[1] == 0x50:
                        self.get_chiptime(self.TempBytes, deviceModel)
                    elif self.TempBytes[1] == 0x51:
                        self.get_acc(self.TempBytes, deviceModel)
                    elif self.TempBytes[1] == 0x52:
                        self.get_gyro(self.TempBytes, deviceModel)
                    elif self.TempBytes[1] == 0x53:
                        self.get_angle(self.TempBytes, deviceModel)
                    elif self.TempBytes[1] == 0x54:
                        self.get_mag(self.TempBytes, deviceModel)
                        deviceModel.dataProcessor.onUpdate(deviceModel)
                    elif self.TempBytes[1] == 0x57:
                        self.get_lonlat(self.TempBytes, deviceModel)
                        deviceModel.dataProcessor.onUpdate(deviceModel)
                    elif self.TempBytes[1] == 0x58:
                        self.get_gps(self.TempBytes, deviceModel)
                        deviceModel.dataProcessor.onUpdate(deviceModel)
                    elif self.TempBytes[1] == 0x59:
                        self.get_four_elements(self.TempBytes, deviceModel)
                        deviceModel.dataProcessor.onUpdate(deviceModel)
                    elif self.TempBytes[1] == 0x5f:
                        self.get_find(self.TempBytes, deviceModel)
                    self.TempBytes = []
                else:
                    del self.TempBytes[0]

    def get_readbytes(self, regAddr):
        return [0xff, 0xaa, 0x27, regAddr & 0xff, regAddr >> 8]

    def get_writebytes(self, regAddr, sValue):
        return [0xff, 0xaa, regAddr, sValue & 0xff, sValue >> 8]

    def get_acc(self, datahex, deviceModel):
        axl = datahex[2]
        axh = datahex[3]
        ayl = datahex[4]
        ayh = datahex[5]
        azl = datahex[6]
        azh = datahex[7]

        tempVal = (datahex[9] << 8 | datahex[8])
        acc_x = (axh << 8 | axl) / 32768.0 * self.accRange
        acc_y = (ayh << 8 | ayl) / 32768.0 * self.accRange
        acc_z = (azh << 8 | azl) / 32768.0 * self.accRange
        if acc_x >= self.accRange:
            acc_x -= 2 * self.accRange
        if acc_y >= self.accRange:
            acc_y -= 2 * self.accRange
        if acc_z >= self.accRange:
            acc_z -= 2 * self.accRange

        deviceModel.setDeviceData("accX", round(acc_x, 4))
        deviceModel.setDeviceData("accY", round(acc_y, 4))
        deviceModel.setDeviceData("accZ", round(acc_z, 4))
        temperature = round(tempVal / 100.0, 2)
        deviceModel.setDeviceData("temperature", temperature)

    def get_gyro(self, datahex, deviceModel):
        wxl = datahex[2]
        wxh = datahex[3]
        wyl = datahex[4]
        wyh = datahex[5]
        wzl = datahex[6]
        wzh = datahex[7]

        gyro_x = (wxh << 8 | wxl) / 32768.0 * self.gyroRange
        gyro_y = (wyh << 8 | wyl) / 32768.0 * self.gyroRange
        gyro_z = (wzh << 8 | wzl) / 32768.0 * self.gyroRange

        if gyro_x >= self.gyroRange:
            gyro_x -= 2 * self.gyroRange
        if gyro_y >= self.gyroRange:
            gyro_y -= 2 * self.gyroRange
        if gyro_z >= self.gyroRange:
            gyro_z -= 2 * self.gyroRange

        deviceModel.setDeviceData("gyroX", round(gyro_x, 4))
        deviceModel.setDeviceData("gyroY", round(gyro_y, 4))
        deviceModel.setDeviceData("gyroZ", round(gyro_z, 4))

    def get_angle(self, datahex, deviceModel):
        rxl = datahex[2]
        rxh = datahex[3]
        ryl = datahex[4]
        ryh = datahex[5]
        rzl = datahex[6]
        rzh = datahex[7]

        angle_x = (rxh << 8 | rxl) / 32768.0 * self.angleRange
        angle_y = (ryh << 8 | ryl) / 32768.0 * self.angleRange
        angle_z = (rzh << 8 | rzl) / 32768.0 * self.angleRange

        if angle_x >= self.angleRange:
            angle_x -= 2 * self.angleRange
        if angle_y >= self.angleRange:
            angle_y -= 2 * self.angleRange
        if angle_z >= self.angleRange:
            angle_z -= 2 * self.angleRange

        deviceModel.setDeviceData("angleX", round(angle_x, 3))
        deviceModel.setDeviceData("angleY", round(angle_y, 3))
        deviceModel.setDeviceData("angleZ", round(angle_z, 3))

    def get_mag(self, datahex, deviceModel):
        _x = deviceModel.get_int(bytes([datahex[2], datahex[3]]))
        _y = deviceModel.get_int(bytes([datahex[4], datahex[5]]))
        _z = deviceModel.get_int(bytes([datahex[6], datahex[7]]))

        deviceModel.setDeviceData("magX", round(_x, 0))
        deviceModel.setDeviceData("magY", round(_y, 0))
        deviceModel.setDeviceData("magZ", round(_z, 0))

    def get_lonlat(self, datahex, deviceModel):
        lon = deviceModel.get_unint(bytes([datahex[2], datahex[3], datahex[4], datahex[5]]))
        lat = deviceModel.get_unint(bytes([datahex[6], datahex[7], datahex[8], datahex[9]]))
        # (lon / 10000000 + ((double)(lon % 10000000) / 1e5 / 60.0)).ToString("f8")

        tlon = lon / 10000000.0
        tlat = lat / 10000000.0

        deviceModel.setDeviceData("lon", round(tlon, 8))
        deviceModel.setDeviceData("lat", round(tlat, 8))

    def get_gps(self, datahex, deviceModel):
        Height = deviceModel.get_int(bytes([datahex[2], datahex[3]])) / 10.0
        Yaw = deviceModel.get_int(bytes([datahex[4], datahex[5]])) / 100.0
        Speed = deviceModel.get_unint(bytes([datahex[6], datahex[7], datahex[8], datahex[9]])) / 1e3

        deviceModel.setDeviceData("Height", round(Height, 3))
        deviceModel.setDeviceData("Yaw", round(Yaw, 2))
        deviceModel.setDeviceData("Speed", round(Speed, 3))

    def get_four_elements(self, datahex, deviceModel):
        q1 = deviceModel.get_int(bytes([datahex[2], datahex[3]])) / 32768.0
        q2 = deviceModel.get_int(bytes([datahex[4], datahex[5]])) / 32768.0
        q3 = deviceModel.get_int(bytes([datahex[6], datahex[7]])) / 32768.0
        q4 = deviceModel.get_int(bytes([datahex[8], datahex[9]])) / 32768.0

        deviceModel.setDeviceData("q1", round(q1, 5))
        deviceModel.setDeviceData("q2", round(q2, 5))
        deviceModel.setDeviceData("q3", round(q3, 5))
        deviceModel.setDeviceData("q4", round(q4, 5))

    def get_chiptime(self, datahex, deviceModel):
        tempVals = []
        for i in range(0, 4):
            tIndex = 2 + i * 2
            tempVals.append(datahex[tIndex + 1] << 8 | datahex[tIndex])

        _year = 2000 + (tempVals[0] & 0xff)
        _moth = ((tempVals[0] >> 8) & 0xff)
        _day = (tempVals[1] & 0xff)
        _hour = ((tempVals[1] >> 8) & 0xff)
        _minute = (tempVals[2] & 0xff)
        _second = ((tempVals[2] >> 8) & 0xff)
        _millisecond = tempVals[3]
        deviceModel.setDeviceData("Chiptime",
                                  str(_year) + "-" + str(_moth) + "-" + str(_day) + " " + str(_hour) + ":" + str(
                                      _minute) + ":" + str(_second) + "." + str(_millisecond))

    def readReg(self, regAddr, regCount, deviceModel):
        tempResults = []
        readCount = int(regCount / 4)

        if (regCount % 4 > 0):
            readCount += 1

        for n in range(0, readCount):
            self.TempFindValues = []
            tempBytes = self.get_readbytes(regAddr + n * 4)
            deviceModel.serialPort.write(tempBytes)
            for i in range(0, 20):
                time.sleep(0.05)
                if (len(self.TempFindValues) > 0):
                    for j in range(0, len(self.TempFindValues)):
                        if (len(tempResults) < regCount):
                            tempResults.append(self.TempFindValues[j])
                        else:
                            break
                    break
        return tempResults

    def writeReg(self, regAddr, sValue, deviceModel):
        tempBytes = self.get_writebytes(regAddr, sValue)
        deviceModel.serialPort.write(tempBytes)

    def unlock(self, deviceModel):
        tempBytes = self.get_writebytes(0x69, 0xb588)
        deviceModel.serialPort.write(tempBytes)

    def save(self, deviceModel):
        tempBytes = self.get_writebytes(0x00, 0x00)
        deviceModel.serialPort.write(tempBytes)

    def accelerationCalibration(self, deviceModel):
        self.unlock(deviceModel)
        time.sleep(0.1)
        tempBytes = self.get_writebytes(0x01, 0x01)
        deviceModel.serialPort.write(tempBytes)
        time.sleep(5.5)

    def beginFieldCalibration(self, deviceModel):
        self.unlock(deviceModel)
        time.sleep(0.1)
        tempBytes = self.get_writebytes(0x01, 0x07)
        success_bytes = deviceModel.serialPort.write(tempBytes)

    def endFieldCalibration(self, deviceModel):
        self.unlock(deviceModel)
        time.sleep(0.1)
        self.save(deviceModel)

    def get_find(self, datahex, deviceModel):
        t0l = datahex[2]
        t0h = datahex[3]
        t1l = datahex[4]
        t1h = datahex[5]
        t2l = datahex[6]
        t2h = datahex[7]
        t3l = datahex[8]
        t3h = datahex[9]

        val0 = (t0h << 8 | t0l)
        val1 = (t1h << 8 | t1l)
        val2 = (t2h << 8 | t2l)
        val3 = (t3h << 8 | t3l)
        self.TempFindValues.extend([val0, val1, val2, val3])
