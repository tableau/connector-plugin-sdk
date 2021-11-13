/**
 * Copyright (C) 2017-2019 Dremio Corporation. This file is confidential and private property.
 */
(function dsbuilder(attr) {
    var server = attr[connectionHelper.attributeServer];
    var port = attr[connectionHelper.attributePort];

    var product = attr["v-dremio-product"];
    if (product == "v-cloud") {
        server = "sql.dremio.cloud"; 
        port = "443";
    }

    var urlBuilder = "jdbc:dremio:direct=" + server + ":" + port+ ";";
    return [urlBuilder];
})
