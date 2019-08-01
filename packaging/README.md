# Tableau Connector Packaging Tool

## Usage

### Install `package` Module
The recommendation is to install `package` within a Python virtual environment. See section Setup Virtual Environment below to create and activate a virtual environment.

```
(.venv) PS connector-plugin-sdk\packaging> python setup.py install
```

### Run package Module

To package the connector and sign it:
```
(.venv) PS connector-plugin-sdk\packaging> python -m package.package [path_to_folder] -a [alias_name] -ks [keystore_file_path]
```

To package the connector without signing:
```
(.venv) PS connector-plugin-sdk\packaging> python -m package.package [path_to_folder] --package-only
```

To validate that the xml files are valid:
```
(.venv) PS connector-plugin-sdk\packaging> python -m package.package --validate-only [path_to_folder]
```

All command line usage details:
```
usage: package.py [-h] [-v] [-l LOG_PATH] [--validate-only] [-d DEST]
                  [--package-only] [-a ALIAS] [-ks KEYSTORE]
                  input_dir

Tableau Connector Packaging Tool: package connector files into a single Tableau
Connector (.taco) file, and sign it.

positional arguments:
  input_dir             path to directory of connector files to package

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
  -l LOG_PATH, --log LOG_PATH
                        path of logging output
  --validate-only       runs package validation steps only
  -d DEST, --dest DEST  destination folder for packaged connector
  --package-only        package a taco only, skip signing
  -a ALIAS, --alias ALIAS
                        alias identifying the private key to be used to sign
                        taco file
  -ks KEYSTORE, --keystore KEYSTORE
                        location of keystore file where key is stored
```

## Development

### Select Python Installation
The `package` tool is developed against Python 3.7.3, which can be downloaded at https://www.python.org/downloads/. After installation, add Python to your PATH or in IDE console.

Example: .vscode\settings.json
```javascript
{
    "python.pythonPath": "~\\AppData\\Local\\Programs\\Python\\Python37-32\\python.exe",
    ...
}
```
### Setup Virtual Environment
[Create](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) a virtual environment using Python's [venv](https://docs.python.org/3/library/venv.html) command. Note: example commands are Windows specific.
```
PS connector-plugin-sdk\packaging> py -3 -m venv .venv
```

Activate the virtual environment.
```
PS connector-plugin-sdk\packaging> .\.venv\Scripts\activate
```

Verify Python version is 3.7.3 or higher.
```
(.venv) PS connector-plugin-sdk\packaging> python --version
Python 3.7.3
```

For reference, to deactivate the virtual environment in the future.
```
(.venv) PS connector-plugin-sdk\packaging> deactivate
```

### Install package Module For Development
```
(.venv) PS connector-plugin-sdk\packaging> python setup.py develop
```

### Test package Module

```
(.venv) PS connector-plugin-sdk\packaging> python setup.py test
```

### Run package Module

```
(.venv) PS connector-plugin-sdk\packaging> python -m package.package
```
