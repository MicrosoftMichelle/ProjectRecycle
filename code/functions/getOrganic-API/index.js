module.exports = async function (context, req) {

    // Tedious: A JavaScript implementation of the TDS protocol which is used to interact with instances of Microsoft's SQL Server

    // Connecting to SQL Database: 
    var Connection = require('tedious').Connection;
    var Request = require('tedious').Request;
    var TYPES = require('tedious').TYPES;

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
            encrypt: true
        }
    }

    const connection = new Connection(config);

    await connection.on('connect', function(err) {
        if (err){
            console.log(err);
        }
        else {
            console.log("Successfully connected to SQL database.");
            executeStatement();
        }
    });

    function executeStatement(){

        // Query for the database: 
        var query = "SELECT PredictionId AS 'ItemNo', \
        ImageUrl AS 'ImageUrl', \
        OrganicProb AS 'OrganicProb' \
        FROM Predictions \
        WHERE ClassifiedAs = 'organic waste' \
        FOR JSON PATH";

        // Making a Tedious Request: 
        var request = new Request(query, function(err, rowCount, rows) {
            if (err) {
                console.log(err);
            }
        });

        var json;
        request.on('row', function(columns) {
            console.log("Columns.Value:", columns[0].value);
            json = columns[0].value;
            results = JSON.parse(json);
        });

        request.on('doneInProc', function(rowCount, more, rows){
            console.log(rowCount + ' row(s) returned.');
        });

        // Execute the request: 
        connection.execSql(request);

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