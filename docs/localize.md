---
title: Localize Your Connector
---

Tableau products are localized in English (United States), English (United Kingdom), French (France), French (Canada), German, Brazilian Portuguese, Spanish, Korean, Japanese, simplified Chinese, and traditional Chinese.

Connector SDK supports localizing connectors in these languages. You can localize the strings that display in the Tableau user interface, such as the connector name and the prompts in the connection dialog.

For the best user experience with Tableau, we recommended that you include translation support in your connector.
## Specify localized strings
You can specify localized strings using the <span style="font-family: courier new">@string/<string_id>/</span> tag. For example:    
  `@string/database_prompt/`

 You can use the tag anywhere a string is defined in the manifest.xml file or the Tableau Connection Dialog (.tcd) file.

This is an example of a Tableau Connection Dialog (.tcd) file with localized strings:
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


## Add string translations
You can add string translations to a connection dialog using resource files. Each language has its own resource file. The resource files must follow this naming convention:

<span style="font-family: courier new">resources-*language*-*region*.xml</span>

  where:
  - *language* is a lowercase two-letter language code.
  - *region* is an uppercase two-letter region code.

This list shows the resource filenames for the currently supported languages:  
```
resources-de_DE.xml
resources-en_GB.xml
resources-en_US.xml
resources-es_ES.xml
resources-fr_CA.xml
resources-fr_FR.xml
resources-ga_IE.xml
resources-it_IT.xml
resources-ja_JP.xml
resources-ko_KR.xml
resources-pt_BR.xml
resources-zh_CN.xml
resources-zh_TW.xml
```
__Note:__ The resource files must be encoded in UTF-8.

Add the string translation for each language to the corresponding resource file.

When you use any localized strings in your connector, you must include resources-en-US.xml, and it must include all localized strings in English (United States). If a string translation is missing in a resource file, or the resource file itself is missing, Tableau falls back to use the English (United States) translation.

Here are examples of resources-en_US.xml (English/United States) and the corresponding resources-es_ES.xml (Spanish/Spain) resource files.

__resources-en_US.xml__  
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
  <string name="port_prompt">Port:</string>
  <string name="database_prompt">Database:</string>
</resources>
```
__resources-es_ES.xml__  
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
  <string name="port_prompt">Puerto:</string>
  <string name="database_prompt">Base de datos:</string>
</resources>
```
