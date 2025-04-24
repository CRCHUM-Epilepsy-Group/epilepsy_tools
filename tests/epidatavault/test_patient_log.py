import pandas as pd
import pytest

from epilepsy_tools.epidatavault import patient_log as logger

from . import config


def test_incorrect_password():
    with pytest.raises(ValueError) as e:
        logger.read_decrypted_excel(config.log18, "wrong_password")
    assert "❌ Incorrect password or corrupted file. Decryption failed." in str(e.value)


def test_load_log18():
    df = logger.load_patient_log(config.log18, "log18", config.password)
    assert isinstance(df, pd.DataFrame)


def test_load_log23():
    df = logger.load_patient_log(config.log23, "log23")
    assert isinstance(df, pd.DataFrame)


def test_load_wrong_version():
    with pytest.raises(ValueError):
        logger.load_patient_log(config.log23, "log42")  # type: ignore
