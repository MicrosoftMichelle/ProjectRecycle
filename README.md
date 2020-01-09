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





