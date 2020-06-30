---
title:  "Tableau 2020.3 Beta released"
abstract: "Sneak peek on the features available on 2020.3"
---
**Note**: Certain features can be seen in the 2020.3 branch, but they are not final and may have issues, and that we will merge them into master when 2020.3 is released to the public. <br/>

With the release of Tableau 2020.3 Beta, you get a sneak peek into the features available in Tableau 2020.3 and Connector SDK. 
- __Connection Dialogs v2__ <br/>
Connection Dialogs v2 feature, which will allow for more flexible connection dialogs. Learn more about connection Dialogs v2 [here]({{ site.baseurl }}/docs/mcd).
- __Updated Dialect Samples__ <br/>
The 2020-3 branch of connector SDK contains the complete dialect definition file for [Postgres JDBC connector](https://github.com/tableau/connector-plugin-sdk/blob/dev-2020.3/samples/plugins/postgres_jdbc/dialect.tdd) and [Postgres ODBC connector](https://github.com/tableau/connector-plugin-sdk/blob/dev-2020.3/samples/plugins/postgres_odbc/dialect.tdd). This should serve as a good example to write a dialect file for JDBC or ODBC connectors with 2020.3 updates.
- __Delegation UID__ <br/>
This applies to databases that support a user(authenticated_user) that can delegate requests to another user(delegated_user) by enabling the client to pass a DelegationUID(delegated_user) to the database server. More details on this feature will be added with the release of 2020.3. 
- __Scenario-based Samples__ <br/>
Scenario-based samples provide good examples for specific scenarios partners might face while developing their connectors.  They are in the master branch of Connector SDK.
    - __Extract Only Connector__ See more [here](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/scenarios/extract_only/sqlite_extract).
    - __MySQL Based Connector__ See more [here](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/scenarios/mysql_based/mysql_odbc).
    - __Connectors Using Vendor Attributes__ See more [here](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/scenarios/vendor_attributes/postgres_vendor).
- __'format-true' and 'format-false' to allow literal, predicate and value attributes__ <br/>
With the release of Tableau 2020.3, `format-true` and `format-false` will have two parameters, literal and predicate. See more about *Boolean Support* [here]({{ site.baseurl }}/docs/dialect#boolean-support). We have also added the support for `unicode-prefix` in `format-string-literal`. See more about *String Literal Support* [here]({{ site.baseurl }}/docs/dialect#string-literal-support) 


