---
title: Common Errors
---
**In this section**

* TOC
{:toc}

## Keywords for Relevant Log Lines.
You can search for relevant logs by searching the logs `connector-plugin`, `connector-plugin-warning`, and `connector-plugin-error`, or by searching directly for your connector class.
[Tableau Log Viewer](https://github.com/tableau/tableau-log-viewer){:target="_blank"} is a good tool to view and filter relevant logs when developing your connector. 

## Connector Doesn't show in Connector List
If your connector does not show up, please check the Tableau logs for any failures for your connector in `/Users/<username>/Documents/My Tableau Repository/Logs/log.txt`. Tableau logs all the file paths for the tacos attempted to load under the keyword `connector-plugin`, and you can search for your connector class or your taco's file name to jump to it directly to that part. If you don't see any log lines for your connector, please check it in the correct place. Follow the section  **Use a connector built with Tableau Connector SDK**
  in [this doc](https://help.tableau.com/current/pro/desktop/en-us/examples_connector_sdk.htm#use-a-connector-built-with-tableau-connector-sdk){:target="_blank"} to check where the taco should be placed. 

##  Plugin Script Faliure
If you get 
  - `Running the plugin script failed`
  - `Running the plugin script component exceeded the timeout: %1ms`
  Check that you've correctly implemented `connectionBuilder.js` and `connectionProperties.js`  are correct. Please follow [this](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins/postgres_jdbc){:target="_blank"} example for the Postgres JDBC connector as the starting point for all the files necessary to successfully build a connector. You can see the exact javascript error by searching for `QJSEngine`, which will be nearby to a `connector-plugin-error` log line.
 Please refer to the [API reference page]({{ site.baseurl }}/docs/api-reference#javascript-function-call-signature) `Javascript function call Signature` to check the javascript call signatures.



## Signature Verification Failed
If you are getting `Package signature verification failed during connection creation.` in the logs for your connector, you can still use your connector by disabling the signature verification during development by using:
- Windows : `"C:\Program Files\Tableau\Tableau 2023.2\bin\tableau.exe" -DDisableVerifyConnectorPluginSignature=true` 
- Mac:  `/Applications/Tableau\ Desktop\ 2023.2.app/Contents/MacOS/Tableau -DDisableVerifyConnectorPluginSignature=true`. 
This error will show up when you click "Sign in" on the connector dialog.
You can see the signature error in the logs, or outside of Tableau by running `jarsigner --verify --strict --verbose --certs [path_to_taco]` .

To fix the issue with signature verification follow the **Sign your packaged connector with jarsigner** section of 
 [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign#sign-your-packaged-connector-with-jarsigner). 
