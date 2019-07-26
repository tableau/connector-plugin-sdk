(function dsbuilder(attr)
{
    var params = {};

    params["SERVER"] = '@' + attr["server"] + ',' + attr["port"]; // NOTE implicit tcp_ip protocol
    params["DATABASE"] = attr["dbname"];
    params["UID"] = attr["username"];
    params["PWD"] = attr["password"];

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
