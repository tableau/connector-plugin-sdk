# Tableau Connector Packaging Tool

## Usage

### Install package Module
The recommendation is to install package within a Python virtual environment. See section Setup Virtual Environment below to create and activate a vitural environment.

```
(.venv) PS connector-plugin-sdk\packaging> python setup.py install
```

### Run package Module

```
(.venv) PS connector-plugin-sdk\packaging> python -m package.package
```

## Development

### Select Python Installation
If not installed, download and install Python 3.7 or greater: https://www.python.org/downloads/  Add to PATH or in IDE console.

Example: .vscode\settings.json
```javascript
{
    "python.pythonPath": "~\\AppData\\Local\\Programs\\Python\\Python37-32\\python.exe",
    ...
}
```
### Setup Virtual Environment
[Create]((https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments)) a virtual environment using Python [venv](https://docs.python.org/3/library/venv.html) command. Note: example commands are Windows specific.
```
PS connector-plugin-sdk\packaging> py -3 -m venv .venv
```

Activate the virtual environment.
```
PS connector-plugin-sdk\packaging> .\.venv\Scripts\Activate.ps1
```

Verify python version is greater than 3.7.
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

#### Notes
- https://stackoverflow.com/a/47559925
