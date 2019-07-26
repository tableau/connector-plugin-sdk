(function dsbuilder(attr) {
    var urlBuilder = "jdbc:ingres://" + attr["server"] + ":" + attr["port"] + "/" + attr["dbname"] + ";";

    var params = [];
    params["UID"] = attr["username"];
    params["PWD"] = attr["password"];

    var formattedParams = [];

    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    urlBuilder += formattedParams.join(";")

    return [urlBuilder];
}) 
 
