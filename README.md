# Epilepsy Tools

This repository contains the `epilepsy_tools` Python package, which contains pre-written function to handle data from the various connected wearables used in the epilepsy research lab at CRCHUM.

## Requirements

The package is built with Python 3.10 and newer in mind, and will not work with older versions.
The list of required packages can be found in `requirements.txt`, and ahould be installed automatically when installing with the methods shown below

## Installation

You can install from the repository directly, with the following command, with [Git](https://git-scm.com/downloads) installed on your computer:
```sh
pip install git+https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools.git
```

You can also clone the repository or download it locally, and run the following command inside the root directory of the project:
```sh
pip install .
```

## Quick Example

This is a quick example that loads data from a Cometa file (.c3d)

```py
from epilepsy_tools import cometa

file_path = "some/directory/data.c3d

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

Functions:

- `cometa.load_data(file)`: Load the data from a .c3d file. Returns a pandas.DataFrame.
- `cometa.downsample(data, ratio)`: Returns a pandas.DataFrame with a lower frequency sampling.
- `cometa.extract_emg_data(data)`: Returns only the EMG data from the provided pandas.DataFrame.
- `cometa.extract_acceleration_data(data)`: Returns only the acceleration data from the provided pandas.DataFrame.
- `cometa.plot_emg(data)`: Plot the EMG data from a Cometa DataFrame.
- `cometa.plot_acceleration(data, *, norm=True)`: Plot the acceleration from a Cometa DataFrame. If norm=True (the default), calculate the norm of the acceleration vectors for each sensors (the X, Y and Z components) and plot that.


Classes:

- `cometa.RecordingInfo`: Metadata for a recording. Construct with `cometa.RecordingInfo.from_file` or `cometa.RecordingInfo.from_data`.

Constants:

- `cometa.SENSOR_LABELS`: A list of labels for the sensors currently used.

### Hexoskin

You can import the subpackage for the Hexoskin data with:
```py
from epilepsy_tools import hexoskin
```
It uses the [pyEDFlib](https://pypi.org/project/pyEDFlib/) package internally.

Functions:

- `hexoskin.load_data(file, *, as_dataframe=True)`: Load the data from a .edf file. Returns a pandas.DataFrame if `as_dataframe` is set to True (the default) or a dict of pandas.Series if set to False.

Classes:

- `hexoskin.RecordingInfo`: Metadata for a recording. Construct with `hexoskin.RecordingInfo.from_file`.

## Logging

Enable logging for the module with:

```py
import logging

logging.getLogger("epilepsy_tools").setLevel(logging.DEBUG)
```
