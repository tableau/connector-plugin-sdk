(function propertiesbuilder(attr) {
    
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    var props = {};
    props["UID"] = attr[connectionHelper.attributeUsername];
    props["PWD"] = attr[connectionHelper.attributePassword];
    
    var authAttrValue = attr[connectionHelper.attributeAuthentication]; 
    
    switch (authAttrValue) {
       case "auth-none": props["AuthMech"] = "0";
           break;
       case "auth-user": props["AuthMech"] = "2";
           break;
       case "auth-user-pass": props["AuthMech"] = "3";	    
	   break;	    
    } 
	
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
