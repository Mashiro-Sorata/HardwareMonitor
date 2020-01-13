import ctypes, sys
import clr
import os
import requests


class Hardwares:
    def __init__(self, computer):
        self.computer = computer
        self.__num = 8
        self.hindexs = self.__get_hardware_indexs()
        self.hardwares = tuple(Sensors(self.computer.Hardware[self.hindexs[i]]) if self.hindexs[i] is not None
                               else None for i in range(self.__num))

    def update(self, index):
        if self.hindexs[index] is not None:
            self.computer.Hardware[self.hindexs[index]].Update()

    def __get_hardware_indexs(self):
        ret = [None for _ in range(self.__num)]
        for _type in range(self.__num):
            for i in range(len(self.computer.Hardware)):
                if self.computer.Hardware[i].HardwareType == _type:
                    ret[_type] = i
                    break
        return ret[:]

    def available(self):
        ret = []
        for i in range(self.__num):
            if self.hindexs[i] is not None:
                ret.append(i)
        return tuple(ret[:])

    def __len__(self):
        return self.__num

    def __getitem__(self, index):
        return self.hardwares[index]


class Sensors:
    def __init__(self, hardware):
        self.hardware = hardware
        self.__num = 12
        self.sindexs = self.__get_sensor_indexs()

    def available(self):
        ret = []
        for i in range(self.__num):
            if self.sindexs[i]:
                ret.append(i)
        return tuple(ret[:])

    def __get_sensor_indexs(self):
        ret = tuple([] for _ in range(self.__num))
        for _type in range(self.__num):
            for i in range(len(self.hardware.Sensors)):
                if self.hardware.Sensors[i].get_SensorType() == _type:
                    ret[_type].append(i)
        return ret[:]


    def __len__(self):
        return self.__num

    def  __getitem__(self, index):
        if self.sindexs[index]:
            return tuple(self.hardware.Sensors[each] for each in self.sindexs[index])
        return None
        

class Monitor:
    HardwareType = ["Mainboard",
                    "SuperIO",
                    "CPU",
                    "GpuNvidia",
                    "GpuAti",
                    "TBalancer",
                    "Heatmaster",
                    "HDD"]
    SensorType = ["Voltage",
                  "Clock",
                  "Temperature",
                  "Load",
                  "Fan",
                  "Flow",
                  "Control",
                  "Level",
                  "Factor",
                  "Power",
                  "Data",
                  "SmallData"]
    
    def __init__(self, DLL=""):
        if DLL:
            clr.AddReference(DLL)
        else:
            clr.AddReference(os.getcwd() + r"\OpenHardwareMonitorLib.dll")
        from OpenHardwareMonitor.Hardware import Computer
        self.computer = Computer()
        self.computer.MainboardEnabled = True
        self.computer.CPUEnabled = True
        self.computer.HDDEnabled = True
        self.computer.RAMEnabled = True
        self.computer.GPUEnabled = True
        self.computer.Open(True)
        self.hardwares = Hardwares(self.computer)

    def get(self, hardware_name, _type_name=None):
        if _type_name is None:
            return self[hardware_name]
        try:
            return self[hardware_name][self.__translate(_type_name, 1)]
        except TypeError:
            return None

    def  __getitem__(self, index):
        self.hardwares.update(self.__translate(index))
        return self.hardwares[self.__translate(index)]

    def __translate(self, name, _type=0):
        return self.HardwareType.index(name) if not _type else self.SensorType.index(name)

    def info(self):
        for hardware in self.computer.Hardware:
            print(hardware.Name, self.HardwareType[hardware.HardwareType])
            hardware.Update()
            for sensor in hardware.Sensors:
                print(self.SensorType[sensor.get_SensorType()]+":", sensor.Name, sensor.Value)

def cpu_temper(sensors):
    temper = 0
    for each in sensors[0:-1]:
        if each.Value is not None:
            temper += each.Value
    if temper:
        return round(temper/(len(sensors)-1), 1)

def gpu_temper(sensors):
    if sensors:
        return sensors[0].Value


    

if __name__ == '__main__':
    m = Monitor()
    import time
    while True:
        print("CPU:%s==GPU:%s" % (cpu_temper(m.get("CPU", "Temperature")),
              gpu_temper(m.get("GpuNvidia", "Temperature"))))
        time.sleep(0.5)
    
