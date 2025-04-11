import pandas as pd


def extract_annotation_dates(
    annotations: pd.ExcelFile, patient_number: str
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Extract the start and end dates of the annotations for a patient.

    Parameters
    ----------
    annotations : :class:`pandas.ExcelFile`
        DataFrame containing patient annotations.
    patient_number : :class:`str`
        Patient number in the format ``pXXX``.

    Returns
    -------
    tuple[:class:`pandas.Timestamp`, :class:`pandas.Timestamp`]
        A tuple containing the start and end dates of the annotations.
    """
    annotations_df = annotations.parse(patient_number, header=None)
    start_date = pd.to_datetime(
        annotations_df.iloc[0, 1],  # type: ignore
        format="%Y-%m-%d",
        errors="coerce",
    )
    end_date = pd.to_datetime(
        annotations_df.iloc[1, 1],  # type: ignore
        format="%Y-%m-%d",
        errors="coerce",
    )

    return start_date, end_date


def count_seizures(
    annotations: pd.DataFrame, seizure_types: list[str] | None
) -> int | None:
    """
    Count the number of seizures of each type for a patient. If no seizure types are provided, all seizure types will be counted.

    Parameters
    ----------
    annotations : :class:`pandas.DataFrame`
        DataFrame containing patient annotations.
    seizure_types : list[:class:`str`]
        List of seizure types to count.

    Returns
    -------
    :class:`int`
        An :class:`int` of the count of total seizures.
    """
    if seizure_types is None:
        seizure_types = ["all"]

    available_sz_types = set(annotations["Seizure_Classification"].unique())

    sz_num = {}

    if seizure_types == ["all"]:
        sz_types_it = available_sz_types
    else:
        sz_types_it = seizure_types
    for sz_type in sz_types_it:
        if sz_type in available_sz_types:
            sz_num[sz_type] = (annotations["Seizure_Classification"] == sz_type).sum()
        else:
            sz_num[sz_type] = 0
    sz_num_total = int(sum(sz_num.values()))

    if seizure_types != ["all"] and sz_num_total == 0:
        sz_num_total = None

    return sz_num_total


def build_patient_datavault(
    annotations: pd.ExcelFile,
    patient_numbers: list[str],
    seizure_types: list[str] | None = None,
    log18: pd.DataFrame | None = None,
    log23: pd.DataFrame | None = None,
    save_path: str | None = None,
) -> pd.DataFrame:
    """Extract patient annotations for a list of patients.

    Parameters
    ----------
    annotations : :class:`pandas.ExcelFile`
        Excel file containing patient annotations.
    patient_numbers : list[:class:`str`]
        List of patient numbers in the format ``pXXX``.
    seizure_types : list[:class:`str`] | ``None``, optional
        List of seizure types to extract information for, by default ``None``.
    log18 : :class:`pandas.DataFrame` | ``None``, optional
        DataFrame containing patient log information from 2018, by default ``None``.
    log23 : :class:`pandas.DataFrame` | ``None``, optional
        DataFrame containing patient log information from 2023, by default ``None``.
    save_path : :class:`str` | ``None``, optional
        Path to save the extracted data, by default ``None``.

    Returns
    -------
    :class:`pandas.DataFrame`
        A DataFrame containing the extracted patient annotation information.

        The DataFrame will have the following columns:

        - ``patient_num`` (:class:`str`): Patient number in the format "pXXX".
        - ``patient_id`` (:class:`str`): Patient ID (CHUM file number).
        - ``patient_name`` (:class:`str`): Name of the patient.
        - ``start_date`` (:class:`pandas.Timestamp`): Date and time when annotation monitoring started, in "YYYY-MM-DD HH:MM:SS" format.
        - ``end_date`` (:class:`pandas.Timestamp`): Date and time when annotation monitoring ended, in "YYYY-MM-DD HH:MM:SS" format.
        - ``num_seizures`` (dict[:class:`str`, :class:`int`]): A dictionary containing the count of each seizure type for the patient.


    Raises
    ------
    :exc:`ValueError`
        Raised when no :class:`pandas.DataFrame` is passed for neither ``log18`` or ``log23``.
    """
    if log18 is None and log23 is None:
        raise ValueError("At least one of log18 or log23 must be provided.")

    patients_list = []

    for p_num in patient_numbers:
        annotation_sheet = annotations.parse(p_num, header=4)
        sz_counts = count_seizures(annotation_sheet, seizure_types)
        start_date, end_date = extract_annotation_dates(annotations, p_num)

        p_id = None
        p_name = None
        p_sex = None

        if log23 is not None:
            match = log23.loc[
                log23["ID du patient"].str.lower() == p_num.lower(),
                ["Numéro de dossier CHUM", "Nom, Prénom", "Sex"],
            ]
            if not match.empty:
                p_id, p_name, p_sex = match.iloc[0]

        if log18 is not None and (p_id is None or p_name is None):
            match = log18.loc[
                log18["# Code"].str.contains(p_num[1:], case=False, na=False),
                ["# Dossier médical", "Nom participant", "Sexe du participant"],
            ]
            if not match.empty:
                p_id, p_name, p_sex = match.iloc[0]

        if p_id is None:
            print(p_num, "-> No match found for patient ID")

        if p_name is None:
            print(p_num, "-> No match found for patient name")

        patient_data = {
            "patient_num": p_num,
            "patient_id": None if p_id == "nan" else str(p_id),
            "patient_name": p_name,
            "patient_sex": p_sex,
            "start_date": start_date,
            "end_date": end_date,
            "num_seizures": sz_counts,
        }

        if sz_counts is not None:
            patients_list.append(patient_data)

    patients_df = pd.DataFrame(patients_list)
    if save_path:
        patients_df.to_parquet(save_path, engine="pyarrow", index=False)
    return patients_df
