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

        sudo raspi-config

    >Interfacing Options

    >I2C

2. Verify I2C connection

        sudo i2cdetect -y 1

    If the gyroscope is properly connected, you will see it at address 68 (default)

3. set I2C Bus Speed

        sudo nano /boot/config.txt

    Find the line containing “dtparam=i2c_arm=on” and change to:

    > dtparam=i2c_arm=on,i2c_arm_baudrate=400000

## AWS IoT Setup

Go to the AWS console, click *IoT Core*

1. Create a new Thing named 'VibrationAnalyzer'
    
    During the setup, allow the following topics in the device policy:
    
    things/VibrationAnalyzer/shadow/

    topic/vibration_analysis

2. Download its certificates and put them in the dir *./cert*

3. Change the endpoint in _start.sh_ to your AWS endpoint (the parameter *-e*)

4. [optional] Create a rule to store analysis to a dynamoDB table

    In AWS Iot -> **Act** -> **Create new rule** ->

    > *Rule query statement*: SELECT * FROM 'vibration_analysis'

    **Add action** -> Select **Insert a message into a DynamoDB table** -> select or create a new DynamoDB table ->
    
    >**Partition key value**: ${id}
    
    >**Sort key value**: ${id}

    Put a role, fill other params as you see fit -> **Add action** -> **Create rule**

## Run

To run the complete application with the AWS part:

1. Make script executable:

        chmod 777 start.sh

2. Run the script:

        sudo ./start.sh

To run a local test that displays the average g and the fft plot:

        sudo python3 src/accelerometer_ftt.py