from dotenv import load_dotenv
import pytest

load_dotenv()

from config.settings import BASE_URL, TIMEOUT


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def default_timeout() -> int:
    return TIMEOUT