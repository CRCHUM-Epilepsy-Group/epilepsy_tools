import itertools
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from epilepsy_tools import cometa

DATA_SHAPES = [
    (2784802, 32),
    (3617662, 32),
]


@pytest.fixture
def downsampled_cometa_data(cometa_data: pd.DataFrame) -> pd.DataFrame:
    return cometa.downsample(cometa_data, ratio=2)


@pytest.fixture
def emg_cometa_data(cometa_data: pd.DataFrame) -> pd.DataFrame:
    return cometa.extract_emg_data(cometa_data)


@pytest.fixture
def acceleration_cometa_data(cometa_data: pd.DataFrame) -> pd.DataFrame:
    return cometa.extract_acceleration_data(cometa_data)


@pytest.fixture
def mock_cometa_recordinginfo() -> cometa.RecordingInfo:
    return cometa.RecordingInfo(
        fs=2000.0,
        samples=DATA_SHAPES[0][0],
        channels=list(
            f"{a} {b}".strip()
            for a, b in itertools.product(
                cometa.data.SENSOR_LABELS, ("",) + cometa.data.ACCELERATION_SUFFIXES
            )
        ),
        start_time=datetime.min,
        end_time=datetime.max,
    )


def test_load_data_returns_dataframe(c3d_files: list[Path]) -> None:
    for file in c3d_files:
        data = cometa.load_data(file)

        assert isinstance(data, pd.DataFrame)


def test_load_data_returns_correct_size(c3d_files: list[Path]) -> None:
    for i, file in enumerate(c3d_files):
        data = cometa.load_data(file)

        assert data.shape == DATA_SHAPES[i]


def test_load_data_non_c3d(tmp_path: Path) -> None:
    file = tmp_path / "not_a_c3d.txt"
    file.write_text("not valid data")

    with pytest.raises(ValueError):
        cometa.load_data(file)


def test_downsample_ratio_2(downsampled_cometa_data: pd.DataFrame) -> None:
    assert downsampled_cometa_data.shape == (DATA_SHAPES[0][0] // 2, DATA_SHAPES[0][1])


def test_downsample_returns_dataframe(downsampled_cometa_data: pd.DataFrame) -> None:
    assert isinstance(downsampled_cometa_data, pd.DataFrame)


def test_downsample_does_not_return_same_object(
    cometa_data: pd.DataFrame, downsampled_cometa_data: pd.DataFrame
) -> None:
    assert cometa_data is not downsampled_cometa_data


def test_extract_emg_only_emg(emg_cometa_data: pd.DataFrame) -> None:
    assert all(
        not c.endswith(cometa.data.ACCELERATION_SUFFIXES)
        for c in emg_cometa_data.columns
    )


def test_extract_emg_correct_shape(emg_cometa_data: pd.DataFrame) -> None:
    assert emg_cometa_data.shape == (DATA_SHAPES[0][0], DATA_SHAPES[0][1] // 4)


def test_extract_acceleration_only_acceleration(
    acceleration_cometa_data: pd.DataFrame,
) -> None:
    assert all(
        c.endswith(cometa.data.ACCELERATION_SUFFIXES)
        for c in acceleration_cometa_data.columns
    )


def test_extract_acceleration_corrent_shape(
    acceleration_cometa_data: pd.DataFrame,
) -> None:
    assert acceleration_cometa_data.shape == (
        DATA_SHAPES[0][0],
        3 * DATA_SHAPES[0][1] // 4,
    )


def _recording_info_is_correct(
    recording_info: cometa.RecordingInfo, mock_recording_info: cometa.RecordingInfo
) -> bool:
    assert isinstance(recording_info, cometa.RecordingInfo)
    assert recording_info.fs == mock_recording_info.fs
    assert recording_info.samples == mock_recording_info.samples
    assert set(recording_info.channels) == set(mock_recording_info.channels)
    assert recording_info.start_time < recording_info.end_time

    return True


def test_recording_info_from_file(
    c3d_files: list[Path], mock_cometa_recordinginfo: cometa.RecordingInfo
) -> None:
    recording_info = cometa.RecordingInfo.from_file(c3d_files[0])
    assert _recording_info_is_correct(recording_info, mock_cometa_recordinginfo)


def test_recording_info_from_data(
    cometa_data: pd.DataFrame, mock_cometa_recordinginfo: cometa.RecordingInfo
) -> None:
    recording_info = cometa.RecordingInfo.from_data(cometa_data)
    assert _recording_info_is_correct(recording_info, mock_cometa_recordinginfo)
