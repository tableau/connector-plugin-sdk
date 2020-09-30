(function propertiesbuilder(attr) {
    function isEmpty(str) {
	    return (!str || 0 === str.length); 
    }
	
    var props = [];

    // Adding properties for Kerberos authentication
    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
	    var tableauServerUser = attr[connectionHelper.attributeTableauServerUser];
        // tableauServerUser is not empty means this is a Tableau Server Environment	    
        if (!isEmpty(tableauServerUser)) {
            props["user"] = tableauServerUser;
            props["gsslib"] = "gssapi";	 
            props["jaasLogin"] = "false";    
        } else {
        // properties for Kerberos SSO on Tableau Desktop    
            props["gsslib"] = "gssapi";	 
            props["jaasLogin"] = "false";  
            props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
        }            
                  
    // username-password auth     
    } else if (attr[connectionHelper.attributeAuthentication] == "auth-user-pass"){
        props["user"] = attr[connectionHelper.attributeUsername];
        props["password"] = attr[connectionHelper.attributePassword];
    }   
        
    
    if (attr[connectionHelper.attributeSSLMode] == "require")
    {        
        props["ssl"] = "true";
        props["sslmode"] = "require";
    }

    var formattedProps = [];

    for (var key in props) {
        formattedProps.push(connectionHelper.formatKeyValuePair(key, props[key]));
    }
    
    return formattedProps;
})
