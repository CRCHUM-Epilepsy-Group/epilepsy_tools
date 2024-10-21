import logging
import unittest
from pathlib import Path

import pandas as pd

from epilepsy_tools import cometa

_log = logging.getLogger("epilepsy_tools")
_log.setLevel(logging.INFO)

DATA_SHAPES = [
    (2573432, 32),
    (2784802, 32),
]


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        c3d_file_path = Path("tests/c3d_sample/")
        self.c3d_files = list(c3d_file_path.glob("*.c3d"))


class DataTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data = cometa.load_data(self.c3d_files[0])


class TestLoadData(BaseTestCase):
    def test_load_data(self) -> None:
        for i, file in enumerate(self.c3d_files):
            data = cometa.load_data(file)

            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(data.shape, DATA_SHAPES[i])


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


class TestOriginalRecordingInfo(DataTestCase):
    def _assert_recording_info(
        self, recording_info: cometa._data.OriginalRecordingInfo
    ) -> None:
        self.assertIsInstance(recording_info, cometa._data.OriginalRecordingInfo)
        self.assertEqual(recording_info.fs, 2000.0)
        self.assertEqual(recording_info.samples, DATA_SHAPES[0][0])
        self.assertEqual(len(recording_info.channels), DATA_SHAPES[0][1])
        self.assertLess(recording_info.start_time, recording_info.end_time)

    def test_get_recording_info_from_file(self) -> None:
        recording_info = cometa.get_record_info(file=self.c3d_files[0])

        self._assert_recording_info(recording_info)

    def test_get_recording_info_from_data(self) -> None:
        recording_info = cometa.get_record_info(data=self.data)

        self._assert_recording_info(recording_info)

    def test_get_recording_info_no_arguments(self) -> None:
        with self.assertRaises(ValueError):
            cometa.get_record_info()

    def test_get_recording_info_both_arguments(self) -> None:
        with self.assertRaises(ValueError):
            cometa.get_record_info(file="not/a/real/file.c3d", data=pd.DataFrame())
