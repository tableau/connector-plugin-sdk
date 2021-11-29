
(function dsbuilder(attr) {
    var server = attr[connectionHelper.attributeServer];
    var port = attr[connectionHelper.attributePort];
    var urlBuilder = "jdbc:oauthconnector:direct=" + server + ":" + port+ ";";
    return [urlBuilder];
})
