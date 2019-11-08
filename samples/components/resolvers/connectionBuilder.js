(function dsbuilder(attr)
{
    var params = {};
    //Set the server which is an existing attribute.
    params["Host"] = attr[connectionHelper.attributeServer];
    params[connectionHelper.keywordODBCUsername] = attr[connectionHelper.attributeUsername];
    params[connectionHelper.keywordODBCPassword] = attr[connectionHelper.attributePassword];
    //Set hardcoded connection string values.
    params["DATETIMEFORMAT"] = "ABC";

    //Check if an attribute is set.
    if (attr["dbname"] != undefined && attr["dbname"] != "")
        params["DATABASE"] = attr["dbname"];

    //You can write to the Tableau log file (tabprotosrv.txt). This requires Debug level logging to see (-DLogLevel=Debug).
    logging.log("Hi")
    
    //If odbc-connect-string-extras is defined then the key value pairs can be extracted and 
    //inserted in the params Map. 
    //For Example : If we have "odbc-connect-string-extras" set to  "key1=value1"
    //then the below code snippet will insert the key1 , value1 pair in the params map , params["key1"] = "value1"
    //Finally the line ';key1=value1' will be appended to the ConnectString.
    var odbcConnectStringExtrasMap = {};
    const attributeODBCConnectStringExtras = "odbc-connect-string-extras";
    
    if (attributeODBCConnectStringExtras in attr) 
    {
        odbcConnectStringExtrasMap = connectionHelper.ParseODBCConnectString(attr[attributeODBCConnectStringExtras]);
    }
    for (var key in odbcConnectStringExtrasMap)
    {
        params[key] = odbcConnectStringExtrasMap[key];
    }
    
    var formattedParams = [];
    //Format the attributes as 'key=value'. By default some values are escaped or wrapped in curly braces to follow the ODBC standard, but you can also do it here if needed.
    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    //Here we use our chosen driver that was matched using the rules in our TDR file.
    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    //The result will look like (search for ConnectString in tabprotosrv.log):
    //ConnectString: Host=teradata.mydomain.com;UID=test;PWD=********;DATETIMEFORMAT=ABC;DRIVER={Teradata Database ODBC Driver 16.20}"}}
    return formattedParams;
})

