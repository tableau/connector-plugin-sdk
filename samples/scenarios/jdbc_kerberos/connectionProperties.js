(function propertiesbuilder(attr) {
    function isEmpty(str) {
	    return (!str || 0 === str.length); 
    }
	
    var props = [];

    // Adding properties for Kerberos authentication
    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
	var str = attr[connectionHelper.attributeTableauServerUser];
        // str is not empty means it is Tableau Server which is connecting	    
	if (!isEmpty(str)) {
            props["user"] = str;
            props["gsslib"] = "gssapi";	 
            props["jaasLogin"] = "false";    
        } else if(connectionHelper.GetPlatform() === "win") {
            // gsslib property for invoking SSPI on Tableau Desktop for Windows
            props["gsslib"] = "sspi";	 
        } else if(connectionHelper.GetPlatform() === "mac") {
            // add this jaasApplicationName used by Tableau's embedded jaas.conf file
	    props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
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
