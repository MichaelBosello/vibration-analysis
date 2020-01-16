# VIBRATION DIAGNOSTIC TOOL

## Hardware
+ Raspberry pi
+ MPU 6050 (Six-Axis Gyro + Accelerometer)

Pin connection:

| Raspberry Pi | MPU 6065 |
|--------------|----------|
| Pin 1 (3.3V) | VCC      |
| Pin 3 (SDA)  | SDA      |
| Pin 5 (SCL)  | SCL      |
| Pin 6 (GND)  | GND      |

## Raspberry setup

1. Turn on I2C communication
> `sudo raspi-config`

> Interfacing Options

> I2C

2. Verify I2C connection

`sudo i2cdetect -y 1`

If the gyroscope is properly connected, you will see it at address 68 (default)