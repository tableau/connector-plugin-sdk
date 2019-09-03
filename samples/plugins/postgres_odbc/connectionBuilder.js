(function dsbuilder(attr)
{
    var params = {};

    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["PORT"] = attr[[connectionHelper.attributePort];
    params["DATABASE"] = attr[connectionHelper.attributeDatabase];
    params["UID"] = attr[connectionHelper.attributeUsername];
    params["PWD"] = attr[[connectionHelper.attributePassword];
    params["BOOLSASCHAR"] = "0";
    params["LFCONVERSION"] = "0";
    params["UseDeclareFetch"] = "1";
    params["Fetch"] = "2048";

    var odbcConnectStringExtrasMap = {};
    if ("odbc-connect-string-extras" in attr) 
    {
        odbcConnectStringExtrasMap = connectionHelper.ParseODBCConnectString(attr["odbc-connect-string-extras"]);
    }
    for (var key in odbcConnectStringExtrasMap)
    {
        params[key] = odbcConnectStringExtrasMap[key];
    }
    
    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
