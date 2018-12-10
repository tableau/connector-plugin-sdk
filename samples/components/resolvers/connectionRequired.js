(function requiredAttrs(attr)
{
    var params = ["enum-with-permissions", "expected-driver-version", connectionHelper.attributeInitialSQL, "odbc-native-protocol", "query-band-spec", "disable-unicode", "source-charset", "encryptionMode", connectionHelper.attributeAuthentication, "odbc-connect-string-extras"];

    if (attr["authentication"] != undefined && attr["authentication"] != "auth-integrated")
    {
        params.push("username");
        params.push("password");
    }
    params.push(connectionHelper.attributeServer);
    if (attr["authentication"] == undefined || attr["authentication"] == "")
    {
        attr["authentication"] = "auth-teradata";
    }
    params = connectionHelper.SetImpersonateAttributes(attr, params);
    return params;
})
