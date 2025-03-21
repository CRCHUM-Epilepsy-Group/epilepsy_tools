from __future__ import annotations

import logging
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import c3d
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", module="c3d.c3d")

__all__ = [
    "SENSOR_LABELS",
    "RecordingInfo",
    "downsample",
    "extract_emg_data",
    "extract_acceleration_data",
    "load_data",
]

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from os import PathLike

DATETIME_FORMAT = "%d-%b-%Y %H:%M:%S.%f"
SENSOR_LABELS = (  # these might need modifications if sensors are edited
    "L.Upper Trap.",
    "R.Upper Trap.",
    "L.Ant.Deltoid",
    "R.Ant.Deltoid",
    "L.Biceps Br.",
    "R.Biceps Br.",
    "L.Tib.Ant.",
    "R.Tib.Ant.",
)
ACCELERATION_SUFFIXES = (":X", ":Y", ":Z")


class RecordingInfo:
    """Stores metadata of the recording (raw signals).
    Construct with `RecordingInfo.from_file` or `RecordingInfo.from_data`.

    Attributes
    ----------
    fs : float
        Original sampling frequency in Hz (before downsampling).
    samples : int
        Total number of data points.
    channels : list[str]
        List of channel labels.
    start_time : datetime.datetime
        Start date and time of recording.
    end_time : datetime.datetime
        End date and time of recording.
    duration : datetime.timedelta
        Duration of recording.
    """

    def __init__(self, data: pd.DataFrame):
        time: Sequence[datetime] = data.index  # type: ignore
        period = (time[1] - time[0]).total_seconds()

        self.fs: float = 1 / period
        self.samples: int = len(data)
        self.channels: list[str] = list(data.columns)
        self.start_time: datetime = time[0]
        self.end_time: datetime = time[-1]
        self.duration: timedelta = self.end_time - self.start_time

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(fs={self.fs}, samples={self.samples}, "
            f"channels={self.channels}, start_time={self.start_time}, "
            f"end_time={self.end_time})"
        )

    @classmethod
    def from_file(cls, file: str | PathLike) -> RecordingInfo:
        """Get the recording info of a given .c3d file.

        Parameters
        ----------
        file : str | PathLike
            Path of the .c3d file.

        Returns
        -------
        RecordingInfo
            The information of the recording.
        """
        data = load_data(file)
        return cls(data)

    @classmethod
    def from_data(cls, data: pd.DataFrame) -> RecordingInfo:
        """Get the recording info of data already loaded.
        This is equivalent to instanciating the class directly.

        Parameters
        ----------
        data : pandas.DataFrame
            The Cometa data loaded from `cometa.load_data`.

        Returns
        -------
        RecordingInfo
            The information of the recording.
        """
        return cls(data)


def generate_timestamps(
    c3d_filepath: str | PathLike, time: Sequence[float]
) -> pd.DatetimeIndex:
    """Generate the timestamps for the given .c3d file, since it does not contain
    the information already.
    This is based on the last modification time of the file, the time between
    data points, and the length of the recording.

    Parameters
    ----------
    c3d_filepath : str | PathLike
        Path of the .c3d file.
    time : Sequence[float]
        A sequence of the time elapsed since the beginning of the recordinf in seconds.

    Returns
    -------
    timestamps : pandas.DatetimeIndex
        A pandas.Index instance of datetime.datetime objects.
    """
    _log.debug("Retrieving recording information...")

    # Get period
    T = time[1] - time[0]

    # Get duration
    dur = (len(time) - 1) * T

    # Get the last modification datetime of the c3d file
    file = Path(c3d_filepath)  # make sure it is a Path instance
    dt_mod = file.stat().st_mtime
    time_stopped = datetime.fromtimestamp(dt_mod)

    # Calculate the time at which the recording started
    time_started = time_stopped - timedelta(seconds=dur)

    _log.debug(f"Recording started at {time_started}")
    _log.debug(f"Recording stopped at {time_stopped}")
    _log.debug(f"Recording duration is {dur} seconds")
    _log.debug(f"Sample frequency is {1 / T} Hz")

    # Generate timestamp for each datapoint
    _log.debug("Generating timestamps...")
    timestamps = pd.date_range(
        start=time_started,
        periods=len(time),
        freq=timedelta(seconds=T),
    )
    timestamps.name = "Timestamps"
    _log.debug("Success!")

    return timestamps


def downsample(data: pd.DataFrame, *, ratio: int) -> pd.DataFrame:
    """Downsample the data to every `ratio` values.
    ratio=2 means keep half of the data, 3 keep only the third.

    Parameters
    ----------
    data : pandas.DataFrame
        The Cometa data loaded from `cometa.load_data`.
    ratio : int
        The ratio of the data to keep. 2 means keep half of the data (1/2),
        3 means keep only one value every three (1/3).

    Returns
    -------
    pandas.DataFrame
        The downsampled DataFrame
    """
    downsampled_data = data.iloc[::ratio, :].copy()
    return downsampled_data


def extract_emg_data(data: pd.DataFrame) -> pd.DataFrame:
    """Take the DataFrame returned by `load_data` and keep only the columns
    containing the EMG data.

    Parameters
    ----------
    data : pandas.DataFrame
        The Cometa data loaded from `cometa.load_data`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with only the EMG data.
    """
    emg_cols = [c for c in data.columns if not c.endswith(ACCELERATION_SUFFIXES)]
    return data[emg_cols]


def extract_acceleration_data(data: pd.DataFrame) -> pd.DataFrame:
    """Take the DataFrame returned by `load_data` and keep only the columns
    containing the acceleration data.

    Parameters
    ----------
    data : pandas.DataFrame
        The Cometa data loaded from `cometa.load_data`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with only the acceleration data.
    """
    accel_cols = [c for c in data.columns if c.endswith(ACCELERATION_SUFFIXES)]
    return data[accel_cols]


def load_data(file: str | PathLike) -> pd.DataFrame:
    """Read a .c3d file from the Cometa device.
    Depending on how many sensors were installed and which modality was recorded,
    the shape of the DataFrame might be different.

    Parameters
    ----------
    file : str | PathLike
        Path of the .c3d file.

    Returns
    -------
    pandas.DataFrame
        The data inside the .c3d file.

    Raises
    ------
    ValueError
        The file provided is not a .c3d file.
    """
    _log.debug(f"reading file {file}")
    if Path(file).suffix.lower() != ".c3d":
        raise ValueError(f"{file} is not a .c3d file")

    with open(file, "rb") as c3dfile:
        frames = c3d.Reader(c3dfile)
        analog_samples = []
        for i, points, analog in frames.read_frames():
            analog_transposed = np.array(analog).T
            analog_samples.append(analog_transposed)

    # Concatenate the samples stored in frames
    all_analog_samples = np.concatenate(analog_samples, axis=0)

    # Convert to dataframe
    data = pd.DataFrame(all_analog_samples, columns=frames.analog_labels)
    data.columns = data.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    # Remove zero-padding
    data = data.apply(lambda x: np.trim_zeros(x, "b"), axis=0)  # 'b' to trim from back

    # Generate time axis (units = seconds) as in EMG and Motion Tools software
    T = 1 / frames.analog_rate  # period in seconds
    dur = (len(data) - 1) * T  # duration in seconds
    time = np.linspace(0.0, dur, num=len(data), dtype=float)

    # Generate timestamps
    timestamps = generate_timestamps(file, time)  # type: ignore
    data.index = timestamps
    data.index = pd.to_datetime(data.index, format=DATETIME_FORMAT)

    # drop NaNs to be coherent with Cometa software
    data.fillna(0)

    return data
