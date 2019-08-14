---
title: Localize Your Connector
---

Tableau products have been localized to English (United States), English (United Kingdom), French, German, Brazilian Portuguese, Spanish, Korean, Japanese, simplified Chinese and traditional Chinese.

Connector SDK supports localization of connectors to the languages mentioned above.

The strings showing up on Tableau UI can be localized. For example, the connector name and the prompts in connection dialog.

For the best user experience with Tableau, it is highly recommended that translation support is included.
## Specify localized Strings
Localized strings are specified using tag `@string/<string_id>/`, for example, `@string/database_prompt/`. You can use the tag anywhere a string is defined in `manifest.xml` or Tableau Custom Dialog (.tcd) file.

Here is an example of a Tableau Custom Dialog (.tcd) file with localized strings.
```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
  <connection-config>
    <authentication-mode value='Basic' />
    <authentication-options>
      <option name="UsernameAndPassword" default="true" />
    </authentication-options>
    <db-name-prompt value="@string/database_prompt/" />
    <port-prompt value="@string/port_prompt/" default="5432" />
  </connection-config>
</connection-dialog>
```

## Add String Translations
String translations are added using resource files.  Each language has its resource file. The resource files must follow naming convention `resources-<language>-<region>.xml`, where `<language>` is lowercase two letter language code and `<region>` is uppercase two letter region code. The resource file names for currently supported languages is listed below.

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
The resource files must be encoded in UTF-8.

If the resource file for a language is missing, or a string translation is missing in a resource file if you have any localized strings in your connector, Tableau will fall back to use translation in English (United States).  You must have resources-en-US.xml included in your connector, that file must include all localized strings.
 
Here is an example of resource file `resources-en_US.xml` and corresponding `resources-es_ES.xml`.
 
resources-en_US.xml 
 ```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
  <string name="port_prompt">Port:</string>
  <string name="database_prompt">Database:</string>
</resources>
```
resources-es_ES.xml 
 ```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
  <string name="port_prompt">Puerto:</string>
  <string name="database_prompt">Base de datos:</string>
</resources>
```

