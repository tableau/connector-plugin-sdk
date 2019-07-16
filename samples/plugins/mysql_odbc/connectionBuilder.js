(function dsbuilder(attr)
{
    var params = {};

    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["PORT"] = attr["port"];
    params["UID"] = attr[connectionHelper.attributeUsername];
    params["PWD"] = attr[connectionHelper.attributePassword];
    params["DATABASE"] = attr[connectionHelper.attributeDatabase];
    params["INITSTMT"] = attr[connectionHelper.attributeInitialSQL];

    if (attr["sslmode"] == "require" && attr["sslfile"] != undefined && attr["sslfile"] != "")
    {
        params["SSLCA"] = attr["sslfile"];
        params["SSLMODE"] = "required";
    }

    params["OPTION"] = "1048576"

    if (parseFloat(driverLocator.LocateDriverVersion(attr)) >= 8.0)
    {
        params["default_auth"] = "mysql_native_password";
    }


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
