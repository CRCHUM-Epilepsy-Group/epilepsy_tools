from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, overload

import numpy as np
import pandas as pd
import pyedflib

if TYPE_CHECKING:
    from os import PathLike
    from typing import Literal, TypedDict

    SignalHeaderDict = TypedDict(
        "SignalHeaderDict", {"label": str, "sample_frequency": float, "dimension": str}
    )
    HeaderDict = TypedDict(
        "HeaderDict",
        {
            "patientname": str,
            "sex": str,
            "startdate": datetime,
            "birthdate": str,
            "recording_additional": str,
            "patient_additional": str,
        },
    )


__all__ = [
    "RecordingInfo",
    "load_data",
]

_log = logging.getLogger(__name__)


@dataclass
class SignalHeader:
    """Stores information of a signal (or channel).

    Attributes
    ----------
    label : str
        The label of the signal.
    sample_rate : float
        The sample rate in Hz of the signal.
    dimension : str
        The units of the signal.
    """

    label: str
    sample_rate: float
    dimension: str


@dataclass
class RecordingInfo:
    """Stores metadata of the recording (raw signals).
    Construct with `RecordingInfo.from_file`.

    Attributes
    ----------
    patient_name : str
        The name of the patient of the recording.
    sex : str
        The sex of the patient of the recording.
    start_time : datetime.datetime
        The date and time the recording started.
    birth_date : datetime.date
        The birth date of the patient of the recording.
    hexoskin_record_id : int
        The ID on Hexoskin's platform of the recording.
    hexoskin_user_id : int
        The ID on Hexoskin's platform of the patient of the recording.
    signals : list[SignalHeader]
        The list of signals (channels) in the recording.
    """

    patient_name: str
    sex: str
    start_time: datetime
    birth_date: date
    hexoskin_record_id: int
    hexoskin_user_id: int
    signals: list[SignalHeader]

    @classmethod
    def from_file(cls, file: str | PathLike) -> RecordingInfo:
        """Get the recording info of a given .edf file or data already loaded.

        Parameters
        ----------
        file : str | PathLike
            Path of the .edf file.

        Returns
        -------
        RecordingInfo
            The information of the recording.
        """

        with pyedflib.EdfReader(str(file)) as reader:
            signal_headers: list[SignalHeaderDict] = reader.getSignalHeaders()  # type: ignore
            header: HeaderDict = reader.getHeader()  # type: ignore

        signals = [
            SignalHeader(
                label=_parse_label(signal_header["label"]),
                sample_rate=signal_header["sample_frequency"],
                dimension=signal_header["dimension"],
            )
            for signal_header in signal_headers
        ]

        return RecordingInfo(
            patient_name=header["patientname"].replace(" ", ""),
            sex=header["sex"],
            start_time=header["startdate"],
            birth_date=datetime.strptime(header["birthdate"], "%d %b %Y").date(),
            hexoskin_record_id=int(
                header["recording_additional"].removeprefix("hexoskin_record_id=")
            ),
            hexoskin_user_id=int(
                header["patient_additional"].removeprefix("hexoskin_user_id=")
            ),
            signals=signals,
        )


def _parse_label(label: str) -> str:
    """Extract the name of the channel from the label.
    Labels have a format of <ID:Name>, so re discard the ID: part.

    Parameters
    ----------
    label : str
        The label of the channel.

    Returns
    -------
    str
        The Name part of the original label.
    """
    return label[label.index(":") + 1 :]


def generate_timestamps(
    start_time: datetime, sample_rate: float, length: int
) -> pd.DatetimeIndex:
    """Generate the timestamps for the given parameters. To be used as the
    index of a DataFrame.

    Parameters
    ----------
    start_time : datetime.datetime
        The datetime to start the timestamps from.
    sample_rate : float
        The number of points per seconds to generate (in hertz).
    length : int
        The total number of points to generate.

    Returns
    -------
    timestamps : pandas.DatetimeIndex
        A pandas.Index instance of datetime.datetime objects.
    """
    timestamps = pd.date_range(
        start=start_time,
        freq=timedelta(seconds=1 / sample_rate),
        periods=length,
    )
    timestamps.name = "Timestamps"

    return timestamps


@overload
def load_data(
    file: str | PathLike, *, as_dataframe: Literal[True] = ...
) -> pd.DataFrame: ...


@overload
def load_data(
    file: str | PathLike, *, as_dataframe: Literal[False]
) -> dict[str, pd.Series[float]]: ...


def load_data(
    file: str | PathLike, *, as_dataframe: bool = True
) -> pd.DataFrame | dict[str, pd.Series[float]]:
    """Read a .edf file from the Hexoskin device.

    Since not every metric is read with the same sampling rate on the device,
    you can load the data as a DataFrame with `as_dataframe=True` (the default)
    that will contain NaNs for metrics with lower sample rates, or as a dict of
    Series with `as_dataframe=False`, what will not contain NaNs but will all be
    of different length.

    In the case of a DataFrame with NaNs, you can fill out the missing values
    with the method `DataFrame.ffill` that will use the last non-NaN value to
    fill the DataFrame.

    Parameters
    ----------
    file : str | PathLike
        Path of the .edf file.
    as_dataframe : bool, optional
        If the data should be returned in a DataFrame or not (if False, a dict of
        Series is returned instead), by default True.

    Returns
    -------
    data : pandas.DataFrame | dict[str, pandas.Series[float]]
        The data inside the .edf file.

    Raises
    ------
    ValueError
        The file provided is not a .edf file.
    """
    _log.debug(f"reading file {file}")
    if Path(file).suffix.lower() != ".edf":
        raise ValueError(f"{file} is not a .edf file")

    # make sure file is a str for pyedflib
    signals, signal_headers, header = pyedflib.highlevel.read_edf(str(file))

    # get the base timestamps
    max_sample_rate = max(
        signal_header["sample_frequency"] for signal_header in signal_headers
    )
    max_length = max(len(signal) for signal in signals)
    timestamps = generate_timestamps(
        start_time=header["startdate"],
        sample_rate=max_sample_rate,
        length=max_length,
    )
    _log.debug(
        f"Generated timetamps for freq={max_sample_rate} Hz, length={max_length}."
    )

    data = pd.DataFrame(index=timestamps)
    for signal, signal_header in zip(signals, signal_headers):
        metric_data = np.full(max_length, fill_value=np.nan)
        metric_data[:: int(max_sample_rate / signal_header["sample_frequency"])] = (
            signal
        )
        data[_parse_label(signal_header["label"])] = metric_data

    if not as_dataframe:
        _log.debug("Returning data in a dict of pandas.Series.")
        return {col: data[col].dropna() for col in data.columns}
    else:
        _log.debug("Returning data in a pandas.DataFrame.")
        return data
