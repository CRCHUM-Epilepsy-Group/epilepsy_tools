import datetime
import traceback
from os import PathLike

import pandas as pd


def create_timestamp(
    date: str | pd.Timestamp | datetime.datetime | None,
    time: str | pd.Timestamp | datetime.datetime | datetime.timedelta | None,
) -> pd.Timestamp | None:
    """
    Create a :class:`~pandas.Timestamp` from a date and time string.

    Parameters
    ----------
    date : :class:`str`
        Date in the format 'YYYY-MM-DD'.
    time : :class:`str`
        Time in the format 'HH:MM:SS'.

    Returns
    -------
    :class:`pandas.Timestamp`
        A :class:`~pandas.Timestamp` object representing the given date and time.
    """
    if pd.isna(date) or pd.isna(time) or time is None:
        return None

    # Check if 'time' is a string representation of 'yes' or 'no'
    if isinstance(time, str) and time.lower() in ["yes", "no"]:
        return None

    # Ensure `date` is a pd.Timestamp object (convert string to timestamp)
    if isinstance(date, str):
        date_ts = pd.to_datetime(date, errors="coerce")
        if pd.isna(date_ts):
            return None

    elif isinstance(date, (pd.Timestamp, datetime.datetime)):
        date_ts = date

    if isinstance(time, int):
        try:
            time_str = f"{time:06d}"  # Ensure it's zero-padded to 6 digits
            time_ts = pd.to_datetime(time_str, format="%H%M%S", errors="coerce")
            if pd.isna(time_ts):
                return None
            time_ts = time_ts.time()
        except Exception:
            return None

    # Ensure `time` is a valid time string and convert to a datetime object
    elif isinstance(time, str):
        time_ts = pd.to_datetime(time, format="%H:%M:%S", errors="coerce")
        # If time parsing failed, return None
        if pd.isna(time_ts):
            return None
        time_ts = time_ts.time()  # Extract the time component only

    elif isinstance(time, (pd.Timestamp, datetime.time, datetime.datetime)):
        time_ts = time

    elif isinstance(time, datetime.timedelta):
        time_ts = (datetime.datetime.min + time).time()

    # Create and return a pd.Timestamp object with the combined date and time
    return pd.Timestamp(
        year=date_ts.year,
        month=date_ts.month,
        day=date_ts.day,
        hour=time_ts.hour,
        minute=time_ts.minute,
        second=time_ts.second,
        microsecond=time_ts.microsecond,
    )


def extract_seizure_info(
    annotations: pd.DataFrame, patient_number: str, seizure_types: list[str] | None
) -> dict:
    """
    Extract seizure information for a patient.

    Parameters
    ----------
    annotations : :class:`pandas.DataFrame`
        :class:`~pandas.DataFrame` containing patient annotations.
    patient_number : :class:`str`
        Patient number in the format ``pXXX``.
    seizure_types : list[:class:`str`]
        List of seizure types to extract information for.

    Returns
    -------
    dict
        A dictionary containing the extracted seizure information.

        The dictionary will have the folowing keys:

        - ``p_num`` (list[:class:`str`]): Patient number in the format ``pXXX``.
        - ``sz_id`` (list[:class:`int`]): Seizure number that each patient had.
        - ``sz_type`` (list[:class:`str`]): Seizure classification according to the ILAE classification.
        - ``sz_date`` (list[:class:`pandas.Timestamp`]): Date when the seizure happened.
        - ``electric_onset`` (list[:class:`pandas.Timestamp`]): Time when the electrical seizure activity began.
        - ``clinical_onset`` (list[:class:`pandas.Timestamp`]): Time when clinical seizure manifestations started.
        - ``generalization`` (list[:class:`pandas.Timestamp`]): Time when generalization of the seizure manifestations started.
        - ``motor_onset`` (list[:class:`pandas.Timestamp`]): Time when motor seizure manifestations started.
        - ``sz_offset`` (list[:class:`pandas.Timestamp`]): Time when the seizure ended.

    Notes
    -----
    The format of all onsets and offset is the same:
    - All are in the format "YYYY-MM-DD HH:MM:SS".
    """

    if seizure_types is None or seizure_types == ["all"]:
        seizure_types = list(annotations["Seizure_Classification"].unique())

    sz_info = {
        "p_num": [],
        "sz_id": [],
        "sz_type": [],
        "sz_date": [],
        "electric_onset": [],
        "clinical_onset": [],
        "generalization": [],
        "motor_onset": [],
        "sz_offset": [],
    }

    for sz_type in seizure_types:
        annotation_filtered = annotations[
            annotations["Seizure_Classification"] == sz_type
        ]
        # Loop over each row in the filtered annotations
        for index, row in annotation_filtered.iterrows():
            # Append the row's data to the corresponding list in sz_info
            sz_info["p_num"].append(patient_number)

            sz_id = row["Seizure_count"]

            if isinstance(sz_id, str):
                sz_id = None
            elif not isinstance(sz_id, int):
                sz_id = None

            sz_info["sz_id"].append(sz_id)

            sz_info["sz_type"].append(row["Seizure_Classification"])

            sz_info["sz_date"].append(
                pd.to_datetime(row["Seizure_Date"], errors="coerce")
            )

            electric_col = (
                "Electric_Onset"
                if "Electric_Onset" in annotations.columns
                else "Electrical_Onset"
            )
            sz_info["electric_onset"].append(
                create_timestamp(row["Seizure_Date"], row.get(electric_col))
            )
            sz_info["clinical_onset"].append(
                create_timestamp(row["Seizure_Date"], row["Clinical_Onset"])
            )
            sz_info["generalization"].append(
                create_timestamp(row["Seizure_Date"], row["Generalization"])
            )
            sz_info["motor_onset"].append(
                create_timestamp(row["Seizure_Date"], row["Motor_Onset"])
            )
            sz_info["sz_offset"].append(
                create_timestamp(row["Seizure_Date"], row["End"])
            )
    return sz_info


def build_seizure_datavault(
    annotations: pd.ExcelFile,
    patient_numbers: list[str],
    seizure_types: list[str] | None = None,
    save_path: str | PathLike | None = None,
) -> pd.DataFrame:
    """
    Extract seizure annotations for a list of patients.

    Parameters
    ----------
    annotations : :class:`pandas.ExcelFile`
        Excel file containing patient annotations.
    patient_numbers : list[:class:`str`]
        List of patient numbers in the format 'pXXX'.
    seizure_types : list[:class:`str`] | ``None``, optional
        List of seizure types to extract annotations for.
    save_path : :class:`str` | :class:`os.PathLike` | ``None``, optional
        Path to save the extracted data.

    Returns
    -------
    :class:`pandas.DataFrame`
        :class:`~pandas.DataFrame` containing seizure annotations for the specified patients.

        Each row in the DataFrame represents a seizure, and the columns are as follows:

        - ``p_num`` (:class:`str`): Patient number in the format ``pXXX``.
        - ``sz_id`` (:class:`int`): Seizure number that each patient had.
        - ``sz_type`` (:class:`str`): Seizure classification according to the ILAE classification.
        - ``sz_date`` (:class:`~pandas.Timestamp`): Date when the seizure happened.
        - ``electric_onset`` (:class:`~pandas.Timestamp`): Time when the electrical seizure activity began.
        - ``clinical_onset`` (:class:`~pandas.Timestamp`): Time when clinical seizure manifestations started.
        - ``generalization`` (:class:`~pandas.Timestamp`): Time when generalization of the seizure manifestations started.
        - ``motor_onset`` (:class:`~pandas.Timestamp`): Time when motor seizure manifestations started.
        - ``sz_offset`` (:class:`~pandas.Timestamp`): Time when the seizure ended.

    Notes
    -----
    The format of all onsets and offset is the same:
    - All are in the format "YYYY-MM-DD HH:MM:SS".
    """

    seizures_list = []

    for p_num in patient_numbers:
        try:
            annotation_sheet = annotations.parse(p_num, header=4)
            sz_info = extract_seizure_info(annotation_sheet, p_num, seizure_types)
            if len(sz_info["p_num"]) > 0:
                seizures_list.append(sz_info)
        except Exception as e:
            print(f"Error processing patient {p_num}: {e}")
            traceback.print_exc()

    seizures_df = pd.DataFrame(seizures_list)
    seizures_df = (
        pd.DataFrame(seizures_list)
        .apply(lambda col: col.explode())
        .reset_index(drop=True)
    )
    if save_path:
        seizures_df.to_parquet(save_path, index=False)

    return seizures_df
