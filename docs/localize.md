---
title: Localize Your Connector
---

Tableau products are localized in English (United States), English (United Kingdom), French, German, Brazilian Portuguese, Spanish, Korean, Japanese, simplified Chinese, and traditional Chinese.

Connector SDK supports localizing connectors in these languages. You can localize the strings that display in the Tableau user interface, such as the connector name and the prompts in the connection dialog.

For the best user experience with Tableau, we recommended that you include translation support in your connector.
## Specify localized Strings
Localized strings are specified using tag `@string/<string_id>/`, for example, `@string/database_prompt/`. You can use the tag anywhere a string is defined in the `manifest.xml` file or the Tableau Custom Dialog (.tcd) file.


Here is an example of a Tableau Custom Dialog (.tcd) file with localized strings.
```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
<connection-config>
...
<db-name-prompt value="@string/database_prompt/" />
<port-prompt value="@string/port_prompt/" default="5432" />
</connection-config>
</connection-dialog>
```


## Add String Translations
String translations are added using resource files. Each language has its own resource file. The resource files must follow the naming convention `resources-<language>-<region>.xml`, where `<language>` is a lowercase two letter language code and `<region>` is an uppercase two letter region code. The resource file names for the currently supported languages are listed below.


```
resources-de_DE.xml
resources-en_GB.xml
resources-en_US.xml
resources-es_ES.xml
resources-fr_FR.xml
resources-ga_IE.xml
resources-it_IT.xml
resources-ja_JP.xml
resources-ko_KR.xml
resources-pt_BR.xml
resources-zh_CN.xml
resources-zh_TW.xml
``` 
The resource files must be encoded in UTF-8. Add the string translation for each language to the corresponding resource file.


When you use any localized strings in your connector, you must include resources-en-US.xml, and it must include all localized strings in English (United States). If a string translation is missing in a resource file, or the resource file itself is missing, Tableau falls back to use the English (United States) translation. 


Here is an example of resource file `resources-en_US.xml` and corresponding `resources-es_ES.xml`.


resources-en_US.xml 
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
<string name="port_prompt">Port:</string>
<string name="database_prompt">Database:</string>
</resources>
```
