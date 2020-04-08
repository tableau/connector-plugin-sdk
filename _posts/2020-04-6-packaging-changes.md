---
title:  "Major Changes to Packaging Tool and Signing Taco Files"
abstract: "The packaging tool no longer signs the .taco files in favor of the user calling jarsigner directly"
---

In Tableau 2019.4, we introduced a python-based packaging tool that packages your connector into a single file we call a `.taco`. Packaging your connector into a single `.taco` file allows you to easily distribute and share your connector, and end users can install these connectors by simply dropping them into their "My Tableau Repository/Connectors" folder. (More information about `.taco` files can be found [here](https://tableau.github.io/connector-plugin-sdk/docs/run-taco).) One of the requirements for `.taco` files to be loaded into Tableau is that they are signed by a trusted certificate authority, so that customers can be confidant of the authenticity and integrity of the `.taco` file.

Before, our packaging tool would sign the connector by calling jarsigner (`.taco` files are actually `.jar` files with a different file extension). However, many of the people signing their `.taco` file have had trouble with the limited options the packaging tool has for signing, and instead called jarsigner themselves. This meant we had two paths to support - signing the `.taco` with our packager, and signing it with jarsigner.

We've pushed a change to the packaging tool that removes the option to sign `.taco` files as part of the packaging process. This means that everyone will need to use jarsigner directly to sign their `.taco` files using the same methods you'd use to sign any other `.jar` file. We decided on this action since creating an  interface for the packager to cover every possible jarsigner option would become unwieldy, especially for a tool whose primary purpose was to package the connector. It also future proofs the signing process in case jarsigner itself changes its interface.

We've also overhauled the [documentation around packaging and signing](https://tableau.github.io/connector-plugin-sdk/docs/package-sign) in order to cover the new changes, as well as smooth over some rough edges in the packaging and signing process.

We hope these changes make it simpler to to sign your connector. If you have any trouble, please look over our documentation or open an issue on our github page.