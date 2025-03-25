from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pyedflib
import pytest

from epilepsy_tools import hexoskin
from epilepsy_tools.hexoskin import RecordingInfo

DATA_SHAPES = [
    (5736960, 20),
    (13545472, 20),
]

if TYPE_CHECKING:
    from typing import TypeAlias

    HX_DICT: TypeAlias = dict[str, pd.Series[float]]


@pytest.fixture(scope="module")
def edf_files() -> list[Path]:
    edf_file_path = Path("tests/edf_sample/")
    return list(edf_file_path.glob("*.edf"))


@pytest.fixture(scope="module")
def hexoskin_data_default(edf_files: list[Path]) -> list[pd.DataFrame]:
    return [hexoskin.load_data(file) for file in edf_files]


@pytest.fixture(scope="module")
def hexoskin_data_explicit(edf_files: list[Path]) -> list[pd.DataFrame]:
    return [hexoskin.load_data(file, as_dataframe=True) for file in edf_files]


@pytest.fixture(scope="module")
def hexoskin_data_dict(
    edf_files: list[Path],
) -> list[HX_DICT]:
    return [hexoskin.load_data(file, as_dataframe=False) for file in edf_files]


@pytest.fixture(scope="module")
def hexoskin_recording_info(edf_files: list[Path]) -> list[RecordingInfo]:
    return [RecordingInfo.from_file(file) for file in edf_files]


def test_load_data_as_dataframe_default_returns_dataframe(
    hexoskin_data_default: list[pd.DataFrame],
) -> None:
    for data in hexoskin_data_default:
        assert isinstance(data, pd.DataFrame)


def test_load_data_as_dataframe_default_returns_correct_shape(
    hexoskin_data_default: list[pd.DataFrame],
) -> None:
    for i, data in enumerate(hexoskin_data_default):
        assert data.shape == DATA_SHAPES[i]


def test_load_data_as_dataframe_explicit_returns_dataframe(
    hexoskin_data_explicit: list[pd.DataFrame],
) -> None:
    for data in hexoskin_data_explicit:
        assert isinstance(data, pd.DataFrame)


def test_load_data_as_dataframe_explicit_returns_correct_shape(
    hexoskin_data_explicit: list[pd.DataFrame],
) -> None:
    for i, data in enumerate(hexoskin_data_explicit):
        assert data.shape == DATA_SHAPES[i]


def test_load_data_as_dataframe_false_returns_dict(
    hexoskin_data_dict: list[HX_DICT],
) -> None:
    for data in hexoskin_data_dict:
        assert isinstance(data, dict)


def test_load_data_as_dataframe_false_has_series(
    hexoskin_data_dict: list[HX_DICT],
) -> None:
    for data in hexoskin_data_dict:
        for signal in data.values():
            assert isinstance(signal, pd.Series)


def test_load_data_as_dataframe_false_returns_correct_shape(
    hexoskin_data_dict: list[HX_DICT],
) -> None:
    for i, data in enumerate(hexoskin_data_dict):
        shape = (max(len(signal) for signal in data.values()), len(data))
        assert shape == DATA_SHAPES[i]


def test_load_non_edf(tmp_path: Path) -> None:
    file = tmp_path / "not_an_edf.txt"
    file.write_text("not valid data")

    with pytest.raises(ValueError):
        hexoskin.load_data(file)


def test_load_data_correct_nan(
    edf_files: list[Path], hexoskin_data_default: list[pd.DataFrame]
) -> None:
    signals, signal_headers, _ = pyedflib.highlevel.read_edf(str(edf_files[0]))
    data = hexoskin_data_default[0]

    for signal, signal_header in zip(signals, signal_headers):
        label = hexoskin.data._parse_label(signal_header["label"])
        non_nan_data = data[label].dropna()

        assert list(signal) == list(non_nan_data)


def test_recording_info_type(hexoskin_recording_info: list[RecordingInfo]) -> None:
    for recording_info in hexoskin_recording_info:
        assert isinstance(recording_info, RecordingInfo)


@pytest.mark.parametrize(
    ["attribute", "expected_type"],
    [
        ("patient_name", str),
        ("sex", str),
        ("start_time", datetime),
        ("birth_date", date),
        ("hexoskin_record_id", int),
        ("hexoskin_user_id", int),
        ("signals", list),
    ],
)
def test_recording_info_attribute_type(
    attribute: str, expected_type: type, hexoskin_recording_info: list[RecordingInfo]
) -> None:
    for recording_info in hexoskin_recording_info:
        assert isinstance(getattr(recording_info, attribute), expected_type)


def test_recording_info_signals_type(
    hexoskin_recording_info: list[RecordingInfo],
) -> None:
    for recording_info in hexoskin_recording_info:
        for signal in recording_info.signals:
            assert isinstance(signal, hexoskin.SignalHeader)


@pytest.mark.parametrize(
    ["attribute", "expected_type"],
    [
        ("dimension", str),
        ("label", str),
        ("sample_rate", float),
    ],
)
def test_recording_info_signals_attribute_type(
    attribute: str, expected_type: type, hexoskin_recording_info: list[RecordingInfo]
) -> None:
    for recording_info in hexoskin_recording_info:
        for signal in recording_info.signals:
            assert isinstance(getattr(signal, attribute), expected_type)
