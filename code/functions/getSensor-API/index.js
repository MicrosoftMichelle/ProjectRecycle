module.exports = async function (context, req) {

    // Tedious: A JavaScript implementation of the TDS protocol which is used to interact with instances of Microsoft's SQL Server

    // Connecting to SQL Database: 
    var Connection = require('tedious').Connection;
    var Request = require('tedious').Request;

    const config = {
        authentication: {
            type: "default",
            options: {
                userName: '{SQL DB Username}',
                password: '{SQL DB Password}'
            }
        },
        server: '{SQL server name}',
        options: {
            database: '{Database name}',
            encrypt: true,
            rowCollectionOnDone: true,
            rowCollectionOnRequestCompletion: true
        }
    }

    const connection = new Connection(config);

    await connection.on('connect', function(err) {
        console.log("Successfully connected to SQL database.");
        executeStatement();
    });

    function executeStatement(){

        // Query for the database: 
        var query = "SELECT TOP 10 \
        Temperature AS 'Temperature', \
        OrientationYaw AS 'Orientation.Yaw', \
        OrientationRoll AS 'Orientation.Roll', \
        OrientationPitch AS 'Orientation.Pitch', \
        AccelerometerYaw AS 'Acceleration.Yaw', \
        AccelerometerRoll AS 'Acceleration.Roll', \
        AccelerometerPitch AS 'Acceleration.Pitch', \
        CurrentDateTime AS 'DateTime' \
        FROM SensorData \
        ORDER BY DateTime DESC \
        FOR JSON PATH";

        var jsonObject;
        // Making a Tedious Request: 
        var request = new Request(query, function(err, rowCount, rows) {
            if (err) {
                console.log(err);
            }

            console.log("Rows:", rows[0][0].value);

            jsonString = rows[0][0].value;

            jsonObject = JSON.parse(jsonString);

            results = jsonObject;

            console.log(rowCount + ' row(s) returned.');

        });

        // Execute the request: 
        connection.execSql(request);

        request.on('requestCompleted', function(){
            console.log("Request Completed:", jsonObject);
            results = jsonObject;
        });

    }
    
    console.log("Results:", results);

    context.res = {
        body: results,
        headers: {
            'Content-Type': 'application/json'
        }
    }
    context.done();

};