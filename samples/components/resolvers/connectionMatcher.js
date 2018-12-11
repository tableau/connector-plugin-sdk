(function matcher(attr1, attr2)
{

    //Bail early if the connection class is different
    if (attr1["class"] != attr2["class"])
        return false;

    //Set the default values populated during Protocol normalization.
    if (attr2["authentication"] == undefined || attr2["authentication"] == "")
        attr2["authentication"] = "auth-teradata";

    // Now compare using the normal mechanism. This will ensure that we match
    // existing Protocols which have these attributes populated with defaults
    // within TeradataDSBuilder; that step is only performed after the ProtocolPool
    // checks for matches and must construct a new Protocol, so this is the
    // only opportunity to handle default values.
    if (connectionHelper.MatchesConnectionAttributes(attr1, attr2))
        return true;

    return false;
})


