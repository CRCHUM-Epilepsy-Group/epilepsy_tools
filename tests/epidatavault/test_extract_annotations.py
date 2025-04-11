import pandas as pd
import pytest

from epilepsy_tools.epidatavault import extract_annotations as ea

from . import config


def test_annotation_loader():
    assert type(ea.load_annotation_file(config.annotations)) is pd.ExcelFile


def test_range_outtabounds():
    annotations = ea.load_annotation_file(config.annotations)
    with pytest.raises(
        ValueError, match="Start number must be less than or equal to end number."
    ):
        ea.generate_patient_numbers_list(
            annotations, selection="range", parient_range=[1000, 10]
        )


def test_three_inputs():
    annotations = ea.load_annotation_file(config.annotations)
    with pytest.raises(ValueError) as exc_info:
        ea.generate_patient_numbers_list(
            annotations, selection="range", parient_range=[100, 101, 102]
        )

    assert (
        str(exc_info.value) == "p_range must be a list of two integers: [start, end]."
    )


def test_other_mode():
    annotations = ea.load_annotation_file(config.annotations)
    with pytest.raises(ValueError) as exc_info:
        ea.generate_patient_numbers_list(annotations, selection="something_else")  # type: ignore

    assert str(exc_info.value) == "Invalid selection mode. Use 'all' or 'range'."
