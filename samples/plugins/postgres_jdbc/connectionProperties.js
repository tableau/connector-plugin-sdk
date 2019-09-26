(function propertiesbuilder(attr) {
    var props = [];
    props["user"] = attr[connectionHelper.attributeUsername];
    props["password"] = attr[connectionHelper.attributePassword];

    var formattedProps = [];

    for (var key in props) {
        formattedProps.push(connectionHelper.formatKeyValuePair(key, props[key]));
    }
    
    return formattedProps;
})
