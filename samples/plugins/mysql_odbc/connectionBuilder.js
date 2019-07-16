(function dsbuilder(attr)
{
    var params = {};

    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["PORT"] = attr[connectionHelper.attributePort];
    params["UID"] = attr[connectionHelper.attributeUsername];
    params["PWD"] = attr[connectionHelper.attributePassword];
    params["DATABASE"] = attr[connectionHelper.attributeDatabase];
    params["INITSTMT"] = attr[connectionHelper.attributeInitialSQL];

    params["OPTION"] = "1048576"

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    if (attr["odbc-connect-string-extra"] != "")
    {
        formattedParams.push(attr["odbc-connect-string-extras"])
    }

    return formattedParams;
})
