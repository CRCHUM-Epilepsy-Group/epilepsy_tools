import datetime

import pandas as pd

from epilepsy_tools.epidatavault import extract_seizures as esz

from . import config


def test_create_timestamp():
    assert esz.create_timestamp(
        pd.Timestamp("2021-01-01"), pd.Timestamp("12:00:00")
    ) == pd.Timestamp("2021-01-01 12:00:00")


def test_create_timestamp_nan():
    assert esz.create_timestamp(pd.Timestamp("2021-01-01"), None) is None


def test_create_timestamp_yes():
    assert esz.create_timestamp(pd.Timestamp("2021-01-01"), "yes") is None
    assert esz.create_timestamp(pd.Timestamp("2021-01-01"), "no") is None


def test_create_timestamp_time_timedelta():
    assert esz.create_timestamp(
        "2021-01-01", datetime.timedelta(0, 3600)
    ) == pd.Timestamp("2021-01-01 01:00:00")


def test_convert_date():
    assert esz.create_timestamp("2021-01-01", "12:00:00") == pd.Timestamp(
        "2021-01-01 12:00:00"
    )


def test_extract_sz_info():
    df = pd.ExcelFile(config.annotations).parse("p242", header=4)
    sz_info = esz.extract_seizure_info(df, "p242", ["FBTCS"])
    expected_keys = [
        "p_num",
        "sz_id",
        "sz_type",
        "sz_date",
        "electric_onset",
        "clinical_onset",
        "generalization",
        "motor_onset",
        "sz_offset",
    ]
    assert isinstance(sz_info, dict)
    assert all(key in sz_info for key in expected_keys)


def test_build_sz_datavault():
    szs = esz.build_seizure_datavault(
        pd.ExcelFile(config.annotations),
        config.patients,
        seizure_types=["FBTCS"],
        save_path=None,
    )

    assert isinstance(szs, pd.DataFrame)
