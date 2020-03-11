(function connectionbuilder(attr2)
{
    var params = {};

    params["SERVER"] = attr2["server"];
    params["PORT"] = attr2["port"];
    params["DATABASE"] = attr2["dbname"];
    params["UID"] = attr2["username"];
    params["PWD"] = attr2["password"];
    params["BOOLSASCHAR"] = "0";
    params["LFCONVERSION"] = "0";
    params["UseDeclareFetch"] = "1";
    params["Fetch"] = "2526";

    //Pull out the attributes from the connection dialog.
    //You can preserve these attributes by adding service and attributeWarehouse to the required attribute list.
    params["WH_TEST"] = attr2[connectionHelper.attributeWarehouse];
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
