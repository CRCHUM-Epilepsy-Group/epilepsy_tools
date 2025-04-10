import msoffcrypto
import pandas as pd
import io

# Expected columns for validation
EXPECTED_COLUMNS = {
    "log18": [
        "# Code",
        "Nom participant",
        "Sexe du participant",
        "# Dossier médical",
        "Date début de la participation",
        "exclu",
        "Date de fin",
        "Commentaires",
        "MD",
        "Chambre",
        "Foyer de la crise",
        "Latéralisation",
        "Sémiologie (a réviser)",
        "Nombre de crise",
        "Date de crise",
        "Annoter",
    ],
    "log23": [
        "ID du patient",
        "Sex",
        "Nom, Prénom",
        "Âge",
        "Numéro de dossier CHUM",
        "Salle à l'UME",
        "Embrace2 / Emfit",
        "Oui ou non",
        "Hexoskin / BioPoint / Nose / Cometa",
        "Oui / Non",
        "Éligible?",
        "Accepte de participer?",
        "Date de signature du FIC jj/mmm/aaaa",
        "Date and time of seizures jj/mm/aaaa",
        "Date and time of seizures jj/mm/aaaa.1",
        "No.",
        "Number of false alarms",
        "Début de la participation          Visite initiale jj/mmm/aaaa",
        "Fin de la participation jj/mmm/aaaa",
        "Comments on false alarms",
        "Nom",
        "Date jj/mmm/aaaa",
        "nom d'infirmiére",
        "Commentaires",
    ],
}


def read_decrypted_excel(input_file, password, header=1) -> pd.DataFrame:
    """
    Reads and decrypts a password-protected Excel file.

    Parameters:
        input_file (str): Path to the encrypted Excel file.
        password (str): Password to decrypt the file.
        header (int): Row number to use as column names.

    Returns:
        pd.DataFrame: Decrypted Excel data as a Pandas DataFrame.

    Raises:
        ValueError: If decryption fails due to an incorrect password or corruption.
        FileNotFoundError: If the input file does not exist.
    """
    try:
        with open(input_file, "rb") as f:
            office_file = msoffcrypto.OfficeFile(f)
            office_file.load_key(password=password)

            decrypted_file = io.BytesIO()
            office_file.decrypt(decrypted_file)

            decrypted_file.seek(0)

            return pd.read_excel(decrypted_file, header=header)
    except msoffcrypto.exceptions.DecryptionError:
        raise ValueError("❌ Incorrect password or corrupted file. Decryption failed.")
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ File not found: {input_file}")
    except Exception as e:
        raise ValueError(f"❌ Unexpected error reading file: {e}")


def validate_columns(df, log_type):
    """
    Validates if the DataFrame columns match the expected schema.

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.
        log_type (str): Either "log18" or "log23".

    Raises:
        ValueError: If the columns do not match the expected schema.
    """
    expected_cols = EXPECTED_COLUMNS.get(log_type, [])
    actual_cols = df.columns.tolist()

    if set(actual_cols) != set(expected_cols):
        missing_cols = set(expected_cols) - set(actual_cols)
        extra_cols = set(actual_cols) - set(expected_cols)
        raise ValueError(
            f"Column mismatch in {log_type}, it is recommended to verify the file!\n"
            f"Missing columns: {missing_cols}\n"
            f"Unexpected columns: {extra_cols}"
        )


def load_log(log_path, log_type, password=None, header=1) -> pd.DataFrame:
    """
    Load log18 or log23, decrypting if neccessary, and returns cleaned DataFrames.

    Parameters:
        file_path (str): Path to the Excel file.
        log_type (str): Either "log18" or "log23" (plain).
        password (str, optional): Password to decrypt the file (only for log18).
        header (int, optional): Row number to use as column names. In date of creation, header = 1 is fucntional, if changed, verify in log
    Returns:
        log (pd.DataFrame): Cleaned DataFrame.
    """

    if log_type == "log18" and password:
        log = read_decrypted_excel(log_path, password=password, header=header)
        log = log.astype(str)
        log.columns = log.columns.str.strip()
    elif log_type == "log18" and not password:
        log = pd.read_excel(log_path, header=header)
        log = log.astype(str)
        log.columns = log.columns.str.strip()
    elif log_type == "log23":
        log = pd.read_excel(log_path, header=header)
        log.columns = log.columns.str.strip()
    else:
        raise ValueError(
            "Invalid log type. Use 'log18' (encrypted) or 'log23' (plain)."
        )

    # Validate the columns
    validate_columns(log, log_type)
    return log
