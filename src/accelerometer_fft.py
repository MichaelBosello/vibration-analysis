from MPU6050 import MPU6050, MPU6050Data
import time
import numpy as np
import matplotlib.pyplot as plt

class accelerometer_ftt:
  TARGET_SAMPLE_NUM = 2048

  def __init__(self):
    self.mpu6050 = MPU6050()
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
          quit()
        # check data ready flag
        if (status & 0x01) == 0x01:
          values.extend(self.mpu6050.read_data_from_fifo())
      else:
        values.extend(self.mpu6050.read_data_from_fifo())
      total = len(values)/ACCEL_BYTES

    fftdata = []
    for i in range (self.TARGET_SAMPLE_NUM):
      sample = values[i*ACCEL_BYTES : i*ACCEL_BYTES+ACCEL_BYTES]
      converted_sample = self.mpu6050.convert_data(sample)
      fftdata.append(converted_sample)

    self.mpu6050.enable_fifo(False)
    return fftdata

  def fft(self, sample):
    data = np.fft.rfft(sample)/self.TARGET_SAMPLE_NUM
    freq = np.fft.rfftfreq(self.TARGET_SAMPLE_NUM, d=1./self.mpu6050.sample_rate)
    return data, freq

  def plot_fft(self, data, freq):
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude |ax|')
    plt.grid(True)

    data[0] = 0
    plt.plot(freq, abs(data))
    plt.xlim([-5,505]) # Nyquist frequency = 500 (-5 +5 for visualization purpose)
    plt.show()

if __name__ == "__main__":
  fft = accelerometer_ftt()
  samples = fft.get_samples()
  print(len(samples))
  avg_x = 0.0
  avg_y = 0.0
  avg_z = 0.0
  for i in range(0, len(samples)):
    #print(str(samples[i]))
    avg_x += samples[i].gx
    avg_y += samples[i].gy
    avg_z += samples[i].gz
  avg_x /= len(samples)
  avg_y /= len(samples)
  avg_z /= len(samples)
  print("avg x: " + str(avg_x) + " avg y: " + str(avg_y) + "avg z: " + str(avg_z))

  # plot of fft on gx
  x_samples = MPU6050Data.vectorize_gx(samples)
  fft_data, fft_freq = fft.fft(x_samples)
  fft.plot_fft(fft_data, fft_freq)