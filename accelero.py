import smbus
import numpy
import json

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

try:
    with open("rotm.json") as f:
        rotm = json.load(f)
        print rotm
except Exception as e:
    rotm = None

def get_accelvector():
    v = [read_word_2c(0x3b), read_word_2c(0x3d), read_word_2c(0x3f)]
    try:
        if rotm:
            v = numpy.matmul(v, rotm)
        return v
    except Exception as e:
        return None

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x69       # This is the address value read via the i2cdetect command

bus.write_byte_data(address, power_mgmt_1, 0)