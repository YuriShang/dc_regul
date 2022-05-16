# Modbus RTU клиент для чтения и записи данных в устройство 

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus import payload as pd
import struct


class Client():
    def __init__(self):
        super().__init__()
        
    def runner(self, volt_reg, curr_reg, slaveID):
        """
        Чтение данных с устройства и их возврат в функцию indicators
        """
        try:
            data = self.client.read_holding_registers(address=0,
                                                      count=99,
                                                      unit=slaveID)
            voltage = struct.pack('>HH', data.registers[volt_reg], 
                                         data.registers[volt_reg-1])
            current = struct.pack('>HH', data.registers[curr_reg], 
                                         data.registers[curr_reg-1])
            self.voltage_float = struct.unpack('>f', voltage)
            self.current_float = struct.unpack('>f', current)
            return round(self.voltage_float[0], 3), round(self.current_float[0], 3), 
        except:
            return 'error', 'error'

    def init_client(self, port_='COM10', baudrate_=9600, parity_='N', stopbits_=1):
        """
        Инициализация модбас клиента
        """
        self.client = ModbusClient(
            method = 'rtu',
            port = port_,
            baudrate = int(baudrate_),
            timeout = 0.1,
            parity = parity_,
            stopbits = int(stopbits_),
            bytesize = 8
            )
    
    def connect(self):
        """
        Запуск клиента
        """
        self.client.connect()

    def writer(self, reg, value, slaveID):
        """
        Функция записи данных в устройство
        """
        builder = pd.BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        builder.add_32bit_float(value)
        payload = builder.to_registers()
        payload = builder.build()
        self.client.write_registers(reg, payload, skip_encode=True, unit=slaveID)

