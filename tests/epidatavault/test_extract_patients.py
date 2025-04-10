import pandas as pd

from epilepsy_tools.epidatavault import extract_patients as epy
from epilepsy_tools.epidatavault import patient_log as logger

from . import config


def test_extract_annotation_dates():
    annotations = pd.ExcelFile(config.annotations)
    p_num = "P109"
    start_date, end_date = epy.extract_annotation_dates(annotations, p_num)
    assert start_date == pd.to_datetime("2019-04-18")
    assert end_date == pd.to_datetime("2019-04-27")


def test_count_sz_num():
    p_num = "P176"
    sz_types = ["FIAS"]
    annotations = pd.ExcelFile(config.annotations).parse(p_num, header=4)
    sz_num = epy.count_seizures(annotations, sz_types)
    print(sz_num)
    assert sz_num == 2


def test_count_sz_num_all():
    p_num = "P176"
    sz_types = ["all"]
    annotations = pd.ExcelFile(config.annotations).parse(p_num, header=4)
    sz_num = epy.count_seizures(annotations, sz_types)
    print(sz_num)
    assert sz_num == 4


def test_build_pt_datavault():
    pts = epy.build_patient_datavault(
        pd.ExcelFile(config.annotations),
        config.patients,
        sz_types=["FBTCS"],
        save_path=None,
        log18=logger.load_patient_log(config.log18, "log18", config.password),
        log23=logger.load_patient_log(config.log23, "log23"),
    )
    assert isinstance(pts, pd.DataFrame)
