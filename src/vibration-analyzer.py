#########################
# Base of the file:
# https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/basicPubSub/basicPubSubAsync.py
#########################

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient
import logging
import time
import threading
import argparse
import json
import uuid

from accelerometer_fft import accelerometer_ftt
from MPU6050 import MPU6050Data

###################################
# parameters
###################################

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="VibrationAnalyzer",
                    help="Targeted client id, it needs to be unique") # uniquely identifies MQTT connection
parser.add_argument("-t", "--topic", action="store", dest="topic", default="vibration_analysis", help="Targeted topic")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="VibrationAnalyzer", help="Targeted thing name")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
thingName = args.thingName

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

###################################
# Init AWSIoTMQTTShadowClient
###################################

shadowClient = None
if useWebsocket:
    shadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    shadowClient.configureEndpoint(host, port)
    shadowClient.configureCredentials(rootCAPath)
else:
    shadowClient = AWSIoTMQTTShadowClient(clientId)
    shadowClient.configureEndpoint(host, port)
    shadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
# Configure the auto-reconnect backoff to start with 1 second and use 32 seconds as a maximum back off time.
# Connection over 20 seconds is considered stable and will reset the back off time back to its base.
shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
# Used to configure the time in seconds to wait for a CONNACK or a disconnect to complete. 
shadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
# Used to configure the timeout in seconds for MQTT QoS 1 publish, subscribe and unsubscribe. 
shadowClient.configureMQTTOperationTimeout(5)  # 5 sec

shadowClient.connect()
client = shadowClient.getMQTTConnection()
time.sleep(1)



###################################
# Shadow of device
# Used to remotely set cycle time
###################################

class DeviceAnalyzerShadow:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance
        self.cycle_hour = 0
        self.cycle_minute = 3
        initial_state = { "cycle": {
            "hour": 0,
            "minute": 3
          }
        }
        initialStatePayload = '{"state":{"reported":' + json.dumps(initial_state) + '}}'
        self.deviceShadowInstance.shadowUpdate(initialStatePayload, None, 5)

    def ShadowCallback_Delta(self, payload, responseStatus, token):
        payloadDict = json.loads(payload)
        print("Received shadow update request: " + str(payloadDict))
        hour = payloadDict["state"]["cycle"].get("hour", 0) # 0 if not present
        minute = payloadDict["state"]["cycle"].get("minute", 0)
        if (hour >= 0 and minute >= 0 and (hour > 0 or minute > 0)):
            shadow.cycle_hour = hour
            shadow.cycle_minute = minute
            new_state = { "cycle": {"hour": hour, "minute": minute } }
            deltaPayload = '{"state":{"reported":' + json.dumps(new_state) + '}}'
            self.deviceShadowInstance.shadowUpdate(deltaPayload, None, 5) # payload, callback, timeout to invalidate request
            print("Updated shadow with new cycle (h: " + str(hour) + " min: " + str(minute) + ")")

# Create a deviceShadow with persistent subscription
deviceShadowHandler = shadowClient.createShadowHandlerWithName(thingName, True)
shadow = DeviceAnalyzerShadow(deviceShadowHandler)
# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(shadow.ShadowCallback_Delta)

###################################
# FTT Topic
# Publish ftt analysis every N minutes/hours
###################################

def sendFTT():
    print("getting samples")
    samples = fft.get_samples()
    print("computing fft")
    x_samples = MPU6050Data.vectorize_gx(samples)
    y_samples = MPU6050Data.vectorize_gy(samples)
    z_samples = MPU6050Data.vectorize_gz(samples)
    x_fft = abs(fft.fft(x_samples, True))
    y_fft = abs(fft.fft(y_samples, True))
    z_fft = abs(fft.fft(z_samples, True))

    json_payload = json.dumps({
      "id": str(uuid.uuid4()),
      "fft_x": x_fft.tolist(),
      "fft_y": y_fft.tolist(),
      "fft_z": z_fft.tolist()
    })

    cycle_wait = shadow.cycle_minute * 60 + shadow.cycle_hour * 3600
    print("next fft at " + str(cycle_wait))
    client.publishAsync(topic, json_payload, 1) # QoS 1
    threading.Timer(cycle_wait, sendFTT).start()

fft = accelerometer_ftt()
sendFTT()