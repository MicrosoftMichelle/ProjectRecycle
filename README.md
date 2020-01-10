# Project Recycle

Project Recycle was my first technical project when I joined Microsoft in 2019. The inspiration for this project came from the bins located in the Melbourne office. 

In the Melbourne office, the rubbish that we throw away is separated into 3 bins: 
General Waste, Recycle, and Organic Waste. 

Mindful of waste contamination, I would always stop and read the signs carefully before throwing my rubbish away and then came the "Aha!" moment for me. 

What if we could leverage some of our powerful Azure services and build something to help classify our rubbish. 
With that in mind, I began Project Recycle....  


Let's start with the architecture diagram (my very first one I must add): 
![Project Recycle Architecture Diagram](project-recycle-architecture.jpg)

All the components in blue are Azure services. I'll include links to what each of those components are if you want to read up on them: 
1. [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/?view=azure-devops) was used to facilitate the source control, continuous integration and deployment of Project Recycle.
2. [Azure Storage](https://docs.microsoft.com/en-us/azure/storage/) is cloud-based storage used to store all the images captured by the pi camera. 
3. [App Service](https://docs.microsoft.com/en-us/azure/app-service/) is used to host and run the Project Recycle web app. 
4. [Logic App](https://docs.microsoft.com/en-us/azure/logic-apps/) is used to insert data from the raspberry pi and custom vision model into an Azure SQL database. 
5. [Custom Vision Model](https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/) is a machine learning model that is trained on a specific set of rubbish data sets for classification. 
6. [Azure SQL Database](https://docs.microsoft.com/en-us/azure/sql-database/) is a cloud-based relational SQL database used to store data from the raspberry pi in a structured way so that the web app can then query that data later on. 
7. [Azure Function](https://docs.microsoft.com/en-us/azure/azure-functions/) is severless compute used to extract data from the database and act as APIs to the web app. 
8. [Azure IoT Hub](https://docs.microsoft.com/en-us/azure/iot-hub/) is used to connect and communicate with the raspberry pi. 
9. [Azure Stream Analytics](https://docs.microsoft.com/en-us/azure/stream-analytics/) processes lots and lots of data by streaming all the high-speed, high-voulme sensor data from the raspberry pi into the Azure SQL database. 

Non-Azure things included: 
1. [Raspberry Pi](https://www.raspberrypi.org/documentation/) which is essentially a mini computer, an IoT device. 
2. [Raspberry Pi SenseHat](https://www.raspberrypi.org/documentation/hardware/sense-hat/) which includes a bunch of sensors you can just pop onto the Raspberry Pi if you don't have an electrical engineering background to wire things up. 
3. [Raspberry Pi Camera](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera) which is basically a camera you can attach to the Raspberry Pi. 
4. [Twilio](https://www.twilio.com/) is a cloud-based communications platform used to send SMS or calls to alert someone if something with the Raspberry Pi goes wrong. 
5. Mouse, Keyboard, Power source.
6. WiFi

And now, the fun part begins...setting up the Raspberry Pi: 
> Your Raspberry Pi may or may not come with the [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) operating system. If it doesn't, you need to get an SD card, follow that link to install it. 
> If you haven't already, pop the Sensehat on the Raspberry Pi and attach the Pi camera as well. 
> Now connect the physical mouse and keyboard to the Raspberry Pi and plug Raspberry Pi into a power source. 
> Once you're in, find the WiFi symbol and connect the Raspberry Pi to the WiFi. You can keep using the mouse and keyboard to navigate the Pi but I like to install [VNC](https://www.realvnc.com/en/connect/download/viewer/) so I could remote access my Raspberry Pi. 
> Check that your Raspberry Pi has [Python](https://www.python.org/) installed, if not, install it. 




