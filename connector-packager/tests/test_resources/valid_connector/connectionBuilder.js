(function dsbuilder(attr)
{
    var params = {};

    params["SERVER"] = attr["server"];
    params["PORT"] = attr["port"];
    params["DATABASE"] = attr["dbname"];
    params["UID"] = attr["username"];
    params["PWD"] = attr["password"];
    params["BOOLSASCHAR"] = "0";
    params["LFCONVERSION"] = "0";
    params["UseDeclareFetch"] = "1";
    params["Fetch"] = "2048";

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
