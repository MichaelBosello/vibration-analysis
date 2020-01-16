import MPU6050
import time

class accelerometer_ftt:
  TARGET_SAMPLE_NUM = 2048

  def __init__(self):
    self.mpu6050 = MPU6050.MPU6050()
    time.sleep(0.01)

  def get_samples(self):
    values = []
    total = 0
    ACCEL_BYTES = self.mpu6050.ACCEL_BYTES

    self.mpu6050.enable_fifo(True)
    time.sleep(0.01)

    while total < accelerometer_ftt.TARGET_SAMPLE_NUM:
      if self.mpu6050.fifo_count == 0:
        status = self.mpu6050.read_status()
        # check overflow flag
        if (status & 0x10) == 0x10 :
          print("Overflow Error! Quitting.\n")
          #quit()
        # check data ready flag
        if (status & 0x01) == 0x01:
          values.extend(self.mpu6050.read_data_from_fifo())
      else:
        values.extend(self.mpu6050.read_data_from_fifo())
      total = len(values)/ACCEL_BYTES

    fftdata = []
    for i in range (self.TARGET_SAMPLE_NUM):
      sample = values[i*ACCEL_BYTES : i*ACCEL_BYTES+ACCEL_BYTES]
      converted_sample = self.mpu6050.convertData(sample)
      fftdata.append(converted_sample)

    self.mpu6050.enable_fifo(False)
    return fftdata

    def fft(self, data):
      pass

if __name__ == "__main__":
  fft = accelerometer_ftt()
  samples = fft.get_samples()
  print(len(samples))
  for i in range(0, 100):
    print(str(samples[i]))