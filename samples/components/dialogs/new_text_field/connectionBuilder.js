(function connectionbuilder(attr2)
{
    var params = {};

    params["SERVER"] = attr2[connectionHelper.attributeServer];
    params["PORT"] = attr2[connectionHelper.attributePort];
    params["DATABASE"] = attr2[connectionHelper.attributeDatabase];
    params["UID"] = attr2[connectionHelper.attributeUsername];
    params["PWD"] = attr2[connectionHelper.attributePassword];
    params["BOOLSASCHAR"] = "0";
    params["LFCONVERSION"] = "0";
    params["UseDeclareFetch"] = "1";
    params["Fetch"] = "2526";

    //Pull out the attributes from the connection dialog.
    //You can preserve these attributes by adding service and vendor attributes to the required attribute list.
    params["SERVICE_TEST"] = attr2[connectionHelper.attributeService];
    params["VENDOR1_TEST"] = attr2[connectionHelper.attributeVendor1];
    params["VENDOR2_TEST"] = attr2[connectionHelper.attributeVendor2];
    params["VENDOR3_TEST"] = attr2[connectionHelper.attributeVendor3];

    var formattedParams = [];

    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr2)));

    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})
