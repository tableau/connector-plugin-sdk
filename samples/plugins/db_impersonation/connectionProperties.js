(function propertiesbuilder(attr) {
    
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    var props = {};
    props["UID"] = attr[connectionHelper.attributeUsername];
    props["PWD"] = attr[connectionHelper.attributePassword];
   
    if (attr[connectionHelper.attributeTableauServerAuthMode] == connectionHelper.valueAuthModeDBImpersonate) {
        var str = attr[connectionHelper.attributeTableauServerUser];
        
        if (!isEmpty(str)){
            props["DelegationUID"] = str;
        }
    }

    if (attr["sslmode"] !== "") {
        props["ssl"] = "true";
    }

    return props;
})
