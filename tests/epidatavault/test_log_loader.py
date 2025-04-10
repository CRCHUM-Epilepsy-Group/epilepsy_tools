import pandas as pd
import pytest

from epilepsy_tools.epidatavault import log_loader as logger

from . import config


def test_incorrect_password():
    with pytest.raises(ValueError) as e:
        logger.read_decrypted_excel(config.log_18, "wrong_password")
    assert "❌ Incorrect password or corrupted file. Decryption failed." in str(e.value)


def test_load_log18():
    df = logger.load_log(config.log_18, "log18", config.password)
    assert isinstance(df, pd.DataFrame)


def test_load_log23():
    df = logger.load_log(config.log_23, "log23")
    assert isinstance(df, pd.DataFrame)
