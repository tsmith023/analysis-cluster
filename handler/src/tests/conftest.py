import os
import pytest
from dotenv import load_dotenv

from ..portfolio.api import PortfolioAPI

@pytest.fixture(scope='session', autouse=True)
def load_env():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env.test"))


@pytest.fixture(scope="session")
def portfolio_api():
    api = PortfolioAPI.create()
    try:
        return api
    finally:
        api.close()
