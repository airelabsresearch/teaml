from pathlib import Path

import pytest
import teaml as tml

@pytest.fixture(scope="session")
def finance101yaml():
    path = Path(__file__).parent / "fixtures" / "Finance101.yaml"
    return open(path, 'r').read()
