# Epilepsy Tools

This repository contains the `epilepsy_tools` Python package, which contains pre-written function to handle data from the various connected wearables used in the epilepsy research lab at CRCHUM.

## Requirements

The package is built with Python 3.10 and newer in mind, and will not work with older versions.
The list of required packages can be found in `requirements.txt`, and ahould be installed automatically when installing with the methods shown below

## Installation

You can install the package from GitHub directly:

With `uv` (recommended):
```sh
# if the project is not initialized already
uv init my-project
cd my-project

uv add git+https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools.git
```

With `pip`:
```sh
pip install git+https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools.git
```

## Documentation

[Documentation can be read here](https://crchum-epilepsy-group.github.io/epilepsy_tools/).

## Quick Example

This is a quick example that loads data from a Cometa file (.c3d)

```py
from epilepsy_tools import cometa

file_path = "some/directory/data.c3d"

data = cometa.load_data(file_path)  # returns a pandas.DataFrame
recording_info = cometa.RecordingInfo.from_data(data)
emg_data = cometa.extract_emg_data(data)  # returns a pandas.DataFrame
```

## Devices

This lists the current devices that have functions implemented for them.

### Cometa

You can import the subpackage for the Cometa data with:
```py
from epilepsy_tools import cometa
```
It uses the [c3d](https://pypi.org/project/c3d/) package internally.

### Hexoskin

You can import the subpackage for the Hexoskin data with:
```py
from epilepsy_tools import hexoskin
```
It uses the [pyEDFlib](https://pypi.org/project/pyEDFlib/) package internally.

## Logging

Enable logging for the module with:

```py
import logging

logger = logging.getLogger("epilepsy_tools")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
```
