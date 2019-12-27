(function propertiesbuilder(attr) {
    function isEmpty(str) {
	    return (!str || 0 === str.length); 
    }
	
    var props = [];

    // integrated auth
    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
	    var str = attr[":tableau-server-user"];
        // properties for kerberos on Tableau Server 	    
	    if (!isEmpty(str)) {
            props["user"] = str;
            props["gsslib"] = "gssapi";	 
            props["jaasLogin"] = "false";    
        } else if(connectionHelper.GetPlatform() == "win") {
            // property for SSPI on Tableau Desktop
            props["gsslib"] = "sspi";	 
        }         
                  
    // username-password auth     
    } else if (attr[connectionHelper.attributeAuthentication] == "username-password"){
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
