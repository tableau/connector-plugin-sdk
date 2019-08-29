(function dsbuilder(attr)
{
    var params = {};

    if (attr["server"].toLowerCase() == "(local)")  // TODO localhost, etc. check
    {
        params["SERVER"] = "(local)";
        // local connection, no auth specified
        // port is ignored
    }
    else
    {
        params["SERVER"] = '@' + attr["server"] + ',' + attr["port"]; // NOTE implicit tcp_ip protocol
        params["UID"] = attr["username"];
        params["PWD"] = attr["password"];
    }
    params["DATABASE"] = attr["dbname"];

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
