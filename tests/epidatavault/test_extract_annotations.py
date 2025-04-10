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
        ea.generate_p_nums_list(annotations, selection="range", p_range=[1000, 10])


def test_three_inputs():
    annotations = ea.load_annotation_file(config.annotations)
    with pytest.raises(ValueError) as exc_info:
        ea.generate_p_nums_list(annotations, selection="range", p_range=[100, 101, 102])

    assert (
        str(exc_info.value) == "p_range must be a list of two integers: [start, end]."
    )


def test_other_mode():
    annotations = ea.load_annotation_file(config.annotations)
    with pytest.raises(ValueError) as exc_info:
        ea.generate_p_nums_list(annotations, selection="something_else")

    assert str(exc_info.value) == "Invalid selection mode. Use 'all' or 'range'."


"""""
annotation_file = load_annotation_file(config["annotations"])

annotations = annotation_file.parse("p201", header=4)

print("------------------------------------")
num_sheets = len(annotation_file.sheet_names)
print("------------------------------------")
print(f"Number of sheets: {num_sheets}")
print("------------------------------------")
print(f"Anntation sheet head:\n {annotations.head()}")
print("------------------------------------")
print(f"Anntation sheet columns:\n {annotations.columns}")
print("------------------------------------")
print(f"Anntation sheet dtypes:\n {annotations.dtypes}")
print("------------------------------------")
"""
