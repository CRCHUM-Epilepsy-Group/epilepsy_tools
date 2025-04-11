from typing import Literal

import pandas as pd


def load_annotation_file(annotations_path: str) -> pd.ExcelFile:
    """
    Load the annotation file and validate essential columns.

    Parameters
    ----------
    annotations_path : :class:`str`
        Path to the Excel file containing the annotations.

    Returns
    -------
    :class:`pandas.ExcelFile`
        The loaded annotations file.
    """

    annotations_excel = pd.ExcelFile(annotations_path)

    # Select a random sheet (excluding the first one)
    sheet_names = annotations_excel.sheet_names
    if len(sheet_names) < 2:
        raise ValueError("No valid annotation sheets found in the Excel file.")
    # Check for missing essential columns
    return annotations_excel


def generate_patient_numbers_list(
    annotations: pd.ExcelFile,
    selection: Literal["all", "range"] = "all",
    p_range: list[int] | None = None,
) -> list[str]:
    """Generate a list of patient numbers based on the specified selection mode.

    Parameters
    ----------
    annotations : :class:`pandas.ExcelFile`
        Excel file containing patient annotations.
    selection : Literal["all", "range"], optional
        Selection mode. ``"all"``: Extracts patient numbers from the sheet names
        in the annotations file (default). ``"range"``: Generates patient numbers
        within a specified range.
    p_range : list[int] | ``None``, optional
        A list containing two integers ``[start, end]`` for range selection,
        by default ``None``.

    Returns
    -------
    list[:class:`str`]
        A list of patient numbers in the format 'pXXX'.

    Raises
    ------
    :exc:`ValueError`
        Error loading the Excel file, or invalid arguments were passed.
    """
    if selection == "all":
        try:
            p_nums_file: list[str] = annotations.sheet_names  # type: ignore
        except Exception as e:
            raise ValueError(f"Error loading Excel file: {e}")
        p_nums = [
            p for p in p_nums_file if p.lower().startswith("p") and p[1:].isdigit()
        ]
    elif selection == "range":
        if not (
            isinstance(p_range, list)
            and len(p_range) == 2
            and all(isinstance(n, int) for n in p_range)
        ):
            raise ValueError("p_range must be a list of two integers: [start, end].")
        start, end = p_range
        if start > end:
            raise ValueError("Start number must be less than or equal to end number.")
        p_nums = [f"p{num}" for num in range(start, end + 1)]
    else:
        raise ValueError("Invalid selection mode. Use 'all' or 'range'.")
    return p_nums
