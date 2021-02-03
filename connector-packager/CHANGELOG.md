# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 5/8/2020
- Add support for packaging connectors using connection dialogs v2

## [2.0.0] - 4/7/2020
- Remove option to sign .taco file

## [1.0.0] - 1/10/2020
- Improve command line argument parsing: detect duplicated option -d/--dest
- Update `package.py` to create directory for logs if it does not exist.
- Change wording for -l flag
- Update packaging unit tests to be more descriptive on the command line.
- Enforce https for links in the manifest while packaging

## [0.0.1] - 10-3-2019
Initial release of the Connector Packaging Tool

This release allows for the packaging, signing, and verification of Tableau Connector (`.taco`) files.
