import os
import re
import uuid
import pytest
from playwright.sync_api import expect
from pages.loginPage import LoginPage
from pages.mainOnboardingPage import MainOnboardingPage, ROLES, CONSENT_ITEMS, CONSENT_INTRO, CONSENT_ACK


def unique_name(kind):
    return f'Automation {kind} {uuid.uuid4().hex[:12]}'


@pytest.fixture
def onboarding(page, base_url):
    email = os.getenv('TEST_EMAIL')
    password = os.getenv('TEST_PASSWORD')
    assert email and password, 'Set TEST_EMAIL and TEST_PASSWORD in the environment.'
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(re.compile(r'.*/nolimit/app/home/?$'), timeout=30000)
    page.get_by_role('link', name='Onboarding', exact=False).click()
    expect(page).to_have_url(re.compile(r'.*/nolimit/app/onboarding/?$'))
    return MainOnboardingPage(page)


@pytest.mark.ui
class TestMainOnboarding:
    def test_heading_and_description(self, onboarding):
        expect(onboarding.heading).to_be_visible()
        expect(onboarding.description).to_be_visible()

    def test_tabs_icons_and_default_active(self, onboarding):
        expect(onboarding.new_tab).to_be_visible()
        expect(onboarding.pending_tab).to_be_visible()
        expect(onboarding.new_tab.locator('i.fa-sparkles')).to_be_visible()
        expect(onboarding.pending_tab.locator('i.fa-pause-circle')).to_be_visible()
        expect(onboarding.new_tab).to_have_class(re.compile(r'\bactive\b'))
        expect(onboarding.pending_tab).not_to_have_class(re.compile(r'\bactive\b'))

    def test_pending_tab_becomes_active(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.pending_tab).to_have_class(re.compile(r'\bactive\b'))
        expect(onboarding.new_tab).not_to_have_class(re.compile(r'\bactive\b'))

    def test_pending_search_and_icons(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.search).to_be_visible()
        expect(onboarding.search).to_have_attribute('placeholder', 'Search by Reference ID or Client name')
        expect(onboarding.search_button.locator('i.fa-search')).to_be_visible()
        expect(onboarding.clear_button).to_be_hidden()
        onboarding.search.fill('TEST')
        expect(onboarding.clear_button).to_be_visible()
        onboarding.clear_button.click()
        expect(onboarding.search).to_have_value('')
        onboarding.search_button.click()

    def test_analyst_label_filter_and_options(self, onboarding):
        onboarding.open_pending()

        label = onboarding.page.locator("label").filter(
            has_text="Created By"
        ).first
        expect(label).to_be_visible()

        dropdown = onboarding.analyst_filter()
        expect(dropdown).to_be_visible()

        expect(
            dropdown.locator(".ant-select-selection-placeholder")
        ).to_have_text("Filter by Analyst")

        onboarding.wait_for_analyst_options()

        expected_analysts = [
            "Oshadha Weerakon",
            "Senith Client",
            "Senith Compliance Officer",
            "Test Admin",
            "Senith Admin",
            "TEST1 Doe",
        ]

        for analyst in expected_analysts:
            option = onboarding.analyst_options().filter(
                has=onboarding.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(analyst, exact=True)
            )
            expect(option).to_be_visible()

    def test_pending_table_headers_and_data(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.table).to_be_visible()
        expect(onboarding.table.locator('thead th')).to_have_text(['Reference ID', 'Name', 'Type', 'Status', 'Created Date', 'Last Update', 'Created By'])
        expect(onboarding.rows.first).to_be_visible()
        for index in range(7):
            assert onboarding.rows.first.locator('td').nth(index).inner_text().strip(), f'Column {index + 1} is blank'
        # Last Update may legitimately show N/A.

    def test_reference_id_navigation(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.rows.first).to_be_visible()
        link = onboarding.rows.first.locator('td').first.locator('a.table-link')
        reference = link.inner_text().strip()
        href = link.get_attribute('href')
        assert href and re.search(rf'/nolimit/app/onboarding/(individual|entity)/process\?.*client={re.escape(reference)}(?:&|$)', href)
        link.click()
        expect(onboarding.page).to_have_url(re.compile(rf'.*/nolimit/app/onboarding/(individual|entity)/process\?.*client={re.escape(reference)}(?:&|$)'))

    def test_pagination_controls(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.pagination).to_be_visible()
        expect(onboarding.pagination.locator('.ant-pagination-prev')).to_be_visible()
        expect(onboarding.pagination.locator('.ant-pagination-next')).to_be_visible()
        expect(onboarding.page_size).to_be_visible()

    def test_next_previous_pagination(self, onboarding):
        onboarding.open_pending()
        next_button = onboarding.pagination.locator('.ant-pagination-next')
        if next_button.get_attribute('aria-disabled') == 'true':
            pytest.skip('Only one page of pending records exists.')
        expect(onboarding.rows.first).to_be_visible()
        first_page = onboarding.row_ids()
        next_button.click()
        expect(onboarding.pagination.locator('.ant-pagination-item-active')).to_contain_text('2')
        expect(onboarding.rows.first.locator('td').first).not_to_have_text(first_page[0], timeout=15000)
        assert onboarding.row_ids() != first_page, 'Next page did not change records'
        onboarding.pagination.locator('.ant-pagination-prev').click()
        expect(onboarding.pagination.locator('.ant-pagination-item-active')).to_contain_text('1')
        expect(onboarding.rows.first.locator('td').first).to_have_text(first_page[0], timeout=15000)
        assert onboarding.row_ids() == first_page, 'Previous page did not restore records'

    @pytest.mark.parametrize('size', [10, 20, 50, 100])
    def test_page_size(self, onboarding, size):
        onboarding.open_pending()
        onboarding.page_size_select(size)
        assert onboarding.rows.count() <= size
        assert onboarding.rows.count() > 0

    def test_new_client_name_and_cards(self, onboarding):
        expect(onboarding.page.get_by_text('Client Name', exact=True)).to_be_visible()
        expect(onboarding.name).to_be_visible()
        expect(onboarding.name).to_have_attribute('placeholder', 'Enter client name')
        value = 'Test A1 !@#'
        onboarding.name.fill(value)
        expect(onboarding.name).to_have_value(value)
        expect(onboarding.page.get_by_role('heading', name='Select Client Type')).to_be_visible()
        for card, icon, description in [
            (onboarding.individual, 'fa-user-plus', 'Select this path to onboard an individual client.'),
            (onboarding.entity, 'fa-building', 'Select this path to onboard a business entity.'),
        ]:
            expect(card).to_be_visible()
            expect(card.locator(f'i.{icon}')).to_be_visible()
            expect(card.locator('p')).to_contain_text(description)

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_client_name_required(self, onboarding, kind):
        card = onboarding.individual if kind == 'individual' else onboarding.entity
        card.click()
        expect(onboarding.name_required_notification()).to_be_visible()

    @pytest.mark.parametrize("kind", ["individual", "entity"])
    def test_selected_card_role_label_and_disabled_proceed(
            self, onboarding, kind
    ):
        onboarding.choose_client(kind, unique_name(kind))

        label = (
            "Client Role" if kind == "individual"
            else "Customer Role"
        )

        expect(
            onboarding.page.get_by_text(label, exact=True)
        ).to_be_visible()

        dropdown = onboarding.role_dropdown(kind)
        expect(dropdown).to_be_visible()

        placeholder = (
            "Select client role" if kind == "individual"
            else "Select customer role"
        )

        expect(
            dropdown.locator(".ant-select-selection-placeholder")
        ).to_have_text(placeholder)

        expect(onboarding.proceed).to_be_visible()

        # This intentionally fails if the application enables
        # Proceed before a role is selected.
        onboarding.assert_proceed_disabled_before_role(kind)

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_role_options_available(self, onboarding, kind):
        onboarding.choose_client(kind, unique_name(kind))
        onboarding.role_dropdown(kind).click()
        for role in ROLES:
            option = onboarding.page.locator('.ant-select-dropdown:visible .ant-select-item-option').filter(has=onboarding.page.locator('.ant-select-item-option-content').get_by_text(role, exact=True))
            expect(option).to_be_visible()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    @pytest.mark.parametrize('role', ROLES)
    def test_role_selection_enables_proceed(self, onboarding, kind, role):
        onboarding.choose_client(kind, unique_name(kind))
        onboarding.select_role(kind, role)
        expect(onboarding.proceed).to_be_enabled()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_content_controls_and_cancel(self, onboarding, kind):
        onboarding.open_consent(kind, unique_name(kind))
        expect(onboarding.consent.locator('.modal-z-title h6')).to_have_text('Consent Letter')
        expect(onboarding.consent_close()).to_be_visible()
        expect(onboarding.consent.get_by_text(CONSENT_INTRO, exact=True)).to_be_visible()
        for statement in CONSENT_ITEMS:
            expect(onboarding.consent.get_by_text(statement, exact=True)).to_be_visible()
        expect(onboarding.consent.get_by_text(CONSENT_ACK, exact=True)).to_be_visible()
        checkbox = onboarding.consent_checkbox()
        expect(checkbox).not_to_be_checked()
        expect(onboarding.consent_agree()).to_have_class(re.compile('cursor-not-allowed'))
        expect(onboarding.consent_cancel()).to_be_visible()
        checkbox.check()
        expect(checkbox).to_be_checked()
        expect(onboarding.consent_agree()).not_to_have_class(re.compile('cursor-not-allowed'))
        onboarding.consent_cancel().click()
        expect(onboarding.consent).to_be_hidden()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_close_x(self, onboarding, kind):
        onboarding.open_consent(kind, unique_name(kind))
        onboarding.consent_close().click()
        expect(onboarding.consent).to_be_hidden()

    def test_individual_consent_agree_navigates(self, onboarding):
        onboarding.open_consent('individual', unique_name('individual'))
        onboarding.consent_checkbox().check()
        onboarding.consent_agree().click()
        expect(onboarding.page).to_have_url(re.compile(r'.*/nolimit/app/onboarding/individual/process\?client=[^&]+&step=verification(?:&.*)?$'))

    def test_existing_individual_popup_and_okay(self, onboarding):
        onboarding.choose_client('individual', os.getenv('EXISTING_INDIVIDUAL_NAME', 'oshadha'))
        onboarding.select_role('individual', 'Seller')
        onboarding.proceed.click()
        expect(onboarding.existing).to_be_visible()
        expect(onboarding.existing.locator('.modal-z-title h6')).to_have_text('Existing Client Information')
        expect(onboarding.existing.get_by_text('A client with this name already exists. You can continue onboarding this client.', exact=True)).to_be_visible()
        expect(onboarding.existing.get_by_text('Previous Client Name', exact=True)).to_be_visible()
        expect(onboarding.existing.get_by_text('Document Number', exact=True)).to_be_visible()
        expect(onboarding.existing.get_by_text(os.getenv('EXISTING_INDIVIDUAL_NAME', 'oshadha'), exact=True)).to_be_visible()
        expect(onboarding.existing_okay()).to_be_visible()
        onboarding.existing_okay().click()
        expect(onboarding.consent).to_be_visible()

    def test_existing_individual_close_x(self, onboarding):
        onboarding.choose_client('individual', os.getenv('EXISTING_INDIVIDUAL_NAME', 'oshadha'))
        onboarding.select_role('individual', 'Seller')
        onboarding.proceed.click()
        expect(onboarding.existing).to_be_visible()
        onboarding.existing_close().click()
        expect(onboarding.existing).to_be_hidden()
        expect(onboarding.consent).to_be_visible()

    # ------------------------------------------------------------
    # Additional independent tests for the remaining checklist items
    # ------------------------------------------------------------

    def test_main_page_element_order(self, onboarding):
        # Compare actual vertical positions, rather than assuming DOM order.
        assert onboarding.description.bounding_box()['y'] > onboarding.heading.bounding_box()['y']
        assert onboarding.pending_tab.bounding_box()['x'] > onboarding.new_tab.bounding_box()['x']
        assert onboarding.name.bounding_box()['y'] > onboarding.page.get_by_text('Client Name', exact=True).bounding_box()['y']
        assert onboarding.page.get_by_role('heading', name='Select Client Type').bounding_box()['y'] > onboarding.name.bounding_box()['y']
        assert onboarding.individual.bounding_box()['y'] > onboarding.page.get_by_role('heading', name='Select Client Type').bounding_box()['y']
        assert onboarding.entity.bounding_box()['x'] > onboarding.individual.bounding_box()['x']

    def test_new_tab_default_active_and_pending_active_classes(self, onboarding):
        expect(onboarding.new_tab).to_have_class(re.compile(r'\bactive\b'))
        onboarding.open_pending()
        expect(onboarding.pending_tab).to_have_class(re.compile(r'\bactive\b'))
        expect(onboarding.new_tab).not_to_have_class(re.compile(r'\bactive\b'))

    def test_pending_search_icon_and_created_by_label_position(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.search_button.locator('i.fa-search')).to_be_visible()
        label = onboarding.page.locator('label').filter(has_text=re.compile(r'^Created By$')).first
        expect(label).to_be_visible()
        assert label.bounding_box()['x'] > onboarding.search.bounding_box()['x']

    def test_pending_search_filters_by_reference_id(self, onboarding):
        onboarding.open_pending()
        expect(onboarding.rows.first).to_be_visible()
        ref_id = onboarding.rows.first.locator('td').first.inner_text().strip()
        onboarding.search.fill(ref_id)
        onboarding.search_button.click()
        onboarding.wait_for_reference_search(ref_id)

    @pytest.mark.parametrize('column,header', list(enumerate([
        'Reference ID', 'Name', 'Type', 'Status', 'Created Date',
        'Last Update', 'Created By'
    ])))
    def test_pending_each_column_header_and_value(self, onboarding, column, header):
        onboarding.open_pending()
        expect(onboarding.table.locator('thead th').nth(column)).to_have_text(header)
        expect(onboarding.rows.first).to_be_visible()
        value = onboarding.rows.first.locator('td').nth(column).inner_text().strip()
        assert value, f'{header} column has no value in the first record'
        if header == 'Reference ID':
            assert value.startswith('SENTINEL')
        if header == 'Type':
            assert value.lower() in ('individual', 'entity')
        if header in ('Created Date', 'Last Update'):
            # Last Update is allowed to be N/A in this application.
            assert value == 'N/A' or re.search(r'\w+ \d{1,2}, \d{4}', value)

    def test_pending_pagination_changes_and_restores_reference_ids(self, onboarding):
        onboarding.open_pending()
        next_button = onboarding.pagination.locator('.ant-pagination-next')
        if next_button.get_attribute('aria-disabled') == 'true':
            pytest.skip('Pending records fit on a single page')
        first = onboarding.row_ids()
        next_button.click()
        expect(onboarding.pagination.locator('.ant-pagination-item-active')).to_contain_text('2')
        expect(onboarding.rows.first.locator('td').first).not_to_have_text(first[0], timeout=15000)
        assert onboarding.row_ids() != first
        onboarding.pagination.locator('.ant-pagination-prev').click()
        expect(onboarding.pagination.locator('.ant-pagination-item-active')).to_contain_text('1')
        expect(onboarding.rows.first.locator('td').first).to_have_text(first[0], timeout=15000)
        assert onboarding.row_ids() == first

    @pytest.mark.parametrize('size', [10, 20, 50, 100])
    def test_page_size_exact_when_enough_records(self, onboarding, size):
        onboarding.open_pending()
        # If fewer than `size` records exist overall, only the available
        # records can be shown; do not invent rows to reach the page size.
        onboarding.page_size_select(size)
        # Wait for asynchronous pagination update before reading row count.
        expect(onboarding.rows.first).to_be_visible(timeout=15000)
        count = onboarding.rows.count()
        assert 0 < count <= size
        expect(onboarding.page_size.locator('.ant-select-selection-item')).to_have_text(f'{size} / page')
        if onboarding.pagination.locator('.ant-pagination-next').get_attribute('aria-disabled') == 'false':
            expect(onboarding.rows).to_have_count(size, timeout=15000)

    def test_analyst_dropdown_displays_available_names(
            self, onboarding
    ):
        onboarding.open_pending()
        onboarding.wait_for_analyst_options()

        expected_names = [
            "Oshadha Weerakon",
            "Senith Client",
            "Senith Compliance Officer",
            "Test Admin",
            "Senith Admin",
            "TEST1 Doe",
        ]

        for name in expected_names:
            option = onboarding.analyst_options().filter(
                has=onboarding.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(name, exact=True)
            )
            expect(option).to_be_visible()

    @pytest.mark.parametrize('analyst', ['Oshadha Weerakon', 'Senith Admin'])
    def test_analyst_filter_matches_visible_created_by_values(
            self, onboarding, analyst
    ):
        onboarding.open_pending()
        onboarding.select_analyst(analyst)

        # Wait for the dropdown to close after selection.
        expect(
            onboarding.page.locator(".ant-select-dropdown:visible")
        ).to_have_count(0, timeout=10000)

        # Allow filtered table data to settle.
        onboarding.page.wait_for_timeout(500)

        for value in onboarding.created_by_values():
            assert value == analyst, (
                f"Expected Created By '{analyst}', "
                f"but found '{value}'"
            )

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_card_selected_active_class(self, onboarding, kind):
        onboarding.choose_client(kind, unique_name(kind))
        card = onboarding.individual if kind == 'individual' else onboarding.entity
        expect(card).to_have_class(re.compile(r'\bactive\b'))

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_client_card_description_full_text(self, onboarding, kind):
        expected = (
            'Select this path to onboard an individual client. You will be guided to enter personal data, '
            'upload identity documentation, and complete mandatory KYC requirements.'
            if kind == 'individual' else
            'Select this path to onboard a business entity. You will be guided to enter company details, '
            'upload supporting documents, and complete mandatory KYC and compliance requirements.'
        )
        card = onboarding.individual if kind == 'individual' else onboarding.entity
        expect(card.locator('p')).to_have_text(expected)

    @pytest.mark.parametrize("kind", ["individual", "entity"])
    def test_role_dropdown_position_and_proceed_position(
            self, onboarding, kind
    ):
        onboarding.choose_client(kind, unique_name(kind))

        dropdown = onboarding.role_dropdown(kind)
        expect(dropdown).to_be_visible()

        dropdown_box = dropdown.bounding_box()
        proceed_box = onboarding.proceed.bounding_box()

        assert dropdown_box is not None
        assert proceed_box is not None

        assert proceed_box["y"] > dropdown_box["y"], (
            "Proceed button should appear below the role dropdown"
        )

        onboarding.assert_proceed_disabled_before_role(kind)

        onboarding.select_role(kind, "Seller")
        expect(onboarding.proceed).to_be_enabled()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_checkbox_agree_and_close_controls(self, onboarding, kind):
        onboarding.open_consent(kind, unique_name(kind))
        expect(onboarding.consent.locator('.modal-z-title h6')).to_have_text('Consent Letter')
        expect(onboarding.consent_close()).to_be_visible()
        expect(onboarding.consent_agree()).to_be_visible()
        expect(onboarding.consent_cancel()).to_be_visible()
        checkbox = onboarding.consent_checkbox()
        expect(checkbox).not_to_be_checked()
        expect(onboarding.consent_agree()).to_have_class(re.compile(r'cursor-not-allowed'))
        checkbox.check()
        expect(checkbox).to_be_checked()
        expect(onboarding.consent_agree()).not_to_have_class(re.compile(r'cursor-not-allowed'))

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_full_text_and_cancel(self, onboarding, kind):
        onboarding.open_consent(kind, unique_name(kind))
        expect(onboarding.consent.get_by_text(CONSENT_INTRO, exact=True)).to_be_visible()
        for text in CONSENT_ITEMS:
            expect(onboarding.consent.get_by_text(text, exact=True)).to_be_visible()
        expect(onboarding.consent.get_by_text(CONSENT_ACK, exact=True)).to_be_visible()
        onboarding.consent_cancel().click()
        expect(onboarding.consent).to_be_hidden()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_existing_client_popup_fields_and_okay(self, onboarding, kind):
        # Individual: use the known existing record. Entity: create a fresh
        # record by agreeing to consent, return and reuse its name.
        if kind == 'individual':
            name = 'oshadha'
        else:
            name = os.getenv('EXISTING_ENTITY_NAME')
            if not name:
                pytest.skip('Set EXISTING_ENTITY_NAME to an existing entity for this test')
        onboarding.start_existing_flow(kind, name)
        expect(onboarding.existing.locator('.modal-z-title h6')).to_have_text('Existing Client Information')
        expect(onboarding.existing_close()).to_be_visible()
        expect(onboarding.existing.get_by_text(
            'A client with this name already exists. You can continue onboarding this client.', exact=True
        )).to_be_visible()
        expect(onboarding.existing_value('Previous Client Name')).to_have_text(name)
        expect(onboarding.existing_value('Document Number')).not_to_be_empty()
        expect(onboarding.existing_okay()).to_be_enabled()
        onboarding.existing_okay().click()
        expect(onboarding.existing).to_be_hidden()
        expect(onboarding.consent).to_be_visible()

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_existing_client_close_returns_to_consent(self, onboarding, kind):
        if kind == 'individual':
            name = 'oshadha'
        else:
            name = os.getenv('EXISTING_ENTITY_NAME')
            if not name:
                pytest.skip('Set EXISTING_ENTITY_NAME to an existing entity for this test')
        onboarding.start_existing_flow(kind, name)
        onboarding.existing_close().click()
        expect(onboarding.existing).to_be_hidden()
        expect(onboarding.consent).to_be_visible()

    # Explicit assertions for checklist details not fully verified above.

    def test_selected_tabs_have_distinct_computed_appearance(self, onboarding):
        # Checklist 5, 8: selected vs unselected styling must actually change.
        new_active = onboarding.computed_appearance(onboarding.new_tab)
        pending_inactive = onboarding.computed_appearance(onboarding.pending_tab)
        assert new_active != pending_inactive, 'Default selected tab has no visual distinction'
        onboarding.open_pending()
        pending_active = onboarding.computed_appearance(onboarding.pending_tab)
        new_inactive = onboarding.computed_appearance(onboarding.new_tab)
        assert pending_active != new_inactive, 'Pending selected tab has no visual distinction'
        assert new_active != new_inactive, 'New tab style did not change when deselected'
        assert pending_active != pending_inactive, 'Pending tab style did not change when selected'
        # Confirm exact pink hex/RGB against your design tokens once supplied.

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_selected_client_card_changes_actual_styling(self, onboarding, kind):
        # Checklist 52, 76: compare before/after computed styles.
        card = onboarding.individual if kind == 'individual' else onboarding.entity
        before = onboarding.computed_appearance(card)
        onboarding.choose_client(kind, unique_name(kind))
        after = onboarding.computed_appearance(card)
        assert before != after, f'{kind} card selection has no visual styling change'

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_role_dropdown_is_below_its_label(self, onboarding, kind):
        # Checklist 54, 78.
        onboarding.choose_client(kind, unique_name(kind))
        label = onboarding.client_role_label(kind)
        dropdown = onboarding.role_dropdown(kind)
        expect(label).to_be_visible()
        expect(dropdown).to_be_visible()
        assert dropdown.bounding_box()['y'] >= label.bounding_box()['y'] + label.bounding_box()['height'] - 2

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_close_is_in_top_right(self, onboarding, kind):
        # Checklist 102, 137.
        onboarding.open_consent(kind, unique_name(kind))
        close_box = onboarding.consent_close().bounding_box()
        modal_box = onboarding.consent.bounding_box()
        title_box = onboarding.consent_title().bounding_box()
        assert close_box['x'] > title_box['x']
        assert close_box['x'] + close_box['width'] > modal_box['x'] + modal_box['width'] / 2
        assert close_box['y'] < modal_box['y'] + modal_box['height'] / 3

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_consent_agree_is_blocked_until_checkbox_selected(self, onboarding, kind):
        # Checklist 119, 120, 154, 155. Verify behavior, not only CSS.
        onboarding.open_consent(kind, unique_name(kind))
        url_before = onboarding.page.url
        agree = onboarding.consent_agree()
        checkbox = onboarding.consent_checkbox()
        expect(checkbox).not_to_be_checked()
        # dispatch_event exercises application click handler even when the CSS
        # prevents a normal user click. Consent must still be enforced.
        agree.dispatch_event('click')
        expect(onboarding.consent).to_be_visible()
        assert onboarding.page.url == url_before, 'Agree navigated without consent'
        checkbox.check()
        expect(checkbox).to_be_checked()
        expect(agree).not_to_have_class(re.compile('cursor-not-allowed'))
        agree.click()
        expect(onboarding.consent).to_be_hidden(timeout=10000)
        if kind == 'individual':
            expect(onboarding.page).to_have_url(
                re.compile(r'.*/nolimit/app/onboarding/individual/process\?.*client=[^&]+.*'),
                timeout=10000,
            )

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_existing_close_button_in_top_right(self, onboarding, kind):
        # Checklist 125, 160. Needs a previously created record.
        if kind == 'individual':
            name = os.getenv('EXISTING_INDIVIDUAL_NAME', 'oshadha')
        else:
            name = os.getenv('EXISTING_ENTITY_NAME')
            if not name:
                pytest.skip('Set EXISTING_ENTITY_NAME to a confirmed existing Entity name')
        onboarding.start_existing_flow(kind, name)
        close_box = onboarding.existing_close().bounding_box()
        modal_box = onboarding.existing.bounding_box()
        title_box = onboarding.existing_title().bounding_box()
        assert close_box['x'] > title_box['x']
        assert close_box['x'] + close_box['width'] > modal_box['x'] + modal_box['width'] / 2
        assert close_box['y'] < modal_box['y'] + modal_box['height'] / 3

    @pytest.mark.parametrize('kind', ['individual', 'entity'])
    def test_existing_client_values_and_return_to_consent(self, onboarding, kind):
        # Checklist 123-134, 158-169: deterministic fixture preferred over
        # creating an Entity that might not be persisted by consent alone.
        env_var = 'EXISTING_INDIVIDUAL_NAME' if kind == 'individual' else 'EXISTING_ENTITY_NAME'
        name = os.getenv(env_var, 'oshadha' if kind == 'individual' else '')
        if not name:
            pytest.skip(f'Set {env_var} to a confirmed existing record name')
        onboarding.start_existing_flow(kind, name)
        expect(onboarding.existing_title()).to_have_text('Existing Client Information')
        expect(onboarding.existing).to_contain_text('A client with this name already exists.')
        expect(onboarding.existing_value('Previous Client Name')).to_have_text(name)
        document_number = onboarding.existing_value('Document Number').inner_text().strip()
        assert document_number, 'Document number must be populated'
        # Optional exact identity verification requires a known fixture value.
        expected_doc = os.getenv('EXISTING_INDIVIDUAL_DOCUMENT' if kind == 'individual' else 'EXISTING_ENTITY_DOCUMENT')
        if expected_doc:
            assert document_number == expected_doc
        expect(onboarding.existing_okay()).to_be_enabled()
        onboarding.existing_okay().click()
        expect(onboarding.existing).to_be_hidden()
        expect(onboarding.consent).to_be_visible()
