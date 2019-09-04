(function dsbuilder(attr) {
    var urlBuilder = "jdbc:postgresql://" + attr[connectionHelper.attributeServer] + ":" + attr[connectionHelper.attributePort] + "/" + attr[connectionHelper.attributeDatabase] + "?";

    var params = [];
    params["user"] = attr[connectionHelper.attributeUsername];
    params["password"] = attr[connectionHelper.attributePassword];

    var formattedParams = [];

    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    urlBuilder += formattedParams.join("&")

    return [urlBuilder];
})
