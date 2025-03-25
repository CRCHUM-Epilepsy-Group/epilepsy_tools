from pathlib import Path

import pandas as pd
import pytest

from epilepsy_tools import cometa


@pytest.fixture(scope="session")
def tests_images_directory() -> Path:
    directory = Path("tests/images")
    directory.mkdir(exist_ok=True)
    return directory


def test_plot_emg(cometa_data: pd.DataFrame, tests_images_directory: Path) -> None:
    fig = cometa.plot_emg(cometa_data)
    assert len(fig.axes) == len(cometa.extract_emg_data(cometa_data).columns)
    fig.savefig(tests_images_directory / "test_plot_emg.png")


def test_plot_emg_select_channels(
    cometa_data: pd.DataFrame, tests_images_directory: Path
) -> None:
    n_emg_channels = 6
    select_channels = cometa.extract_emg_data(cometa_data).iloc[:, :n_emg_channels]

    fig = cometa.plot_emg(select_channels)
    assert len(fig.axes) == n_emg_channels
    fig.savefig(tests_images_directory / "test_plot_emg_select_channels.png")


def test_plot_acceleration(
    cometa_data: pd.DataFrame, tests_images_directory: Path
) -> None:
    fig = cometa.plot_acceleration(cometa_data)
    assert (
        len(fig.axes) == len(cometa.extract_acceleration_data(cometa_data).columns) // 3
    )
    fig.savefig(tests_images_directory / "test_plot_acceleration.png")


def test_plot_acceleration_no_norm(
    cometa_data: pd.DataFrame, tests_images_directory: Path
) -> None:
    fig = cometa.plot_acceleration(cometa_data, norm=False)
    assert len(fig.axes) == len(cometa.extract_acceleration_data(cometa_data).columns)
    fig.savefig(tests_images_directory / "test_plot_acceleration_no_norm.png")
