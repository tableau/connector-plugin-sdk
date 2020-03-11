(function propertiesbuilder(attr) {
    var props = {};
    props["user"] = attr[connectionHelper.attributeUsername];
    props["password"] = attr[connectionHelper.attributePassword];
    props["logLevel"] = attr[connectionHelper.attributeVendor1];
    props["protocolVersion"] = attr[connectionHelper.attributeVendor2];
    props["charSet"] = attr[connectionHelper.attributeVendor3];

    if (attr[connectionHelper.attributeSSLMode] == "require") {
        props["ssl"] = "true";
        props["sslmode"] = "require";
    }

    return props;
})
