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


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    args = [
        arg
        for arg in browser_type_launch_args.get("args", [])
        if not arg.startswith((
            "--use-fake-device-for-media-stream",
            "--use-fake-ui-for-media-stream",
            "--use-file-for-fake-video-capture",
        ))
    ]

    return {
        **browser_type_launch_args,
        "args": args,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "permissions": ["camera"],
    }