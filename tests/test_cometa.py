import logging
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from epilepsy_tools import cometa
from epilepsy_tools.cometa._data import (
    extract_acceleration_data,
    extract_emg_data,
)

DATA_SHAPES = [
    (2784802, 32),
    (3617662, 32),
]
TESTS_IMAGES = Path("tests/images")


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        c3d_file_path = Path("tests/c3d_sample/")
        cls.c3d_files = list(c3d_file_path.glob("*.c3d"))


class DataTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.data = cometa.load_data(cls.c3d_files[0])


class TestLoadData(BaseTestCase):
    def test_load_data(self) -> None:
        for i, file in enumerate(self.c3d_files):
            data = cometa.load_data(file)

            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(data.shape, DATA_SHAPES[i])

    def test_load_non_c3d(self) -> None:
        with self.assertRaises(ValueError), tempfile.TemporaryDirectory() as d:
            file = Path(d) / "not_a_c3d.txt"
            with open(file, "w") as f:
                f.write("not valid data")

            cometa.load_data(file)


class TestDownsample(DataTestCase):
    def test_downsample_ratio_2(self) -> None:
        downsampled = cometa.downsample(self.data, ratio=2)

        self.assertEqual(downsampled.shape, (DATA_SHAPES[0][0] // 2, DATA_SHAPES[0][1]))

    def test_downsample_returns(self) -> None:
        downsampled = cometa.downsample(self.data, ratio=2)

        self.assertIsInstance(downsampled, pd.DataFrame)
        self.assertIsNot(downsampled, self.data)


class TestModalitySelection(DataTestCase):
    def test_extract_emg(self) -> None:
        emg = cometa.extract_emg_data(self.data)

        self.assertTrue(
            all(not c.endswith(cometa._data.ACCELERATION_SUFFIXES) for c in emg.columns)
        )
        self.assertEqual(emg.shape, (DATA_SHAPES[0][0], DATA_SHAPES[0][1] // 4))

    def test_extract_acceleration(self) -> None:
        accel = cometa.extract_acceleration_data(self.data)

        self.assertTrue(
            all(c.endswith(cometa._data.ACCELERATION_SUFFIXES) for c in accel.columns)
        )
        self.assertEqual(accel.shape, (DATA_SHAPES[0][0], 3 * DATA_SHAPES[0][1] // 4))


class TestRecordingInfo(DataTestCase):
    def _assert_recording_info(
        self, recording_info: cometa._data.RecordingInfo
    ) -> None:
        self.assertIsInstance(recording_info, cometa._data.RecordingInfo)
        self.assertEqual(recording_info.fs, 2000.0)
        self.assertEqual(recording_info.samples, DATA_SHAPES[0][0])
        self.assertEqual(len(recording_info.channels), DATA_SHAPES[0][1])
        self.assertLess(recording_info.start_time, recording_info.end_time)

    def test_get_recording_info_from_file(self) -> None:
        recording_info = cometa.RecordingInfo.from_file(self.c3d_files[0])

        self._assert_recording_info(recording_info)

    def test_get_recording_info_from_data(self) -> None:
        recording_info = cometa.RecordingInfo.from_data(self.data)

        self._assert_recording_info(recording_info)


class TestPlots(DataTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # remove some matplotlib logging
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        # make sure the directory exists first
        TESTS_IMAGES.mkdir(exist_ok=True)

    def test_plot_emg(self) -> None:
        fig = cometa.plot_emg(self.data)
        self.assertEqual(len(fig.axes), len(extract_emg_data(self.data).columns))
        fig.savefig(TESTS_IMAGES / "test_plot_emg.png")

    def test_plot_emg_select_channels(self) -> None:
        n_emg_channels = 6
        select_channels = cometa.extract_emg_data(self.data).iloc[:, :n_emg_channels]

        fig = cometa.plot_emg(select_channels)
        self.assertEqual(len(fig.axes), n_emg_channels)
        fig.savefig(TESTS_IMAGES / "test_plot_emg_select_channels.png")

    def test_plot_acceleration(self) -> None:
        fig = cometa.plot_acceleration(self.data)
        self.assertEqual(
            len(fig.axes), len(extract_acceleration_data(self.data).columns) // 3
        )
        fig.savefig(TESTS_IMAGES / "test_plot_acceleration.png")

    def test_plot_acceleration_no_norm(self) -> None:
        fig = cometa.plot_acceleration(self.data, norm=False)
        self.assertEqual(
            len(fig.axes), len(extract_acceleration_data(self.data).columns)
        )
        fig.savefig(TESTS_IMAGES / "test_plot_acceleration_no_norm.png")
