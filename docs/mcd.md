---
title: Connection Dialog v2
---
**IMPORTANT:** This feature is available only in Tableau 2020.3 or later. For compatibility with older versions, use Connection Dialog v1 (documentation found [here]({{ site.baseurl }}/docs/ui)).

Connection Dialog v2 is a new feature that enables a more fully data-driven connection dialog for plugin connectors. Additionally, it provides some control over the metadata hierarchy elements--Database, Schema, and Table--both in the connection dialog and in the schema viewer, which the user sees after the connection is established.


# How to Use Connection Dialog v2

To use Connection Dialog v2, in the manifest replace `<connection-dialog>` with `<connection-fields>`, shown in the following example. The connector will fail to load if both elements appear in the manifest.

If you want to modify metadata hierarchy behavior you can add to the manifest a `<connection-metadata>` element, which is also shown in the following example.

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

The Connection Fields file ([XSD](https://github.com/tableau/connector-plugin-sdk/blob/master/validation/connection_fields.xsd)) is identified in the manifest using the `<connection-fields>` element. Here we discuss the structure of this file.

To avoid confusion, in the following we use the term "field" in place of "connection attribute," and use the generic term "attribute" to mean an XML element attribute.

## XML Elements

### `<connection-fields>`

This is the parent element for fields.

### `<field>`

Each connection attribute is represented by a field element in the XML. The field element has the following XML attributes.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| name  | Unique name of the field: used in the platform, connection-normalizer, and connection-builder | No | Names must be unique <br> Name is a Tableau-defined name **OR** prefixed with `v-` | If there is a Tableau-defined name for this attribute, that name must be used. See 'Connection Field Platform Integration' section below. |
| label | Label that appears on the connection dialog for the field | No | | |
| value-type | Dictates the default validation rule and the UI widget | No | Allowed Values: UI Widget Type <br> `string`: text field <br> `textbox`: text area <br>  `option`: drop-down  <br> `boolean`: checkbox <br> `file`: file picker | In the 2020.2 release `file` is not supported. <br>  In the 2020.2 and  2020.3 releases `textbox` is not supported.|
| default-value | Default value for the attribute | Yes	| Default values by value-type <br> string: `""` <br> option: first option <br> boolean: `false` <br> file: `""` | |
| optional | Whether the user must specify a value for the attribute | Yes | Allowed values: `true`, `false`. <br> Default value: `false`. | If a field is in the `advanced` category and is not optional, it must be given a default value. |
| editable | Whether the user can edit the attribute | Yes | Allowed values: `true`, `false`. <br> Default value: `true`. | When set to `false`, the attribute is not shown in the connection dialog, and its default-value is passed to the ConnectionBuilder(). |
| secure | Whether the attribute value is sensitive data, and should be suppressed from logs | Yes | Allowed values: `true`, `false`. <br> Default value: `false`. | In the 2020.2 release only `password` is allowed to be secure. The connector will not load if other fields are specified as secure. **Any fields not marked secure will be logged and persisted to Tableau workbook XML in plain text.** |
| category | Specifies which tab contains the field for the attribute. | Yes | Allowed values: <br> `endpoint` (for server, port, and so on) <br> `metadata` (for data hierarchy) <br> `authentication` <br> `general` <br> `initial-sql` <br> `advanced` <br> Default value: `general` | In the 2020.2 release this has minimal effect; `<initial-sql>` and `<advanced>` are not supported. |

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

A required child of field when value-type is `option`. This is the container element for the options that will appear in the dropdown. It has no XML attributes.

Multiple selection-group elements can be used; see `<conditions>`.

### `<option>`

A child of selection-group, this represents one entry in the dropdown. It has the following XML attributes.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| value | The value sent to ConnectionBuilder() | No | Any string value | |
| label | The text the user sees | No | Any string value | |

### `<conditions>`

An optional child of field or selection group, this is used for conditional display. It specifies whether the field or selection group should be visible in the dialog based on the values the user has specified for other fields.

Multiple condition elements can be used, and will be OR'd. That is, the field or selection group will be visible when any one or more of the `<condition>` elements is matched. Hence, this is a container element for the condition elements. It has no XML attributes.

The connector will not load if there are circular references.

### `<condition>`

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| field | Name of the field whose value will be checked for equality | No | Any string value | |
| value | The value to match. If the field's value is equal to this, the condition is true. | No | Any string value | |

## Connection Field Platform Integration

As referenced above in the `<field>` element section, some `name` attribute values describe platform functionality. It is important that if the desired connector functionality matches any of the descriptions below then the names and values below must be used.

If the field functionality does not match any of the descriptions below see 'Vendor Defined' section.

For each `<field>` element used its `name` attribute value is required to be listed in the `<attribute-list>` section of the `.tdr` file as well. See [connection-normalizer]({{ site.baseurl }}/docs/api-reference#connection-normalizer) for more details.

Additionally there are a set of reserved `name` attribute values not documented at this time. Recommendations, documentation, and enforcement coming soon.

### Endpoint

The endpoint attributes describe the unique parameters of a connection. Many connections provide additional field names and values not defined by the platform.

The connection field names below should specify the `endpoint` category.

| Name  | Meaning | Optional? | Value Notes |
| ----  | ------- | --------- | ----------- |
| server | Server or URL of connection | **No** | |
| port | Port of connection | Yes | Allowed Values: numeric value, 0–65535 |

### SSL

The SSL requirements of the connection. No platform functionality is provided at this time, but field name and values are reserved based on historical usage. If used, the value is generally passed to driver via ODBC connection string or JDBC properties.

The connection field names below can specify the `endpoint` or `general` category depending on dialog layout preference.

| Name  | Meaning | Optional? | Value Notes |
| ----  | ------- | --------- | ----------- |
| sslmode | Is SSL enabled or disabled for connection | Yes | Allowed Values: `require` or `''` (empty string) |

### Authentication

The authentication attributes control how and when a user is prompted to enter data source credentials. The primary scenarios where authentication occurs:

- Creating a connection with the connection dialog
- Opening a workbook and reconnecting to the data source
- Publishing a workbook or data source to Tableau Server

The connection field names below should specify the `authentication` category.

| Name  | Meaning | Optional? | Value Notes |
| ----  | ------- | --------- | ----------- |
| authentication | The authentication mode for connection | **No** | Allowed Values: Meaning <br> `auth-none`: None <br> `auth-user`: Username Only <br> `auth-user-pass`: Username and Password <br> `auth-pass`: Password Only <br> `oauth`: See the [OAuth Authentication Support](({{ site.baseurl }}/docs/oauth)) for details  |
| username | Username | Yes |  |
| password | Password | Yes | Supports `secure` field attribute |
| instanceurl | OAuth Instance Url | Yes | Only supported for use when `authentication` value is `oauth` |

### Vendor Defined

The vendor defined attributes are unique to an individual connector and do not imply platform functionality. They are pass-through to the connection normalizer, connection builder and properties builder.

**Vendor defined attributes will be logged and persisted to Tableau workbook xml in plain text.** This means the input for these fields cannot contain any Personally Identifiable Information (PII), as they are not secure and could leak sensitive customer information.

| Name  | Meaning | Optional? | Value Notes |
| ----  | ------- | --------- | ----------- |
| v- | The `v-` prefix indicates a vendor defined name | Yes | Any value compatible with type |
| vendor1 | Vendor attribute field 1 | Yes | Any value compatible with type. Parity with the vendor attribute value used in Connection Dialog V1 |
| vendor2 | Vendor attribute field 2 | Yes | Any value compatible with type. Parity with the vendor attribute value used in Connection Dialog V1 |
| vendor3 | Vendor attribute field 3 | Yes | Any value compatible with type. Parity with the vendor attribute value used in Connection Dialog V1 |

## Example 1 - A Non-Editable Field

The image shows the Connection Dialog produced using the Connection Fields file below. The username and password fields are required and don't have default-values, so the Sign In button will not be enabled until the user provides values for them.

![alt text]({{ site.baseurl }}/assets/mcd-connection-dialog-3.png "Connection Dialog with fixed authentication auth-user-pass")

The field "authentication" is non-editable and so will not be visible in the connection dialog, but its default value of "auth-user-pass" will be available in ConnectionBuilder() to add to the connection string.

```xml
<?xml version="1.0" encoding="utf-8"?>

<connection-fields>

  <field name="server" label="Server" category="endpoint" value-type="string">
    <validation-rule reg-exp="^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$"/>
  </field>

  <field name="port" label="Port" category="endpoint" value-type="string" default-value="5432"/>

  <field name="authentication" label="Authentication" category="authentication" value-type="string" editable="false" default-value="auth-user-pass" />

  <field name="username" label="Username" category="authentication" value-type="string" />

  <field name="password" label="Password" category="authentication" value-type="string" secure="true" />

</connection-fields>
```


## Example 2 - Conditional Display of Fields

The images show the Connection Dialog produced using the Connection Fields file below. The left side shows the dialog as it is initially displayed, after the user enters a Server name. Note that the default Authentication option is No Authentication, and the Sign In button is enabled. If the user clicks Sign In at this point, in ConnectionBuilder() the field "authentication" will have value "auth-none". The right side shows what it changes to when the user selects Authentication Username and Password. If the user enters a username and password then clicks Sign In, in ConnectionBuilder() the field "authentication" will have value "auth-user-pass".

![alt text]({{ site.baseurl }}/assets/mcd-connection-dialog-1.png "Connection Dialog as initially displayed, after the user enters a Server name")&nbsp;![alt text]({{ site.baseurl }}/assets/mcd-connection-dialog-2.png "Connection Dialog after user selects Authentication Username and Password")

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

</connection-fields>
```

## Example 3 - Boolean Field

This example shows how to add a checkbox to the dialog. For sslmode custom boolean values are required to be defined, following 'Connection Field Platform Integration' section below.  The default-value matches false-value, ensuring the checkbox is unchecked by default.  Within the ConnectionBuilder() the field "sslmode" will only have value "" or "require".

![alt text]({{ site.baseurl }}/assets/mcd-connection-dialog-4.png "Connection Dialog with a 'Require SSL' checkbox")

```xml
<?xml version="1.0" encoding="utf-8"?>

<connection-fields>
  ...

  <field name="sslmode" label="Require SSL" value-type="boolean" category="general" default-value="" >
    <boolean-options>
      <false-value value="" />
      <true-value value="require" />
    </boolean-options>
  </field>

</connection-fields>
```


# The Connection Metadata File

The Connection Metadata file provides some limited control over the metadata hierarchy elements Database, Schema, and Table. For example, it can be used to:
- provide a default value for Database on the connection dialog, and
- suppress the Database, Schema, or Table selectors from the schema viewer, which the user sees after the connection is established.

If you don't provide a Connection Metadata file, then by default all three selectors will be shown.

The Connection Metadata file ([XSD](https://github.com/tableau/connector-plugin-sdk/blob/master/validation/connector_plugin_metadata.xsd)) is the one named in the manifest in the `<connection-metadata>` element. Here we discuss the structure of this file.

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

An optional child of `<connection-metadata>`, this controls whether the Schema selector is shown in the schema viewer. If it is not present, Schema does not appear. It has the following XML attributes.

| Name  | Meaning | Optional? | Value Notes | Other Notes |
| ----  | ------- | --------- | ----------- | ----------- |
| enabled | Whether to show the Schema selector | No | Allowed values: `true`, `false`| |
| label | The label shown to the user | Yes | Default value: `Schema` | |

### `<table>`

An optional child of `<connection-metadata>`, this controls whether the Table selector is shown in the schema viewer. If it is not present, Table does not appear. It has the following XML attributes.

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

![alt text]({{ site.baseurl }}/assets/mcd-schema-viewer-1.png "Schema Viewer with Connection Metadata file")&nbsp;![alt text]({{ site.baseurl }}/assets/mcd-schema-viewer-2.png "Schema Viewer after removing schema element from Connection Metadata file")
