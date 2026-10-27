
import re

from playwright.sync_api import Page, expect


class DashboardPage:

    def __init__(self, page: Page):
        self.page = page

        # =====================================
        # Dashboard
        # =====================================

        self.dashboard_heading = page.get_by_role(
            "heading", name="Dashboard", exact=True
        )

        self.ongoing_card = self.get_card("Ongoing Onboarding")
        self.individual_card = self.get_card("Individuals")
        self.company_card = self.get_card("Companies")

        self.ongoing_icon = self.ongoing_card.locator(
            ".fa-clipboard-list-check"
        )
        self.individual_icon = self.individual_card.locator(
            ".fa-user-tie"
        )
        self.company_icon = self.company_card.locator(
            ".fa-building"
        )

        # Charts
        self.risk_card = self.get_card("Client Risk Breakdown")
        self.onboarding_chart_card = self.get_card("Onboarding")

        self.risk_chart = self.risk_card.locator("canvas")
        self.onboarding_chart = self.onboarding_chart_card.locator("canvas")

        # Documents
        self.documents_card = self.get_card("Documents")
        self.documents_table = self.documents_card.locator(".ant-table")
        self.documents_headers = self.documents_table.locator("thead th")
        self.client_id_links = self.documents_table.locator(
            "tbody tr td:first-child a"
        )

        # =====================================
        # Pending Onboarding
        # =====================================

        self.pending_tab = page.locator(".tab-z-option").filter(
            has_text="Pending Onboarding"
        )

        self.pending_table = page.locator(".ant-table").filter(
            has=page.get_by_role(
                "columnheader", name="Reference ID", exact=True
            )
        )

        # =====================================
        # Profiles -> All Files
        # =====================================

        self.profiles_heading = page.get_by_role(
            "heading", name="Profiles", exact=True
        )

        self.all_files_tab = page.locator(".tab-z-option").filter(
            has_text="All Files"
        )

        self.profiles_table = page.locator(".ant-table").filter(
            has=page.get_by_role(
                "columnheader", name="Client ID", exact=True
            )
        )

    # =====================================
    # Common helpers
    # =====================================

    def get_card(self, heading):
        return self.page.locator(".dashboard-card").filter(
            has=self.page.get_by_role(
                "heading", name=heading, exact=True
            )
        )

    def _open_sidebar_page(self, name):
        self.page.get_by_role(
            "link", name=re.compile(re.escape(name), re.I)
        ).click()

    def _get_table_pagination(self, table):
        """
        Locate pagination inside the Ant Design table wrapper.
        """
        wrapper = table.locator(
            "xpath=ancestor::div[contains("
            "concat(' ', normalize-space(@class), ' '), "
            "' ant-table-wrapper ')][1]"
        )

        return wrapper.locator("ul.ant-table-pagination")

    def _read_paginated_records(self, table, columns, label):
        """
        Read all records from a paginated Ant Design table.

        - Waits for the first page to load.
        - Reads all rows.
        - Clicks Next until disabled.
        - Waits for table data to change.
        - Checks for duplicate IDs.
        """

        records = []
        visited_pages = set()

        expect(table).to_be_visible(timeout=20000)

        rows = table.locator("tbody tr.ant-table-row")
        pagination = self._get_table_pagination(table)

        # Both tables are expected to contain records.
        expect(rows.first).to_be_visible(timeout=20000)

        while True:

            if pagination.count() == 0:
                active_page = "1"
            else:
                active_page = pagination.locator(
                    ".ant-pagination-item-active"
                ).inner_text().strip()

            assert active_page not in visited_pages, (
                f"{label}: repeated pagination page {active_page}"
            )

            visited_pages.add(active_page)

            expect(rows.first).to_be_visible()

            page_records = []

            for index in range(rows.count()):
                cells = rows.nth(index).locator("td")

                if cells.count() <= max(columns.values()):
                    continue

                record = {
                    key: cells.nth(position).inner_text().strip()
                    for key, position in columns.items()
                }

                page_records.append(record)

            assert page_records, (
                f"{label}: no records found on page {active_page}"
            )

            print(
                f"{label} page {active_page}: "
                f"{len(page_records)} records"
            )

            records.extend(page_records)

            if pagination.count() == 0:
                break

            next_button = pagination.locator(
                ".ant-pagination-next"
            )

            next_disabled = (
                next_button.get_attribute("aria-disabled") == "true"
                or "ant-pagination-disabled" in (
                    next_button.get_attribute("class") or ""
                )
            )

            if next_disabled:
                break

            previous_ids = [
                record["reference_id"]
                for record in page_records
            ]

            next_button.click()

            # Wait for active page number to change
            expect(
                pagination.locator(
                    ".ant-pagination-item-active"
                )
            ).not_to_have_text(active_page)

            # Wait for actual table data to change.
            table.evaluate(
                """
                (element, previousIds) => new Promise(
                    (resolve, reject) => {

                        const readIds = () =>
                            Array.from(
                                element.querySelectorAll(
                                    "tbody tr.ant-table-row"
                                )
                            ).map(row => {
                                const cell = row.querySelector(
                                    "td:first-child"
                                );

                                return cell
                                    ? cell.innerText.trim()
                                    : "";
                            });

                        const changed = () =>
                            JSON.stringify(readIds()) !==
                            JSON.stringify(previousIds);

                        if (changed()) {
                            resolve();
                            return;
                        }

                        const observer = new MutationObserver(() => {
                            if (changed()) {
                                observer.disconnect();
                                resolve();
                            }
                        });

                        observer.observe(element, {
                            childList: true,
                            subtree: true,
                            characterData: true
                        });

                        setTimeout(() => {
                            observer.disconnect();
                            reject(
                                new Error(
                                    "Table records did not change"
                                )
                            );
                        }, 20000);
                    }
                )
                """,
                previous_ids
            )

        reference_ids = [
            record["reference_id"] for record in records
        ]

        assert len(reference_ids) == len(set(reference_ids)), (
            f"{label}: duplicate Reference IDs found"
        )

        print(f"{label} total records: {len(records)}")

        return records

    # =====================================
    # Dashboard navigation
    # =====================================

    def open_dashboard(self):
        self._open_sidebar_page("Dashboard")
        self.verify_dashboard_heading()

    def verify_dashboard_heading(self):
        expect(self.dashboard_heading).to_be_visible()

    # =====================================
    # Dashboard cards
    # =====================================

    def verify_ongoing_card_visible(self):
        expect(self.ongoing_card).to_be_visible()

    def verify_individual_card_visible(self):
        expect(self.individual_card).to_be_visible()

    def verify_company_card_visible(self):
        expect(self.company_card).to_be_visible()

    def get_card_count(self, card):
        count_locator = card.locator("h3")

        expect(card).to_be_visible()
        expect(count_locator).to_be_visible()

        # Wait for data to replace initial zero.
        # Appropriate for current QA dataset.
        expect(count_locator).to_have_text(
            re.compile(r"^[1-9][0-9,]*$"),
            timeout=20000
        )

        return int(
            count_locator.inner_text().strip().replace(",", "")
        )

    def get_ongoing_count(self):
        return self.get_card_count(self.ongoing_card)

    def get_individual_count(self):
        return self.get_card_count(self.individual_card)

    def get_company_count(self):
        return self.get_card_count(self.company_card)

    # =====================================
    # Icons
    # =====================================

    def verify_ongoing_icon(self):
        expect(self.ongoing_icon).to_be_visible()

    def verify_individual_icon(self):
        expect(self.individual_icon).to_be_visible()

    def verify_company_icon(self):
        expect(self.company_icon).to_be_visible()

    # =====================================
    # Charts
    # =====================================

    def verify_risk_chart_visible(self):
        expect(self.risk_card).to_be_visible()
        expect(self.risk_chart).to_be_visible()

    def verify_onboarding_chart_visible(self):
        expect(self.onboarding_chart_card).to_be_visible()
        expect(self.onboarding_chart).to_be_visible()

    def get_pie_chart_colors(self):
        expect(self.onboarding_chart).to_be_visible()

        return self.onboarding_chart.evaluate("""
            canvas => {
                const ctx = canvas.getContext("2d");
                const image = ctx.getImageData(
                    0, 0, canvas.width, canvas.height
                );

                const pixels = image.data;
                let pink = 0;
                let purple = 0;

                for (let i = 0; i < pixels.length; i += 4) {
                    if (pixels[i + 3] < 200) continue;

                    const r = pixels[i] / 255;
                    const g = pixels[i + 1] / 255;
                    const b = pixels[i + 2] / 255;

                    const max = Math.max(r, g, b);
                    const min = Math.min(r, g, b);
                    const delta = max - min;

                    if (delta < 0.15 || max === 0) continue;

                    const saturation = delta / max;
                    if (saturation < 0.25) continue;

                    let hue = 0;

                    if (max === r) {
                        hue = ((g - b) / delta) % 6;
                    } else if (max === g) {
                        hue = (b - r) / delta + 2;
                    } else {
                        hue = (r - g) / delta + 4;
                    }

                    hue = ((hue * 60) + 360) % 360;

                    if (hue >= 325 && hue <= 350) pink++;
                    if (hue >= 270 && hue < 325) purple++;
                }

                return {pink, purple};
            }
        """)

    def verify_in_progress_pink(self):
        colors = self.get_pie_chart_colors()

        assert colors["pink"] > 50, (
            f"Pink pie-chart section not detected: {colors}"
        )

    def verify_closed_purple(self):
        colors = self.get_pie_chart_colors()

        assert colors["purple"] > 50, (
            f"Purple pie-chart section not detected: {colors}"
        )

    # =====================================
    # Documents
    # =====================================

    def verify_documents_heading(self):
        expect(
            self.documents_card.get_by_role(
                "heading", name="Documents", exact=True
            )
        ).to_be_visible()

    def verify_documents_table_visible(self):
        expect(self.documents_table).to_be_visible()

    def verify_document_header(self, position, expected_text):
        expect(
            self.documents_headers.nth(position - 1)
        ).to_have_text(expected_text)

    def click_first_client_id(self):
        expect(self.client_id_links.first).to_be_visible()

        client_id = self.client_id_links.first.inner_text().strip()
        self.client_id_links.first.click()

        return client_id

    def verify_client_kyc_navigation(self, client_id):
        expect(self.page).to_have_url(
            re.compile(
                r"/nolimit/app/onboarding/"
                r"(individual|entity)/process"
                r"\?step=kyc-form&client="
                + re.escape(client_id)
                + r"(?:&.*)?$"
            )
        )

    # =====================================
    # Pending Onboarding
    # =====================================

    def open_pending_onboarding(self):
        self._open_sidebar_page("Onboarding")

        expect(
            self.page.get_by_role(
                "heading", name="Onboarding", exact=True
            )
        ).to_be_visible()

        self.pending_tab.click()

        expect(self.pending_table).to_be_visible()

    def get_all_pending_records(self):
        return self._read_paginated_records(
            self.pending_table,
            columns={
                "reference_id": 0,
                "type": 2,
                "status": 3
            },
            label="Pending Onboarding"
        )

    def get_pending_onboarding_counts(self):
        records = self.get_all_pending_records()

        return {
            "ongoing": sum(
                1 for r in records
                if r["status"].casefold() == "ongoing"
            ),
            "individuals": sum(
                1 for r in records
                if r["type"].casefold() == "individual"
            ),
            "companies": sum(
                1 for r in records
                if r["type"].casefold() == "entity"
            ),
            "total": len(records)
        }

    # =====================================
    # Profiles -> All Files
    # =====================================

    def open_profiles_all_files(self):
        self._open_sidebar_page("Profiles")

        expect(self.profiles_heading).to_be_visible()

        self.all_files_tab.click()

        expect(self.profiles_table).to_be_visible()

    def get_all_profiles_records(self):
        return self._read_paginated_records(
            self.profiles_table,
            columns={
                "reference_id": 0,
                "type": 2,
                "status": 3
            },
            label="Profiles All Files"
        )

    def get_profiles_counts(self):
        records = self.get_all_profiles_records()

        completed = [
            r for r in records
            if r["status"].casefold() == "onboarded"
        ]

        return {
            "individuals": sum(
                1 for r in completed
                if r["type"].casefold() == "individual"
            ),
            "companies": sum(
                1 for r in completed
                if r["type"].casefold() == "entity"
            ),
            "total": len(completed)
        }
