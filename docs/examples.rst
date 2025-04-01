Examples
========

Cometa
------

How to load the ``cometa`` package and start loading data:

.. code-block:: python

    from epilepsy_tools import cometa
    import pandas as pd

    # you can (and probably should) use a pathlib.Path object
    data: pd.DataFrame = cometa.load_data("path/to/cometa_data.c3d")

    # keep only the acceleration data (similar for emg data)
    acceleration_data: pd.DataFrame = cometa.extract_acceleration_data(data)

How to get the recordings metadata with the ``cometa.RecordingInfo`` object:

.. code-block:: python

    # get information about a recording
    recording_info = cometa.RecordingInfo.from_file("path/to/cometa_data.c3d")

    # and then print out some information
    print(recording_info.fs)  # original sampling frequency in Hz
    print(recording_info.channels)  # list of channel labels
    print(recording_info.start_time, recording_info.end_time)  # datetime objects


You can also easily create plots of the data, for quick visualization:

.. code-block:: python

    import matplotlib.pyplot as plt

    data: pd.DataFrame = cometa.load_data("path/to/cometa_data.c3d")

    # plot acceleration data from all channels (similar for emg data)
    fig = cometa.plot_acceleration(data)
    plt.show()  # or fig.savefig("figure_name.png") if you want to save

Hexoskin
--------

How to load the ``hexoskin`` package and start loading data:

.. code-block:: python

    from epilepsy_tools import hexoskin
    import pandas as pd

    # you can (and probably should) use a pathlib.Path object
    data: pd.DataFrame = hexoskin.load_data("path/to/hexoskin_data.edf")

The data in a :class:`~pandas.DataFrame` format will contain NaNs.
To work around that you have two choices:

.. code-block:: python

    # Fill the DatFrame with values, removing the NaNs but creating repetition
    data: pd.DataFrame = data.ffill()

    # OR

    # load the data initially as a dict of Series, which will all be of different length
    data: dict[str, pd.Series] = hexoskin.load_data("path/to/hexoskin_data.edf", as_dataframe=False)

How to get the recordings metadata with the ``hexoskin.RecordingInfo`` object:

.. code-block:: python

    # get information about a recording
    recording_info = hexoskin.RecordingInfo.from_file("path/to/hexoskin_data.edf")

    # and then print out some information
    print(recording_info.patient_name)
    print(recording_info. start_time)
    for signal in recording_info.signals:
        # print information on the SignalHeader objects
        print(signal.label, signal.sample_rate)
