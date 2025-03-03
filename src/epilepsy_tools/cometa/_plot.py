from __future__ import annotations

import itertools
import logging
import re
from typing import TYPE_CHECKING

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from ._data import SENSOR_LABELS, extract_acceleration_data, extract_emg_data

__all__ = [
    "plot_emg",
    "plot_acceleration",
]

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from datetime import datetime

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

COMETA_COLORS = {
    sensor: color
    for sensor, color in zip(
        SENSOR_LABELS,
        [
            "firebrick",
            "darkorange",
            "goldenrod",
            "seagreen",
            "lightseagreen",
            "mediumblue",
            "darkorchid",
            "sienna",
        ],
    )
}


def _clean_sensor_label(sensor_label: str) -> str:
    """Remove the coordinate prefix of the sensor labels, if present.

    Parameters
    ----------
    sensor_label : str
        The label for the sensor.

    Returns
    -------
    clean_label: str
        The label without the coordinate prefix.
    """
    return re.sub(r"\s\:(X|Y|Z)", "", sensor_label)


def _make_stacked_figure(data: pd.DataFrame) -> tuple[Figure, list[Axes]]:
    """Create a figure of every column in the data, each on their own Axes,
    stacked vertically.

    Parameters
    ----------
    data : `pandas.DataFrame`
        The Cometa data loaded from `cometa.load_data`, with possibly selected
        columns.

    Returns
    -------
    fig : `~matplotlib.figure.Figure`
        The Figure containing the plot.
    axes : `list[~matplotlib.axes.Axes]`
        A list of Axes from the Figure.
    """
    nrows = len(data.columns)

    fig, _axes = plt.subplots(
        nrows=nrows,
        sharex=True,
        sharey=True,
        figsize=(15, nrows),
        squeeze=False,
    )

    axes: list[Axes] = list(_axes.flatten())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    axes[-1].set_xlabel("Time (HH:MM:SS)")

    for sensor, ax in zip(data.columns, axes):
        sensor_clean = _clean_sensor_label(sensor)
        _log.debug(sensor_clean)
        ax.margins(x=0)
        ax.plot(data[sensor], color=COMETA_COLORS[sensor_clean])
        ax.set_ylabel(sensor, rotation=0, labelpad=40)

    recording_start: datetime = data.index[0]
    recording_end: datetime = data.index[-1]

    y_date = -0.4
    fig.text(
        0,
        y_date,
        recording_start.strftime("%d-%b-%Y"),
        ha="left",
        va="top",
        transform=axes[-1].transAxes,
    )
    fig.text(
        1,
        y_date,
        recording_end.strftime("%d-%b-%Y"),
        ha="right",
        va="top",
        transform=axes[-1].transAxes,
    )

    return fig, axes


def _acceleration_norm(data: pd.DataFrame) -> pd.DataFrame:
    """Compute the norm of the acceleration of the different sensors.

    Parameters
    ----------
    data : `pandas.DataFrame`
        The Cometa data loaded from `cometa.load_data`, with possibly selected
        columns.

    Returns
    -------
    vector_norm: `pandas.DataFrame`
        A DataFrame with the vector norm of every sensor.
    """
    vector_norm = pd.DataFrame()
    for key, group in itertools.groupby(
        sorted(
            data.columns,
            key=lambda s: SENSOR_LABELS.index(_clean_sensor_label(s)),
        ),
        key=_clean_sensor_label,
    ):
        vector_norm[key] = np.sqrt(np.square(data[list(group)]).sum(axis=1))

    return vector_norm


def plot_emg(data: pd.DataFrame) -> Figure:
    """Plot the EMG data from a Cometa DataFrame.

    Parameters
    ----------
    data : `pandas.DataFrame`
        The Cometa data loaded from `cometa.load_data`.

    Returns
    -------
    fig : Figure
        The Figure with the data plotted.
    """
    # make sure only the EMG data is present
    emg_data = extract_emg_data(data)

    fig, _ = _make_stacked_figure(emg_data)
    fig.suptitle("EMG Data ($\\mu$V)")

    fig.tight_layout()

    return fig


def plot_acceleration(data: pd.DataFrame, *, norm: bool = True) -> Figure:
    """Plot the acceleration from a Cometa DataFrame.
    If norm=True (the default), calculate the norm of the acceleration vectors
    for each sensors (the X, Y and Z components) and plot that.

    Parameters
    ----------
    data : `pandas.DataFrame`
        The Cometa data loaded from `cometa.load_data`.
    norm : bool, optional
        If we should compute the norm of the acceleration vectors from
        components, by default True.

    Returns
    -------
    fig : Figure
        The Figure with the data plotted.
    """
    # make sure only the acceleration data is present
    acceleration_data = extract_acceleration_data(data)

    if norm:
        acceleration_data = _acceleration_norm(acceleration_data)
        fig, _ = _make_stacked_figure(acceleration_data)

    else:
        nrows = len(acceleration_data.columns) // 3
        fig, axes = plt.subplots(
            figsize=(15, nrows),
            ncols=3,
            nrows=nrows,
            sharey=True,
            sharex=True,
        )

        for n, sensor in enumerate(acceleration_data.columns):
            i, j = divmod(n, 3)
            clean_sensor = _clean_sensor_label(sensor)
            if i == 0:
                axes[i, j].set_title(sensor[-1])

            if j == 0:
                axes[i, j].set_ylabel(clean_sensor, rotation=0, labelpad=40)

            if i == len(acceleration_data.columns) // 3 - 1:
                axes[i, j].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                axes[i, j].set_xlabel("Time (HH:MM:SS)")

            axes[i, j].margins(x=0)
            axes[i, j].plot(
                acceleration_data[sensor], color=COMETA_COLORS[clean_sensor]
            )

        recording_start: datetime = acceleration_data.index[0]
        recording_end: datetime = acceleration_data.index[-1]

        y_date = -0.4
        fig.text(
            0,
            y_date,
            recording_start.strftime("%d-%b-%Y"),
            ha="left",
            va="top",
            transform=axes[-1, 0].transAxes,
        )
        fig.text(
            1,
            y_date,
            recording_end.strftime("%d-%b-%Y"),
            ha="right",
            va="top",
            transform=axes[-1, -1].transAxes,
        )

    fig.suptitle("Acceleration Data (g)")

    fig.tight_layout()

    return fig
