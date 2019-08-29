(function dsbuilder(attr)
{
    var params = [];

    if (attr["server"].toLowerCase() == "(local)")  // match ODBC implementation, even though JDBC driver does not understand (local)
    {
        attr["server"] = "localhost";
        // local connection, no auth specified
        // port is required
    }
    else
    {
        params["UID"] = attr["username"];
        params["PWD"] = attr["password"];
    }

    var urlBuilder = "jdbc:ingres://" + attr["server"] + ":" + attr["port"] + "/" + attr["dbname"] + ";";

    var formattedParams = [];

    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    urlBuilder += formattedParams.join(";")

    return [urlBuilder];
}) 
 
