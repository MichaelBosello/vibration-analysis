#!/usr/bin/python

###########################################
#
# Thanks to danjperron https://github.com/danjperron
# https://github.com/danjperron/mpu6050TestInC/blob/master/MPU6050.py
#
# File modified:
# Set up to use only accelerometer at fastest pace
# Add comments about registers
# Removed unused stuff
# Refactor according to python conventions
#
# Register map: https://www.invensense.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
#
###########################################


import smbus
import struct
import math


bus = smbus.SMBus(1)


class MPU6050Data:

  def __init__(self):
    self.gx = 0
    self.gy = 0
    self.gz = 0
  def __str__(self):
    return 'x:' + str(self.gx) + ' y:' + str(self.gy) + ' z:' + str(self.gz)


class MPU6050:
  ACCEL_BYTES = 6

  MPU6050_ADDRESS = 0x68  # default I2C Address

  # register definition
  # [7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
  MPU6050_RA_XG_OFFS_TC = 0x00
  # [7] PWR_MODE, [6:1] YG_OFFS_TC, [0] OTP_BNK_VLD
  MPU6050_RA_YG_OFFS_TC = 0x01
  # [7] PWR_MODE, [6:1] ZG_OFFS_TC, [0] OTP_BNK_VLD
  MPU6050_RA_ZG_OFFS_TC = 0x02
  MPU6050_RA_X_FINE_GAIN = 0x03  # [7:0] X_FINE_GAIN
  MPU6050_RA_Y_FINE_GAIN = 0x04  # [7:0] Y_FINE_GAIN
  MPU6050_RA_Z_FINE_GAIN = 0x05  # [7:0] Z_FINE_GAIN
  MPU6050_RA_XA_OFFS_H = 0x06  # [15:0] XA_OFFS
  MPU6050_RA_XA_OFFS_L_TC = 0x07
  MPU6050_RA_YA_OFFS_H = 0x08  # [15:0] YA_OFFS
  MPU6050_RA_YA_OFFS_L_TC = 0x09
  MPU6050_RA_ZA_OFFS_H = 0x0A  # [15:0] ZA_OFFS
  MPU6050_RA_ZA_OFFS_L_TC = 0x0B
  MPU6050_RA_XG_OFFS_USRH = 0x13  # [15:0] XG_OFFS_USR
  MPU6050_RA_XG_OFFS_USRL = 0x14
  MPU6050_RA_YG_OFFS_USRH = 0x15  # [15:0] YG_OFFS_USR
  MPU6050_RA_YG_OFFS_USRL = 0x16
  MPU6050_RA_ZG_OFFS_USRH = 0x17  # [15:0] ZG_OFFS_USR
  MPU6050_RA_ZG_OFFS_USRL = 0x18
  MPU6050_RA_SMPLRT_DIV = 0x19
  MPU6050_RA_CONFIG = 0x1A
  MPU6050_RA_GYRO_CONFIG = 0x1B
  MPU6050_RA_ACCEL_CONFIG = 0x1C
  MPU6050_RA_FF_THR = 0x1D
  MPU6050_RA_FF_DUR = 0x1E
  MPU6050_RA_MOT_THR = 0x1F
  MPU6050_RA_MOT_DUR = 0x20
  MPU6050_RA_ZRMOT_THR = 0x21
  MPU6050_RA_ZRMOT_DUR = 0x22
  MPU6050_RA_FIFO_EN = 0x23
  MPU6050_RA_I2C_MST_CTRL = 0x24
  MPU6050_RA_I2C_SLV0_ADDR = 0x25
  MPU6050_RA_I2C_SLV0_REG = 0x26
  MPU6050_RA_I2C_SLV0_CTRL = 0x27
  MPU6050_RA_I2C_SLV1_ADDR = 0x28
  MPU6050_RA_I2C_SLV1_REG = 0x29
  MPU6050_RA_I2C_SLV1_CTRL = 0x2A
  MPU6050_RA_I2C_SLV2_ADDR = 0x2B
  MPU6050_RA_I2C_SLV2_REG = 0x2C
  MPU6050_RA_I2C_SLV2_CTRL = 0x2D
  MPU6050_RA_I2C_SLV3_ADDR = 0x2E
  MPU6050_RA_I2C_SLV3_REG = 0x2F
  MPU6050_RA_I2C_SLV3_CTRL = 0x30
  MPU6050_RA_I2C_SLV4_ADDR = 0x31
  MPU6050_RA_I2C_SLV4_REG = 0x32
  MPU6050_RA_I2C_SLV4_DO = 0x33
  MPU6050_RA_I2C_SLV4_CTRL = 0x34
  MPU6050_RA_I2C_SLV4_DI = 0x35
  MPU6050_RA_I2C_MST_STATUS = 0x36
  MPU6050_RA_INT_PIN_CFG = 0x37
  MPU6050_RA_INT_ENABLE = 0x38
  MPU6050_RA_DMP_INT_STATUS = 0x39
  MPU6050_RA_INT_STATUS = 0x3A
  MPU6050_RA_ACCEL_XOUT_H = 0x3B
  MPU6050_RA_ACCEL_XOUT_L = 0x3C
  MPU6050_RA_ACCEL_YOUT_H = 0x3D
  MPU6050_RA_ACCEL_YOUT_L = 0x3E
  MPU6050_RA_ACCEL_ZOUT_H = 0x3F
  MPU6050_RA_ACCEL_ZOUT_L = 0x40
  MPU6050_RA_TEMP_OUT_H = 0x41
  MPU6050_RA_TEMP_OUT_L = 0x42
  MPU6050_RA_GYRO_XOUT_H = 0x43
  MPU6050_RA_GYRO_XOUT_L = 0x44
  MPU6050_RA_GYRO_YOUT_H = 0x45
  MPU6050_RA_GYRO_YOUT_L = 0x46
  MPU6050_RA_GYRO_ZOUT_H = 0x47
  MPU6050_RA_GYRO_ZOUT_L = 0x48
  MPU6050_RA_EXT_SENS_DATA_00 = 0x49
  MPU6050_RA_EXT_SENS_DATA_01 = 0x4A
  MPU6050_RA_EXT_SENS_DATA_02 = 0x4B
  MPU6050_RA_EXT_SENS_DATA_03 = 0x4C
  MPU6050_RA_EXT_SENS_DATA_04 = 0x4D
  MPU6050_RA_EXT_SENS_DATA_05 = 0x4E
  MPU6050_RA_EXT_SENS_DATA_06 = 0x4F
  MPU6050_RA_EXT_SENS_DATA_07 = 0x50
  MPU6050_RA_EXT_SENS_DATA_08 = 0x51
  MPU6050_RA_EXT_SENS_DATA_09 = 0x52
  MPU6050_RA_EXT_SENS_DATA_10 = 0x53
  MPU6050_RA_EXT_SENS_DATA_11 = 0x54
  MPU6050_RA_EXT_SENS_DATA_12 = 0x55
  MPU6050_RA_EXT_SENS_DATA_13 = 0x56
  MPU6050_RA_EXT_SENS_DATA_14 = 0x57
  MPU6050_RA_EXT_SENS_DATA_15 = 0x58
  MPU6050_RA_EXT_SENS_DATA_16 = 0x59
  MPU6050_RA_EXT_SENS_DATA_17 = 0x5A
  MPU6050_RA_EXT_SENS_DATA_18 = 0x5B
  MPU6050_RA_EXT_SENS_DATA_19 = 0x5C
  MPU6050_RA_EXT_SENS_DATA_20 = 0x5D
  MPU6050_RA_EXT_SENS_DATA_21 = 0x5E
  MPU6050_RA_EXT_SENS_DATA_22 = 0x5F
  MPU6050_RA_EXT_SENS_DATA_23 = 0x60
  MPU6050_RA_MOT_DETECT_STATUS = 0x61
  MPU6050_RA_I2C_SLV0_DO = 0x63
  MPU6050_RA_I2C_SLV1_DO = 0x64
  MPU6050_RA_I2C_SLV2_DO = 0x65
  MPU6050_RA_I2C_SLV3_DO = 0x66
  MPU6050_RA_I2C_MST_DELAY_CTRL = 0x67
  MPU6050_RA_SIGNAL_PATH_RESET = 0x68
  MPU6050_RA_MOT_DETECT_CTRL = 0x69
  MPU6050_RA_USER_CTRL = 0x6A
  MPU6050_RA_PWR_MGMT_1 = 0x6B
  MPU6050_RA_PWR_MGMT_2 = 0x6C
  MPU6050_RA_BANK_SEL = 0x6D
  MPU6050_RA_MEM_START_ADDR = 0x6E
  MPU6050_RA_MEM_R_W = 0x6F
  MPU6050_RA_DMP_CFG_1 = 0x70
  MPU6050_RA_DMP_CFG_2 = 0x71
  MPU6050_RA_FIFO_COUNTH = 0x72
  MPU6050_RA_FIFO_COUNTL = 0x73
  MPU6050_RA_FIFO_R_W = 0x74
  MPU6050_RA_WHO_AM_I = 0x75

  def __init__(self):
    self.setup()
    self.fifo_count = 0

  def setup(self):
    # Reset all registers
    # DEVICE_RESET bit7 (When set to 1, this bit resets all internal registers to their default values.)
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_PWR_MGMT_1, 0x80)

    self.set_sample_rate(1000)
    self.set_g_resolution(2)

    # Upon power up, the MPU-60X0 clock source defaults to the internal oscillator. However, it is highly
    # recommended that the device be configured to use one of the gyroscopes (or an external clock
    # source) as the clock reference for improved stability.
    #
    # sets clock source to gyro reference PLL (Phase-locked loop)
    # CLKSEL bit[2:0] ~ CLKSEL=1 => PLL with X axis gyroscope reference
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_PWR_MGMT_1, 0b00000010)

    # This register enables interrupt generation by interrupt sources.
    # FIFO_OFLOW_EN bit4 (When set to 1, this bit enables a FIFO buffer overflow to generate an interrupt.)
    # DATA_RDY_EN bit0 (When set to 1, this bit enables the Data Ready interrupt.)
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_INT_ENABLE, 0b00010001)

  def read_data_from_fifo(self):
    if self.fifo_count == 0:
      self.fifo_count = self.read_fifo_count()
    # max block transfer in i2c is 32 bytes including the address
    # accelerometer data => 3 short = 6 bytes  => 31 / 6 = 5
    # then it will be 30
    if (self.fifo_count > 30):
      n_count = 30
    else:
      n_count = self.fifo_count
    g_data = bus.read_i2c_block_data(self.MPU6050_ADDRESS, self.MPU6050_RA_FIFO_R_W, n_count)
    self.fifo_count = self.fifo_count - n_count
    return g_data

  def read_fifo_count(self):
    g_data = bus.read_i2c_block_data(self.MPU6050_ADDRESS, self.MPU6050_RA_FIFO_COUNTH)
    # g_data[0] high register, g_data[1] low register
    self.fifo_count = (g_data[0] * 256 + g_data[1])
    return self.fifo_count

  def read_status(self):
    # FIFO_OFLOW_INT bit3 (This bit automatically sets to 1 when a FIFO buffer overflow interrupt has been generated.)
    # DATA_RDY_INT bit0 (This bit automatically sets to 1 when a Data Ready interrupt is generated.)
    # The bit clears to 0 after the register has been read.
    return bus.read_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_INT_STATUS)

  def convertData(self, list_data):
    # '>' = big-endian, 'h' = short
    short_data = struct.unpack(">hhh", memoryview(bytearray(list_data)))
    acc_data = MPU6050Data()

    acc_data.Gx = short_data[0] * self.acceleration_factor
    acc_data.Gy = short_data[1] * self.acceleration_factor
    acc_data.Gz = short_data[2] * self.acceleration_factor

    return acc_data

  def set_g_resolution(self, value):
    # use dictionary to get correct G resolution 2,4,8 or 16G
    # AFS_SEL[bit4, bit3]: 0 = 2g, 1 = 4g, 2 = 8g, 3 = 16g
    # 8d=01000b 16d=10000b 24d=11000b
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_ACCEL_CONFIG, { 2: 0, 4: 8, 8: 16, 16: 24}[value])
    self.acceleration_factor = value/32768.0

  def set_sample_rate(self, rate):
    # The sensor register output and FIFO output sampling are all based on the Sample Rate.
    # The Sample Rate is generated by dividing the gyroscope output rate by SMPLRT_DIV:
    #
    #    Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
    #
    # where Gyroscope Output Rate = 8kHz when the DLPF is disabled (DLPF_CFG = 0 or 7), and 1kHz
    # when the DLPF is enabled (see Register 26).
    sample_reg = int((8000 / rate) - 1)
    self.sample_rate = 8000.0 / (sample_reg + 1.0)
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_SMPLRT_DIV, sample_reg)

  def enable_fifo(self, flag=True):
    if flag:
      self.reset_fifo()
      # We want only the accel data. ACCEL_FIFO_EN = bit3
      # ACCEL_FIFO_EN When set to 1, this bit enables ACCEL_XOUT_H, ACCEL_XOUT_L,
      # ACCEL_YOUT_H, ACCEL_YOUT_L, ACCEL_ZOUT_H, and ACCEL_ZOUT_L to be written into the FIFO buffer.
      bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_FIFO_EN, 0b00001000)
    else:
      # shut off the feed in the FIFO.
      bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_FIFO_EN, 0)

  def reset_fifo(self):
    # shut off the feed in the FIFO.
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_USER_CTRL, 0b00000000)
    pass
    # bit 2 FIFO_RESET (This bit resets the FIFO buffer when set to 1 while FIFO_EN equals 0.
    # This bit automatically clears to 0 after the reset has been triggered.
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_USER_CTRL, 0b00000100)
    pass
    # bit 6 = FIFO_EN (When set to 1, this bit enables FIFO operations)
    bus.write_byte_data(self.MPU6050_ADDRESS, self.MPU6050_RA_USER_CTRL, 0b01000000)