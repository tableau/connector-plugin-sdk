# Tableau Connector Plugin SDK - Early Release


At Tableau, we pride ourselves in helping people see and understand their data... wherever it may be. A key investment for us has been creating a way to enable both partners and customers help us in this mission. Thank you for expressing your interest in joining us on that mission.  On behalf of the Connectivity team at Tableau, I’d like to announce the early release of our Connector Plugin SDK!  

In order to kick this off, please take a look at the attached documents, and over the next few weeks be on the lookout while we share some additional information as part of the 2019.1 Beta 2 cycle.  

For more information please reach out to us through GitHub Issues here or contact me directly.


## FAQ
**If I build a plugin, will Tableau include it?**  

Not necessarily. We plan to include connector plugins on a case by case basis. The work needed to include connectors with a shipping Tableau product extends well beyond the code itself and into the continuous integration and supportability concerns. We are looking at providing a way to include third-party connectors in the future through some exciting new features as well as a more formal certification program.

**Why would I build a plugin instead of just telling users to use Other ODBC/JDBC?**
   
Connector Plugins allow for a more extensive level of customization than using generic “Other ODBC”, and it is possible to apply many of the optimizations that current "named" connectors in Tableau go through.  
 
**Can I make a plugin for OLAP Cubes, file-based, or REST API-based connections?**
We intend for the Connector Plugin SDK to eventually support additional connector types, but we're starting with ODBC and JDBC.  

**How would I distribute plugins to my customers?**
Until v1.0 is officially released in mid-2019, we do NOT recommend distributing connector plugins to customers. Based on your feedback we expect to iterate for the next two quarters with breaking changes to a number of plugin aspects.  

After v1.0, we expect to work with partners to review test results and discuss customer support processes.

**What types of things might change during the v1.0 of plugin development?**
Many things may change before mid-2019, but most likely how a connector plugin is packaged as well as the components associated with enterprise authentication. We highly encourage you to sign up in GitHub or email us to get the latest information. Partners participating in the open sprint demos will get notice of any breaking changes in real-time.
