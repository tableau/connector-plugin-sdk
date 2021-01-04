(function propertiesbuilder(attr) {
    var props = {};

    var auth = attr[connectionHelper.attributeAuthentication];
    
    if (auth == "auth-none")
    {
        props["user"] = "<sample username>";
        props["password"] = "<sample password>"; // example only, do not hardcode passwords
    }
    else if (auth == "auth-user")
    {
        props["user"] = attr[connectionHelper.attributeUsername];
        props["extra"] = attr["v-username"];
        props["password"] = "<sample password>"; // example only, do not hardcode passwords
    }
    else if (auth == "auth-user-pass")
    {
        props["user"] = attr[connectionHelper.attributeUsername];
        props["extra"] = attr["v-username"];
        props["password"] = attr[connectionHelper.attributePassword];    
    }
    else if (auth == "auth-pass")
    {
        props["user"] = "<sample username>";
        props["extra"] = attr["v-username"];
        props["password"] = attr[connectionHelper.attributePassword];    
    }
    
    return props;
})
