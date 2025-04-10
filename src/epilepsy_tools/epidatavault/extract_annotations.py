import pandas as pd


def load_annotation_file(annotations_path: str) -> pd.ExcelFile:
    """
    Load the annotation file and validate essential columns.

    Parameters
    ----------
    annotations_path : str
        Path to the Excel file containing the annotations.

    Returns
    -------
    pd.ExcelFile
        The loaded annotations file.
    """

    annotations_excel = pd.ExcelFile(annotations_path)

    # Select a random sheet (excluding the first one)
    sheet_names = annotations_excel.sheet_names
    if len(sheet_names) < 2:
        raise ValueError("No valid annotation sheets found in the Excel file.")
    # Check for missing essential columns
    return annotations_excel


def generate_p_nums_list(
    annotations: pd.ExcelFile, selection: str = "all", p_range: list | None = None
) -> list:
    """
    Generate a list of patient numbers based on the specified selection mode.

    Parameters
    ----------
    annotations : pd.ExcelFile
        Excel file containing patient annotations.
    selection : str, optional
        Selection mode. Options:
        - **"all"**: Extracts patient numbers from the sheet names in the annotations file.
        - **"range"**: Generates patient numbers within a specified range.
    p_range : list, optional
        A list containing two integers `[start, end]` for range selection.

    Returns
    -------
    list
        A list of patient numbers in the format 'pXXX'.

    Raises
    ------
    ValueError
        If an invalid selection mode is provided or `p_range` is improperly formatted.
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
