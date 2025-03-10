import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pyedflib

from epilepsy_tools import hexoskin

DATA_SHAPES = [
    (5736960, 20),
    (13545472, 20),
]


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        edf_file_path = Path("tests/edf_sample/")
        self.edf_files = list(edf_file_path.glob("*.edf"))


class DataTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data = hexoskin.load_data(self.edf_files[0])


class TestLoadData(BaseTestCase):
    def test_as_dataframe_default(self) -> None:
        for i, file in enumerate(self.edf_files):
            data = hexoskin.load_data(file)

            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(data.shape, DATA_SHAPES[i])

    def test_as_dataframe_explicit(self) -> None:
        for i, file in enumerate(self.edf_files):
            data = hexoskin.load_data(file, as_dataframe=True)

            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(data.shape, DATA_SHAPES[i])

    def test_as_dataframe_false(self) -> None:
        for i, file in enumerate(self.edf_files):
            data = hexoskin.load_data(file, as_dataframe=False)

            self.assertIsInstance(data, dict)
            for signal in data.values():
                self.assertIsInstance(signal, pd.Series)
            self.assertEqual(len(data), DATA_SHAPES[i][1])
            self.assertEqual(
                max(len(signal) for signal in data.values()), DATA_SHAPES[i][0]
            )

    def test_load_non_c3d(self) -> None:
        with self.assertRaises(ValueError), tempfile.TemporaryDirectory() as d:
            file = Path(d) / "not_a_c3d.txt"
            with open(file, "w") as f:
                f.write("not valid data")

            hexoskin.load_data(file)

    def test_load_data_correct_nan(self) -> None:
        signals, signal_headers, _ = pyedflib.highlevel.read_edf(str(self.edf_files[0]))
        data = hexoskin.load_data(self.edf_files[0])

        for signal, signal_header in zip(signals, signal_headers):
            label = hexoskin.data._parse_label(signal_header["label"])
            non_nan_data = data[label].dropna()
            self.assertEqual(len(signal), len(non_nan_data))
            self.assertListEqual(list(signal), list(non_nan_data))


class TestRecordingInfo(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recording_info = hexoskin.RecordingInfo.from_file(self.edf_files[0])

    def test_get_record_info(self) -> None:
        self.assertIsInstance(self.recording_info, hexoskin.RecordingInfo)

    def test_attributes_type(self) -> None:
        self.assertIsInstance(self.recording_info.patient_name, str)
        self.assertIsInstance(self.recording_info.sex, str)
        self.assertIsInstance(self.recording_info.start_time, datetime)
        self.assertIsInstance(self.recording_info.birth_date, date)
        self.assertIsInstance(self.recording_info.hexoskin_record_id, int)
        self.assertIsInstance(self.recording_info.hexoskin_user_id, int)
        self.assertIsInstance(self.recording_info.signals, list)

        for signal in self.recording_info.signals:
            self.assertIsInstance(signal, hexoskin.data.SignalHeader)
            self.assertIsInstance(signal.dimension, str)
            self.assertIsInstance(signal.label, str)
            self.assertIsInstance(signal.sample_rate, float)
