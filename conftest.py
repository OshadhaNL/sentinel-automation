from dotenv import load_dotenv
import os
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

def pytest_configure(config):
    """Reject unsafe parallel scheduling before any shared-client test starts.

    xdist workers receive a separate config, so check --dist only on the
    controller. With --dist=loadfile, tests from the individual onboarding
    module run sequentially on a single worker while other files run on the
    remaining workers. This does not protect against other modules deliberately
    modifying the same seeded client ID.
    """
    if hasattr(config, "workerinput"):
        return  # xdist worker; controller already validated its scheduler

    seeded_reuse = (
        os.getenv("TEST_REUSE_VERIFIED", "1") != "0"
        and os.getenv("TEST_REUSE_USE_EXISTING", "0") == "1"
        and bool(os.getenv("TEST_REUSE_CLIENT_ID", "").strip())
    )
    if not seeded_reuse:
        return

    workers = config.getoption("numprocesses", default=None)
    distribution = config.getoption("dist", default="load")
    if workers and distribution != "loadfile":
        raise pytest.UsageError(
            "Seeded shared-client reuse with parallel workers requires "
            "--dist=loadfile. Run with -n 6 --dist=loadfile, or use -n 0."
        )
