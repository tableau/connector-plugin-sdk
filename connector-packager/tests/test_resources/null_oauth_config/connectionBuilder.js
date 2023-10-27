(function dsbuilder(attr)
{
    var params = {};
    var authAttrValue = attr[connectionHelper.attributeAuthentication];

    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["UID"] = attr[connectionHelper.attributeUsername];
    if(authAttrValue =="auth-user-pass")
    {
        params["PWD"] = attr[connectionHelper.attributePassword];
    }
    else if(authAttrValue == "oauth")
    {
        params["AUTHENTICATOR"] = "OAUTH";
        params["TOKEN"] = attr["ACCESSTOKEN"];
    }

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
