import pytest
import requests

from helpers import API_URL, BASE_URL, FIXTURES, make_test_image, make_test_txt


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def api_url() -> str:
    return API_URL.rstrip("/")


@pytest.fixture(scope="session", autouse=True)
def ensure_stack_up(base_url: str, api_url: str):
    """Fail fast if Docker stack is not running."""
    try:
        ui = requests.get(base_url, timeout=5)
        api = requests.get(f"{api_url}/api/comments/", timeout=5)
    except requests.RequestException as exc:
        pytest.exit(
            f"Stack is not reachable ({exc}). "
            f"Run: docker compose up --build -d",
            returncode=1,
        )
    if ui.status_code >= 500 or api.status_code >= 500:
        pytest.exit("UI or API returned 5xx — check docker compose logs.", returncode=1)


@pytest.fixture(scope="session")
def sample_image() -> str:
    path = make_test_image(FIXTURES / "e2e_big.png")
    return str(path)


@pytest.fixture(scope="session")
def sample_txt() -> str:
    path = make_test_txt(FIXTURES / "e2e_note.txt")
    return str(path)


@pytest.fixture
def page(context, base_url: str):
    page = context.new_page()
    page.set_default_timeout(15_000)
    page.goto(base_url)
    page.get_by_role("heading", name="Comments", exact=True).first.wait_for()
    yield page
    page.close()
