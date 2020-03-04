# Connection Dialog v2

**IMPORTANT:** This is alpha software and should be used in a test environment. Do not deploy the connector to a production environment.

Connection Dialog v2 is a new feature that enables a more fully data-driven connection dialog for plugin connectors. Additionally, it provides some control over the metadata hierarchy elements--Database, Schema, and Table--both in the connection dialog and in the schema viewer, which the user sees after the connection is established.

This feature is new in 2020.2. It is an alpha feature, and as such it is available in Desktop only. In future releases it will become available in other Tableau products including Server and Prep. 

# How to Use Connection Dialog v2

To use Connection Dialog v2, in the manifest replace `<connection-dialog>` with `<connection-fields>`, described below. The connector will fail to load if both elements appear in the manifest.

If you wish to modify metadata hierarchy behavior you can add to the manifest a `<connection-metadata>` element, which is also described below. 

```xml
  manifest.xml

  <?xml version='1.0' encoding='utf-8' ?>

  <connector-plugin class=...>
    ...
    <connection-fields   file='connection-fields.xml'/>    <!-- use this instead of connection-dialog -->
    <connection-metadata file='connection-metadata.xml'/>  <!-- add this to modify metadata hierarchy behavior -->
    <connection-resolver file="connectionResolver.tdr"/>
    <dialect file='dialect.tdd'/>
  </connector-plugin>
```

# The Connection Fields File

The Connection Fields file dictates the content and behavior of Connection Dialog as seen by the user. It also specifies the names of the connection attributes that will be available, along with the values specified by the user, in the ConnectionBuilder(). 

The Connection Fields file ([XSD](https://github.com/tableau/connector-plugin-sdk/blob/dev-2020.2/validation/connection_fields.xsd)) is indentified in the manifest using the `<connection-fields>` element. Here we discuss the structure of this file. 

To avoid confusion, in the following we use the term "field" in place of "connection attribute," and use the generic term "attribute" to mean an XML element attribute. 

## XML Elements

### `<connection-fields>`

This is the parent element for fields.

### `<field>`

Each connection attribute is represented by a field element in the XML. The field element has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| name  | Unique name of the field, which is used in the ConnectionBuilder() | No | Names must be unique, and cannot be any of the reserved names `dbname`, `schema`, `tablename`. | If there is a Tableau-defined name for this attribute, that name must be used. The Tableau-defined attribute name list is coming soon. |
| label | Label that appears on the connection dialog for the field | No | | |
| value-type | Dictates the default validation rule and the UI widget | No | Allowed Values / UI Widget Type <br> <ul><li>`string` / text box</li><li>`option` / drop-down</li><li>`boolean` / checkbox</li><li>`file` / file picker</li> | In the 2020.2 release `file` is not supported. |
| default-value | Default value for the attribute | Yes	| Default values by value-type <br> <ul><li>string: `""`</li><li>option: first option</li><li>boolean: `false`</li><li>file: `""`</li></ul>| |
| optional | Whether the user must specify a value for the attribute | Yes | Allowed values: `true`, `false`. <br> Default value: `false`. | |
| editable | Whether the user can edit the attribute | Yes | Allowed values: `true`, `false`. <br> Default value: `true`. | When set to `false`, the attribute is not shown in the connection dialog, and its default-value is passed to the ConnectionBuilder(). |
| secure | Whether the attribute value is sensitive data, and should be suppressed from logs | Yes | Allowed values: `true`, `false`. <br> Default value: `false`. | In the 2020.2 release only `password` is allowed to be secure. The connector will not load if other fields are specified as secure. |
| category | Specifies which tab contains the field for the attribute. | Yes | Allowed values: <br> <ul><li>`endpoint` (for server, port, etc.)</li><li>`metadata` (for data hierarchy)</li><li>`authentication`</li><li>`general`</li><li>`initial-sql`</li><li>`advanced`</li></ul> Default value: `general` | In the 2020.2 release this has minimal effect; `<initial-sql>` and `<advanced>` are not supported. | 

### `<validation-rule>`

An optional child of field, validation-rule lets you specify a regular expression for validating the user input. 
It has the following XML attributes.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| reg-exp | Regular Expression | No | | In the 2020.2 release the validation rule is not enforced. |

### `<boolean-options>`

A required child of field when value-type is `boolean`, this is the container element for the two boolean options. It has no XML attributes. 

### `<false-value>`

A required child of boolean-options when value-type is `boolean`. This is the value to send to ConnectionBuilder() when the user does not check the box.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| value | The value to send to the ConnectionBuilder() | No | Any string value | |

### `<true-value>`

A required child of boolean-options when value-type is `boolean`. This is the value to send to ConnectionBuilder() when the user checks the box.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| value | The value to send to the ConnectionBuilder() | No | Any string value | |

### `<selection-group>`

A required child of field when value-type is `option`. This is the container element for the options that will appear in the drop-down. It has no XML attributes. 

Multiple selection-group elements can be used; see `<conditions>`.

### `<option>`

A child of selection-group, this represents one entry in the drop-down. It has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| value | The value sent to ConnectionBuilder() | No | Any string value | |
| label | The text the user sees | No | Any string value | |

### `<conditions>`

An optional child of field or selection group, this is used for conditional display. It specifies whether the field or selection group should be visible in the dialog based on the values the user has specified for other fields. 

Multiple condition elements can be used, and will be OR'd. That is, the field or selection group will be visible when any one or more of the `<condition>` elements is matched. The connector will not load if there are circular references.

Hence, this is a container element for the condition elements. It has no XML attributes. 

### `<condition>`

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| field | Name of the field whose value will be checked for equality | No | Any string value | |
| value | The value to match. If the field's value is equal to this, the condition is true. | No | Any string value | |


## Example

The Connection Fields file below demonstrates both conditional display of fields and a non-editable field. 

The images below show the Connection Dialog produced using this file. The left side shows the dialog as it is initially displayed, after the user enters a Server name. Note that the default Authentication option is No Authentication, and the Sign In button is enabled. The right side shows what it changes to when the user selects Authentication Username and Password. 

<p float="left">
  <img src="{{ site.baseurl }}/assets/mcd-connection-dialog-1.png" alt="Connection Dialog as initially displayed, after the user enters a Server name" align=top hspace=40/>
  <img src="{{ site.baseurl }}/assets/mcd-connection-dialog-2.png" alt="Connection Dialog after user selects Authentication Username and Password" align=top />
</p>

AutoReconnect is an example of a non-editable field. It will not be visible in the connection dialog, but its default value of `0` will be available in ConnectionBuilder() to add to the Connection String.

```xml
<?xml version="1.0" encoding="utf-8"?>
 
<connection-fields>

  <field name="server" label="Server" category="endpoint" value-type="string">
    <validation-rule reg-exp="^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$"/>
  </field>
 
  <field name="port" label="Port" category="endpoint" value-type="string" default-value="5432"/>
 
  <field name="authentication" label="Authentication" category="authentication" value-type="selection" >
    <selection-group>
      <option value="auth-none" label="No Authentication"/>
      <option value="auth-user" label="Username"/>
      <option value="auth-user-pass" label="Username and Password"/>
    </selection-group>
  </field>

  <field name="username" label="Username" category="authentication" value-type="string">
    <conditions>
      <condition field="authentication" value="auth-user"/>
      <condition field="authentication" value="auth-user-pass"/>
    </conditions>
  </field>
 
  <field name="password" label="Password" category="authentication" value-type="string" secure="true">
    <conditions>
      <condition field="authentication" value="auth-user-pass"/>
    </conditions>
  </field>
 
  <field name="AutoReconnect" label="" value-type="string" default-value="0" editable="false" />
 
</connection-fields>
```


# The Connection Metadata File

The Connection Metadata file provides some limited control over the metadata hierarchy elements Database, Schema, and Table. For example, it can be used to:
- provide a default value for Database on the connection dialog, and
- supress the Database, Schema, or Table selectors from the schema viewer, which the user sees after the connection is established.

If you don't provide a Connection Metadata file, then by default all three selectors will be shown.

The Connection Metadata file ([XSD](https://github.com/tableau/connector-plugin-sdk/blob/dev-2020.2/validation/connector_plugin_metadata.xsd)) is the one named in the manifest in the `<connection-metadata>` element. Here we discuss the structure of this file. 

## XML Elements

### `<connection-metadata>`

This is the parent element for the metadata hierarchy elements. 

### `<database>`

An optional child of `<connection-metadata>`, this controls whether the Database selector is shown in the connection dialog and the schema viewer. If it is not present, Database does not appear. It has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| enabled | Whether to show the Database selector | No | Allowed values: `true`, `false`| |
| label | The label shown to the user | Yes | Default value: `Database` | |

### `<field>`

An optional child of `<database>`, this indicates whether the user must provide a value for Database, and a default value for it. It has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| optional | Whether the user must provide a value for Database | Yes | Allowed values: `true`, `false`<br>Default value: `false`| |
| default-value | A default value for Database | Yes | Default value: `""` | |

### `<schema>`

An optional child of `<connection-metadata>`, this controls whether the Schema selector is shown in the shema viewer. If it is not present, Schema does not appear. It has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| enabled | Whether to show the Schema selector | No | Allowed values: `true`, `false`| |
| label | The label shown to the user | Yes | Default value: `Schema` | |

### `<table>`

An optional child of `<connection-metadata>`, this controls whether the Table selector is shown in the shema viewer. If it is not present, Table does not appear. It has the following XML attributes. 

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| enabled | Whether to show the Table selector | No | Allowed values: `true`, `false`| |
| label | The label shown to the user | Yes | Default value: `Table` | |


## Example

The Connection Metadata file below matches the default--that is, what you get if you don't reference the file in the manifest at all--except that it provides a default value of 'TestV1' for Database. 

```xml
<?xml version="1.0" encoding="utf-8"?>

<connection-metadata>
  <database enabled='true' label='Database'>
    <field optional='true' default-value='TestV1' />
  </database>
  <schema enabled='true' label="Schema" />
  <table enabled='true' label="Table" />
</connection-metadata>
```

The left side image below shows what the Schema Viewer will look like with this Connection Metadata file. The right side shows what it will look like if you remove the `<schema>` element from the file.

<p float="left">
  <img src="{{ site.baseurl }}/assets/mcd-schema-viewer-1.png" alt="Schema Viewer with Connection Metadata file" align=top hspace=40/>
  <img src="{{ site.baseurl }}/assets/mcd-schema-viewer-2.png" alt="Schema Viewer after removing schema element from Connection Metadata file" align=top />
</p>

