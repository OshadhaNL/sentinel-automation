
import os
import re

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage


def open_client_profile(
    page: Page,
    base_url: str,
    client_type: str = "individual",
    client_id: str | None = None,
):
    """
    Login and navigate to a client profile.

    If client_id is provided:
        Search for and open that exact client.

    If client_id is None:
        Select the first matching client type.

    Returns the selected client ID.
    """

    client_type = client_type.strip().lower()

    if client_type not in ("individual", "entity"):
        raise ValueError(
            f"Unsupported client type: {client_type}"
        )

    requested_id = (
        client_id.strip().upper()
        if client_id
        else None
    )

    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    assert email and password, (
        "Set TEST_EMAIL and TEST_PASSWORD"
    )

    # Login
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"),
        timeout=30000,
    )

    # Navigate to Profiles
    page.get_by_role(
        "link",
        name="Profiles",
        exact=False
    ).click()

    expect(
        page.get_by_role(
            "heading",
            name="Profiles",
            exact=True
        )
    ).to_be_visible(timeout=15000)

    # Open All Files
    all_files = page.locator(
        ".tab-z-option"
    ).filter(
        has=page.locator(
            "label",
            has_text=re.compile(
                r"^\s*All Files\s*$"
            )
        )
    ).first

    all_files.click()

    expect(all_files).to_have_class(
        re.compile(r"\bactive\b")
    )

    # Search by exact client ID when provided
    if requested_id:
        search = page.get_by_placeholder(
            "Search by client ID or name"
        )

        search.fill(requested_id)
        search.press("Enter")

    rows = page.locator(
        "tbody.ant-table-tbody tr.ant-table-row"
    )

    expect(rows.first).to_be_visible(
        timeout=15000
    )

    selected_row = None
    selected_id = None

    for index in range(rows.count()):
        row = rows.nth(index)

        # Client ID link
        link = row.locator("a[href]").first

        if link.count() == 0:
            continue

        row_client_id = (
            link.inner_text().strip().upper()
        )

        if requested_id and row_client_id != requested_id:
            continue

        # Read client type from the table's Type column.
        # Based on the existing Profiles table structure.
        cells = row.locator("td")

        if cells.count() < 3:
            continue

        row_type = (
            cells.nth(2).inner_text().strip().lower()
        )

        if client_type == "individual":
            valid_type = row_type == "individual"
        else:
            valid_type = row_type in (
                "entity",
                "company"
            )

        if not valid_type:
            continue

        selected_row = row
        selected_id = row_client_id

        break

    if selected_row is None:
        print("\nDEBUG: No matching client found")
        print(f"Requested client type: {client_type}")
        print(f"Requested client ID: {requested_id}")
        print(f"Visible table rows: {rows.count()}")

        for index in range(rows.count()):
            row = rows.nth(index)

            print(
                f"Row {index + 1}: "
                f"{row.inner_text()}"
            )

        pytest.fail(
            f"No matching {client_type} profile found. "
            "Check the table output above."
        )

    link = selected_row.locator(
        "a[href]"
    ).first

    expect(link).to_be_visible()

    print(
        f"\nSelected {client_type} client: "
        f"{selected_id}"
    )

    link.click()

    expect(page).to_have_url(
        re.compile(r"/nolimit/app/profiles/"),
        timeout=15000
    )

    return selected_id
