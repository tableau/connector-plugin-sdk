/**
 * Copyright (C) 2017-2019 Dremio Corporation. This file is confidential and private property.
 */
(function propertiesbuilder(attr) {
    function isAttributeSet(value) {
        return (value !== "") && (value !== null) && (value !== undefined);
    }

    var props = {};
    var username = "";
    var password = "";

    var authMethod = attr[connectionHelper.attributeAuthentication];

    if (authMethod == "Basic" || authMethod == "basic" || authMethod == "auth-user-pass" || !isAttributeSet(authMethod)) {
        username = attr[connectionHelper.attributeUsername];
        password = attr[connectionHelper.attributePassword];

        if (attr["workgroup-auth-mode"] == "db-impersonate") {
            var str = attr[":workgroup-auth-user"];
            
            if (isAttributeSet(str)) {
                // Strip domain, if any
                var arr = str.split("\\");
                if (arr.length == 2) {
                    props["impersonation_target"] = arr[1];
                } else {
                    props["impersonation_target"] = str;
                }
            }
        }
    } else if (authMethod == "auth-pass") {
        password = attr[connectionHelper.attributePassword];
        props["token_type"] = "personal_access_token";

    } else if (authMethod == "oauth") {
        password = attr["ACCESSTOKEN"];
        props["token_type"] = "access_token";
    }

    props["user"] = username;
    props["password"] = password;

    var product = attr["v-dremio-product"];

    var isUseSSL = attr["sslmode"];
    if (product == "v-cloud" || isUseSSL == "require") {
        props["ssl"] = "true";
    } else {
        props["ssl"] = "false";
    }

    projectId = attr["v-project-id"];
    if (isAttributeSet(projectId)) {
        props["project_id"] = projectId;
        props["catalog"] = projectId;
    }

    routingEngine = attr["v-engine"];
    if (isAttributeSet(routingEngine)) {
        props["engine"] = routingEngine;
    }

    routingTag = attr["v-routing-tag"];
    if (isAttributeSet(routingTag)) {
        props["routing_tag"] = routingTag;
    }

    routingQueue = attr["v-routing-queue"];
    if (isAttributeSet(routingQueue)) {
        props["routing_queue"] = routingQueue;
    }

    return props;
})
