''' Project Recycle '''


# Setting up camera
import os
from picamera import PiCamera
camera = PiCamera()


# Setting up a timer
from time import sleep

# Set up datetime to identify images
from datetime import datetime

# Setting up SenseHat
from sense_hat import SenseHat
sense = SenseHat()
# sense.set_imu_config(#compass, #gyroscope, #accelerometer)

# Setting up IoT:
# Source from: Azure-Samples/azure-iot-samples-python
import random
import sys
import json
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

iot_hub_connection_string = "HostName=projectrecycle.azure-devices.net;DeviceId=projectrecycleiotdeviceID;SharedAccessKey=O2cWv72KSoPsMtJ+hekrDgSUqt1gkfcBTW4Y/ZdG6cY="
mqtt_protocol = IoTHubTransportProvider.MQTT
iot_message_timeout = 10000


# Setting up connection to Azure Blob Storage
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService


# Setting up Custom Vision model connection:
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient


# Streaming data to IoT Hub:
def message_to_iothub():
    temperature = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()
    orientation = sense.get_orientation_degrees()
    compass = sense.get_compass()
    gyroscope = sense.get_gyroscope()
    accelerometer = sense.get_accelerometer()
    message = { "temperature": temperature, "humidity": humidity, "pressure": pressure, "orientation": orientation, "compass": compass, "gyroscope": gyroscope, "accelerometer": accelerometer }
    json_message = json.dumps(message)
    return json_message


def send_confirmation_callback(message, result, user_context):
    print("IoT Hub responded to message with status: %s" % (result))

def iothub_client_init():
    # Create an IoT Hub Client
    client = IoTHubClient(iot_hub_connection_string, mqtt_protocol)
    return client
      
def iothub_client_telemetry_run():
    
    try:
        client = iothub_client_init()
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit.")
        while True:
            message = IoTHubMessage(message_to_iothub())
            
            # can detect checks and send alerts here

            print("Sending message: %s" % message.get_string())
            client.send_event_async(message, send_confirmation_callback, None)
            sleep(1)
            
    except IoTHubError as iothub_error:
        print("Unexpected error %s from IoTHub" % iothub_error)
        return
    
    except KeyboardInterrupt:
        print("IoTHubClient stopped")
        
            

# Output to device:
def trash():
    red = (255, 0, 0)
    for i in range(0, 8):
        for j in range(0, 8):
            sense.set_pixel(i, j, red)
    sleep(5)
    sense.clear((0, 0, 0))

def recycle():
    yellow = (255, 255, 0)
    for i in range(0, 8):
        for j in range(0, 8):
            sense.set_pixel(i, j, yellow)
    sleep(5)
    sense.clear((0, 0, 0))

def organic():
    green = (0, 128, 0)
    for i in range(0, 8):
        for j in range(0, 8):
            sense.set_pixel(i, j, green)
    sleep(5)
    sense.clear((0, 0, 0))
    
def trash_word():
    word = "GENERAL WASTE"
    for char in word:
        sense.show_letter(char, text_colour=[0, 0, 0], back_colour=[255, 0, 0])
        sleep(1)
    trash()

def recycle_word():
    word = "RECYCLE PLEASE"
    for char in word:
        sense.show_letter(char, text_colour=[0, 0, 0], back_colour=[255, 255, 0])
        sleep(1)
    recycle()

def organic_word():
    word = "ORGANIC WASTE"
    for char in word:
        sense.show_letter(char, text_colour=[0, 0, 0], back_colour=[0, 128, 0])
        sleep(1)
    organic()


# Blob storage connection:
def blob(file_path, blob_name):
    block_blob_service = BlockBlobService(account_name='{insert-account-name-here}', account_key='{insert-account-key-here}')
    container_name = 'iotimage'
    block_blob_service.create_blob_from_path(container_name, blob_name, file_path, content_settings=ContentSettings(content_type='image/jpeg'))


def custom_vision(image_name):
    # Establishing key connections: 
    training_key = "{insert-training-key-here}"
    prediction_key = "{insert-prediction-key-here}"    
    storage_account_url = "{insert-storage-account-here}"
    ENDPOINT = "{insert-endpoint-here}"
    
    pid = "{insert-pid-here}"
    
    # For future re-training model purposes: 
    # trainer = CustomVisionTrainingClient(training_key, endpoint=training_endpoint)

    predictor = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)

    image_url = storage_account_url + image_name
    print("Image url: " + image_url + "\n")
    
    # Using the default iteration otherwise you can set iteration_id to something else
    results = predictor.predict_image_url(project_id=pid, url=image_url)
    
    return results

            
def output_results(bin_category):
    print(bin_category)
    if bin_category == "general waste":
        trash_word()
    elif bin_category == "recycle":
        recycle_word()
    elif bin_category == "organic waste":
        organic_word()
    else:
        print("ALERT: This human is making me very confused.\n")
        

def display(results):
    acceptance_rate = 0.8
    
    # Display the results:
    for prediction in results.predictions:
        print(prediction.tag_name + ":{0:.2f} %".format(prediction.probability*100))
        if prediction.probability >= float(acceptance_rate):
            bin_category = str(prediction.tag_name)
            output_results(bin_category)
    
    

def start():
    try:
        print("Starting up camera\n")
        camera.start_preview()
        current_datetime = datetime.now()
        image_name = 'image-' + current_datetime.strftime("%d%m%Y-%H%M%S") +'.jpg'
        full_path = '/home/pi/Desktop/' + image_name
        camera.capture(full_path)
        camera.stop_preview()
        blob(full_path, image_name)
        print("Success: " + image_name + " has been successfully uploaded to Azure Blob Storage\n")
        print("Sending to custom vision model\n")
        model = custom_vision(image_name)
        display(model)
        os.remove(full_path)
    except Exception as e:
        print("There has been an error. Please see below for full details.\n")
        print(e)


start()



    
    
    
