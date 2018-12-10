(function dsbuilder(attr) {
    var urlBuilder = "jdbc:postgresql://" + attr["server"] + ":" + attr["port"] + "/" + attr["dbname"] + "?";

    var params = [];
    params["user"] = attr["username"];
    params["password"] = attr["password"];

    var formattedParams = [];

    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    urlBuilder += formattedParams.join("&")

    return [urlBuilder];
})
