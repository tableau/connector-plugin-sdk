---
title: Common Errors
---
**In this section**

* TOC
{:toc}

## Keywords for Relevant Log Lines.
Users can search for relevant logs by searching the logs `connector-plugin`, `connector-plugin-warning`, and `connector-plugin-error`. 
Search for the relevant logs in `/Users/<username>/Documents/My Tableau Repository/Logs/log.txt` for your current instance. 
[Tableau Log Viewer](https://github.com/tableau/tableau-log-viewer) is a good tool to view and filter relevant logs when developing your connector. 


##  Plugin Script Faliure
If you get 
  - `Running the plugin script failed`
  - `Running the plugin script component exceeded the timeout: %1ms`
  Check that you've correctly implemented `connectionBuilder.js`, `connectionProperties.js` and `required attributes` are correct. Please follow [this](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins/postgres_jdbc) example for the Postgres JDBC connector as the starting point for all the files necessary to successfully build a connector. 


## Connector Doesn't show in Connector List
- If your connector does not show up. Check the location of the taco. Follow the section  **Use a connector built with Tableau Connector SDK**
  in [this doc]([https://help.tableau.com/current/pro/desktop/en-us/examples_connector_sdk.htm)
- Check that the the taco is signed with a valid certificate. Follow **Sign your packaged connector with jarsigner** section of 
 [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign). 
- Check the Tableau logs for any failures for your connector in `/Users/<username>/Documents/My Tableau Repository/Logs/log.txt`


## Signature Verification Failed
If you are getting `Package signature verification failed during connection creation.` in the logs for your connector, you can still use your connector by disabling the signature verification during development by using:
- Windows : `"C:\Program Files\Tableau\Tableau 2023.2\bin\tableau.exe" -DDisableVerifyConnectorPluginSignature=true` 
- Mac:  `/Applications/Tableau\ Desktop\ 2023.2.app/Contents/MacOS/Tableau -DDisableVerifyConnectorPluginSignature=true`. 

To fix the issue with signature verification follow the **Sign your packaged connector with jarsigner** section of 
 [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign). 
