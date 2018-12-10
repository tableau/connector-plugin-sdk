(function propertiesBuilder(attr)
{
    //This script is only needed if you are using a JDBC driver. 
    
    var params = {};
    
    //set keys for properties needed for connecting using JDBC
    var KEY_USER = "user";
    var KEY_PASSWORD = "password";
    var KEY_WAREHOUSE = "s3_staging_dir"
    
    //set connection properties from existing attributes
    params[KEY_USER] = attr[connectionHelper.attributeUsername];
    params[KEY_PASSWORD] = attr[connectionHelper.attributePassword];
    params[KEY_WAREHOUSE] = attr[connectionHelper.attributeWarehouse];  
    
    var formattedParams = [];
    
    //Format the attributes as 'key=value'. By default some values are escaped or wrapped in curly braces to follow the JDBC standard, but you can also do it here if needed.
    for (var key in params)
    {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }
    
    //The result will look like (search for jdbc-connection-properties in tabprotosrv.log):
    //"jdbc-connection-properties","v":{"password":"********","s3_staging_dir":"s3://aws-athena-s3/","user":"admin"}
    return formattedParams;
})