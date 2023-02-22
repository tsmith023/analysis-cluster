import os
import pytest
from dotenv import load_dotenv

from ..manager.api import IEXAPI

@pytest.fixture(scope='session', autouse=True)
def load_env():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env.test"))
