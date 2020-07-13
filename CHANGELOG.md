# Tableau Connector SDK Changelog

## Unreleased

### Added
### Changed
### Removed

## 2020-07-13
### Added
- Add `PasswordOnly` as an option to AuthMode-CT in `tcd_latest.xsd`.
- Add `Password` as an option to AuthOptionEnum-ST in `tcd_latest.xsd`.


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
