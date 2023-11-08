# Tableau Connector SDK Changelog
## 2023-04-20
### Changed
- Update `oauth_config.xsd` to include `defaultInstanceUrl` field and update `min-version-tableau` to be 2023.3 if present
## 2023-04-10
### Changed
- Update `oauth_config.xsd` to include `configLabel` field and update `min-version-tableau` to be 2023.2 if present
## 2023-04-04
### Changed
- Update `oauth_config.xsd` to include `instanceUrlSuffix` field and update `min-version-tableau` to be 2023.1 if present
## 2022-12-16
### Changed
- Convert database impersonation sample to Connection Dialog V2     
## 2022-11-21
### Changed
- Update `connector_plugin_manifest_latest.xsd` to allow multple `oauth-config` fields and update `min-version-tableau` to be 2021.4 if present
## 2022-11-16
### Changed
- Update `oauth_config.xsd` to include `oauthConfigId` field and update `min-version-tableau` to be 2021.4 if present
## 2021-09-02
### Changed
- Validate max length of `name` in Company-G in `connector_plugin_manifest_latest.xsd`
## 2021-08-23
### Added
- Add language support for French (Canada)
## 2021-01-22
### Removed
- Remove support for `script` element and `cacheSize` attribute in ConnectionNormalizer-CT and ConnectionMatcher-CT in `tdr_latest.xsd`.  This has not been a recommended pattern since initial release and deprecated in 2020.3 release.  Documentation, samples and [API Reference](https://tableau.github.io/connector-plugin-sdk/docs/api-reference) have been previously updated.
## 2021-01-10
### Added
- Add OAuth Scenario for Snowflake
## 2020-10-01
### Added
- Add JDBC Kerberos scenario for postgres

## 2020-09-21
### Changed
- Validate min length of `name` in Company-G in `connector_plugin_manifest_latest.xsd`

## 2020-08-27
### Added
- Add ISO8601 support to postgres_odbc and postgres_jdbc samples

## 2020-08-11
### Added
-  Add `vendor[1,2,3]-prompt` as options to ConnectionConfig-CT in `tcd_latest.xsd`.

## 2020-07-13
### Changed
- Changed sqlite_extract\dialect.xml, make it doesn't inherit from any base dialect

## 2020-07-13
### Added
- Add `PasswordOnly` as an option to AuthMode-CT in `tcd_latest.xsd`.
- Add `Password` as an option to AuthOptionEnum-ST in `tcd_latest.xsd`.


## 2020-06-10
### Added
- Add SQLDialect to samples/components/dialects

## 2020-06-11
### Removed
- Remove `base-types` from tdd samples. Intended functionality is exposed in `<format-column-definition>`

## 2020-06-02
### Changed
- Date functions in dialect examples to have only `<formula part='week'>` for functions with `localstr` as last argument. See [isuue](https://github.com/tableau/connector-plugin-sdk/issues/505) for details

## 2019-12-11
### Added
- New SQLite Extract-Only Sample
- Removed unnecessary attribute from samples
- Fix issue with SSL in the MySQL ODBC sample
### Changed
### Removed
- Removed INITSTMT from MySQL ODBC sample so that intialSQL does not run twice.

## 2019-03-29
### Added
- Brought in changes from internal repository.
- New ISO Date test cases.
### Changed
- Improved error messaging when running TDVT from the wrong directory.
- Improved the generated Diff files.

## 2019-11-22

### Changed
- XSD changes, Change connectionconfig's children could be in random order
