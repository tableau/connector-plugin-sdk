(function dsbuilder(attr) {
    var urlBuilder = "jdbc:impala://" + attr[connectionHelper.attributeServer] + ":" + attr[connectionHelper.attributePort] + ";"
    
    return [urlBuilder];
})
