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


# Python Script -> HTTP Post -> Azure Logic App -> SQL DB:
import requests
import json
import uuid


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
    print(json_message)
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
            
            # print("Sending message: %s" % message.get_string())
            
            client.send_event_async(message, send_confirmation_callback, None)
            sleep(1)
            check(message_to_iothub())
            
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
    block_blob_service = BlockBlobService(account_name='{insert-account-name}', account_key='{insert-account-key}')
    container_name = 'iotimage'
    block_blob_service.create_blob_from_path(container_name, blob_name, file_path, content_settings=ContentSettings(content_type='image/jpeg'))


def custom_vision(image_name):
    # Establishing key connections: 
    training_key = "{insert-training-key}"
    prediction_key = "{insert-prediction-key}"    
    storage_account_url = "{insert-storage-account-url}"
    ENDPOINT = "{insert-endpoint}"
    
    pid = "{insert-pid}"
    
    # For future re-training model purposes: 
    # trainer = CustomVisionTrainingClient(training_key, endpoint=training_endpoint)

    predictor = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)

    image_url = storage_account_url + image_name
    print("Image url: " + image_url + "\n")
    
    # Using the default iteration otherwise you can set iteration_id to something else
    results = predictor.predict_image_url(project_id=pid, url=image_url)
    
    return results

            
def output_results(bin_category):
    if bin_category == "general waste":
        trash()
    elif bin_category == "recycle":
        recycle()
    elif bin_category == "organic waste":
        organic()
    else:
        print("ALERT: This human is making me very confused.\n")
        

def display(results):
    acceptance_rate = 0.8
    classified = False
    post_results = {}
    
    # Display the results:
    for prediction in results.predictions:
        print(prediction.tag_name + ":{0:.2f} %".format(prediction.probability*100))
        
        if str(prediction.tag_name) == "general waste":
            post_results.update({"GeneralWasteProb": prediction.probability})
        if str(prediction.tag_name) == "recycle":
            post_results.update({"RecycleProb": prediction.probability})
        if str(prediction.tag_name) == "organic waste":
            post_results.update({"OrganicProb": prediction.probability})
    
        if prediction.probability >= float(acceptance_rate) and not classified: 
            bin_category = str(prediction.tag_name)
            output_results(bin_category)
            # Update JSON results: 
            post_results.update({"ClassifiedAs":str(prediction.tag_name)})
            classified = True
            print("Prediction Tag Name:", prediction.tag_name)
            
        if prediction.probability < float(acceptance_rate) and not classified:
            post_results.update({"ClassifiedAs":"unclassified"})
            classified = True
            print("Prediction Tag Name:", "unclassified")
            
    return post_results
    

def http_post(payload):
    try:
        # uniqueid = str(uuid.uuid4())
        # payload.update({"PredictionId":uniqueid})
        url = "{insert-logic-app-trigger}"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)      
        print("Success: ", r.status_code, r.reason)
    except Exception as e:
        print("Error in HTTP Post: ", e)
    

def start():
    try:
        # Capturing image from pi camera: 
        print("Starting up camera\n")
        camera.start_preview()
        current_datetime = datetime.now()
        image_name = 'image-' + current_datetime.strftime("%d%m%Y-%H%M%S") +'.jpg'
        full_path = '/home/pi/Desktop/' + image_name
        camera.capture(full_path)
        camera.stop_preview()
        # Storing image to blob storage account: 
        blob(full_path, image_name)
        print("Success: " + image_name + " has been successfully uploaded to Azure Blob Storage\n")
        print("Sending to custom vision model\n")
        # Sending image to custom vision model for analysis: 
        model = custom_vision(image_name)
        # Displaying results to LED screen:
        results = display(model)
        # Posting results to Azure Logic App: 
        storage_account_url = "{insert-storage-account-url}"
        imageurl = storage_account_url + image_name
        results.update({"ImageUrl": imageurl})
        http_post(results)
        # Remove local image file: 
        os.remove(full_path)
    except Exception as e:
        print("There has been an error. Please see below for full details.\n")
        print(e)

# To end the script: 
def end_script():
    return sys.exit()

# To shut down device():
def shutdown_device():
    return os.system("shutdown now -h")

def wait(time):
    if time == 0.25:
        sleep(15)
    if time == 0.5:
        sleep(30)
    if time == 1:
        sleep(60)
    elif time == 2:
        sleep(120)
    elif time == 3:
        sleep(180)
    elif time == 4:
        sleep(240)
    elif time == 5:
        sleep(300)

# To check the sensor data: 
def check(json_message):
    message = json.loads(json_message)
    temperature = message["temperature"]
    orientation = message["orientation"]
    acceleration = message["accelerometer"]
    
    # Limits:
    tempLimit = 35.0

    orientateLowerLimit = 1.0
    orientateUpperLimit = 350.0
    
    accelerateLimit = 15.0
    
    accelerateYawIdeal = 150.0
    accelerateRollIdeal = 355.0
    acceleratePitchIdeal = 355.0

    # Yaw, Roll, Pitch: 
    orientateRoll = orientation["roll"]
    orientatePitch = orientation["pitch"]

    accelerateYaw = acceleration["yaw"]
    accelerateRoll = acceleration["roll"]
    acceleratePitch = acceleration["pitch"]

    # Calculations:
    accelerateYawDiff = abs(accelerateYaw - accelerateYawIdeal)
    accelerateRollDiff = abs(accelerateRoll - accelerateRollIdeal)
    acceleratePitchDiff = abs(acceleratePitch - acceleratePitchIdeal)
    
    
    # End script if conditions are not normal: 
    if temperature > tempLimit:
        client = iothub_client_init()
        lastmessage = IoTHubMessage(message_to_iothub())
        client.send_event_async(lastmessage, send_confirmation_callback, None)
        return end_script()
    elif orientateRoll > orientateLowerLimit and orientateRoll < orientateUpperLimit:
        client = iothub_client_init()
        lastmessage = IoTHubMessage(message_to_iothub())
        client.send_event_async(lastmessage, send_confirmation_callback, None)
        # return end_script()
        wait(2)
    elif orientatePitch > orientateLowerLimit and orientatePitch < orientateUpperLimit:
        client = iothub_client_init()
        lastmessage = IoTHubMessage(message_to_iothub())
        client.send_event_async(lastmessage, send_confirmation_callback, None)
        # return end_script()
        wait(2)
    elif accelerateRollDiff > accelerateLimit or acceleratePitchDiff > accelerateLimit:
        client = iothub_client_init()
        lastmessage = IoTHubMessage(message_to_iothub())
        client.send_event_async(lastmessage, send_confirmation_callback, None)
        # return end_script()
        wait(0.25)

    
# start()
# iothub_client_telemetry_run()


'''
while True:
    joystick = sense.stick.get_events()
    if len(joystick) > 0:
        shutdown_device()
    else:
        iothub_client_telemetry_run()
        # start()
'''
