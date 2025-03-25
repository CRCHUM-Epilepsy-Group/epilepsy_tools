from pathlib import Path

import pandas as pd
import pytest

from epilepsy_tools import cometa


@pytest.fixture(scope="module")
def c3d_files() -> list[Path]:
    c3d_file_path = Path("tests/c3d_sample/")
    return list(c3d_file_path.glob("*.c3d"))


@pytest.fixture(scope="module")
def cometa_data(c3d_files: list[Path]) -> pd.DataFrame:
    return cometa.load_data(c3d_files[0])
