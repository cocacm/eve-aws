from time import sleep
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT certificate based connection
# MQQT client is an ID so that the MQTT broker can identify the client, using
# any random string will do.
myMQTTClient = AWSIoTMQTTClient("123afhlss456")
# this is the unique thing endpoint with the .503 certificate
myMQTTClient.configureEndpoint("a375a74rjdbru6.iot.us-west-2.amazonaws.com", 8883)
# michael
myMQTTClient.configureCredentials(
    "aws-iot-device-sdk-python/deviceSDK/certs/VeriSign-Class3-Public-Primary-Certification-Authority-G5.pem.txt",
    "aws-iot-device-sdk-python/deviceSDK/certs/24535dbd29-private.pem.key",
    "aws-iot-device-sdk-python/deviceSDK/certs/24535dbd29-certificate.pem.crt")
# above has the path for the CA root cert, private key cert, and device cert
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(180)  # 5 sec

# callback function for AWS sub
def on_subscribe(client, userdata, message):
    print('hello from callback')
    print(message.payload)

# connect and subscribe
myMQTTClient.connect()
myMQTTClient.subscribe('thing02/water', 1, on_subscribe)

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print('exited')
