"""Page object for Profile - Individual > Risk Assessment (Playwright sync)."""
import re
from playwright.sync_api import expect


class IndividualRiskAssessmentPage:
    FACTORS = {
        'country': {'low': ('Low risk countries per Basel AML Index (3.33 or lower)', 1), 'other': ('Other countries and jurisdictions', 3), 'high': ('High risk countries as per Basel AML Index (6.67 or higher)', 5)},
        'pep': {'nonPep': ('Not a Politically Exposed Person', 1), 'associate': ('Associate of a Politically Exposed Person', 3), 'pep': ('Politically Exposed Person', 5)},
        'residence': {'residence': ('Residence', 1), 'nonResidence': ('Non-Residence', 3)},
        'funds': {'bankTransfer': ('Bank Transfers', 1), 'cash': ('Cash Transactions', 3)},
        'media': {'noHits': ('No Hits', 1), 'confirmed': ('Confirmed Adverse Media Hits', 3)},
    }
    SECTIONS = ('Country / Jurisdiction Risk', 'Individual Risk', 'Australian Residential Status', 'Transfer of Funds', 'Adverse Media', 'Risk Assessment Summary', 'Approval')
    HEADERS = ('Risk Factor', 'Attribute', 'Risk Score')
    APPROVAL_HEADERS = ('Name', 'Role', 'Date', 'Signature')

    def __init__(self, page):
        self.page = page

    @property
    def heading(self):
        return self.page.get_by_role('heading', name='Profile - Individual', exact=True)

    def open(self):
        self.page.evaluate("window.__riskAssessmentReadiness = null")
        self.page.locator(".tab-z-option").filter(
            has_text="Risk Assessment"
        ).click()

        expect(
            self.page.get_by_text(
                "Risk Assessment Summary",
                exact=True
            )
        ).to_be_visible()

        self.wait_until_risk_loaded()

    def section(self, title):
        return self.page.locator('.section-header h6').filter(has_text=re.compile(r'^\s*' + re.escape(title) + r'\s*$'))

    def factor_group(self, factor):
        if factor not in self.FACTORS:
            raise KeyError(factor)
        label = {'country': 'Country / Jurisdiction Risk', 'pep': 'Politically Exposed Person (PEP) Status', 'residence': 'Australian Residential Status', 'funds': 'Transfer of Funds', 'media': 'Adverse Media'}[factor]
        box = self.page.locator('.border-box').filter(has=self.page.locator('.border-box-label', has_text=re.compile(r'^\s*' + re.escape(label) + r'\s*$')))
        return box.locator('.ant-radio-group')

    def option(self, factor, value):
        if value not in self.FACTORS[factor]:
            raise KeyError((factor, value))
        return self.factor_group(factor).locator('input.ant-radio-input[type="radio"][value="' + value + '"]')

    def select(self, factor, value):
        radio = self.option(factor, value)

        expect(radio).to_be_attached(timeout=10000)
        expect(radio).to_be_enabled(timeout=10000)

        if radio.is_checked():
            print(f"Already selected: {factor} = {value}")
            return

        print(f"Selecting: {factor} = {value}")

        label = radio.locator("xpath=ancestor::label[1]")
        expect(label).to_be_visible(timeout=10000)
        label.click()

        expect(radio).to_be_checked(timeout=10000)

        print(f"Selection confirmed: {factor} = {value}")

    def selected(self, factor):
        return self.factor_group(factor).locator('input.ant-radio-input[type="radio"]:checked').get_attribute('value')

    def current_choices(self):
        return {factor: self.selected(factor) for factor in self.FACTORS}

    def select_choices(self, choices):
        """Select factors and detect unexpected changes to earlier selections."""
        applied = {}
        for factor, value in choices.items():
            self.select(factor, value)
            applied[factor] = value

            current = self.current_choices()
            for previous_factor, previous_value in applied.items():
                assert current[previous_factor] == previous_value, (
                    f"Selection reset after {factor} = {value}. "
                    f"Lost: {previous_factor} = {previous_value}. "
                    f"Current selections: {current}"
                )

            expected = self.expected_score(current)
            total_cell = (
                self.summary_table()
                .locator('tbody tr')
                .filter(has=self.page.get_by_text('Total Score', exact=True))
                .locator('td').last
            )
            expect(total_cell).to_have_text(str(expected), timeout=10000)

    @classmethod
    def expected_score(cls, choices):
        return sum(cls.FACTORS[factor][value][1] for factor, value in choices.items())

    @staticmethod
    def expected_rating(score):
        return 'Low' if score <= 5 else 'Medium' if score <= 15 else 'High'

    def summary_table(self):
        return self.page.locator('table.signature-table').filter(has=self.page.locator('th', has_text='Risk Factor'))

    def range_table(self):
        return self.page.locator('table.signature-table').filter(has=self.page.locator('th', has_text='Risk Rating Range'))

    def approval_table(self):
        return self.page.locator('table.signature-table').filter(has=self.page.locator('th', has_text=re.compile(r'^\s*Signature\s*$')))

    def summary_row(self, attribute):
        return self.summary_table().locator('tbody tr').filter(has=self.page.locator('td:nth-child(1), td:nth-child(2)', has_text=re.compile(r'^\s*' + re.escape(attribute) + r'\s*$')))

    def attribute_row(self, attribute):
        # Attribute may appear in the first or second TD because factor labels use rowspan.
        return self.summary_table().locator('tbody tr').filter(has=self.page.locator('td', has_text=re.compile(r'^\s*' + re.escape(attribute) + r'\s*$')))

    def total_score(self):
        row = self.summary_table().locator('tbody tr').filter(has=self.page.get_by_text('Total Score', exact=True))
        return int(row.locator('td').last.inner_text().strip())

    def classification(self):
        label = self.page.get_by_text(re.compile(r'^Risk Classification:\s*(Low|Medium|High)\s*$'))
        return label.inner_text().split(':', 1)[1].strip()

    def diagnostic_snapshot(self):
        """Useful failure context without weakening assertions."""
        selected = self.current_choices()
        rows = []
        for factor, value in selected.items():
            label, expected_points = self.FACTORS[factor][value]
            row = self.attribute_row(label)
            rows.append({
                'factor': factor, 'selected': value,
                'expected_points': expected_points,
                'summary_points': row.locator('td').last.inner_text().strip() if row.count() == 1 else 'row missing',
                'row_class': row.get_attribute('class') if row.count() == 1 else 'row missing',
            })
        return {'choices': selected, 'expected_total': self.expected_score(selected),
                'displayed_total': self.total_score(), 'displayed_rating': self.classification(),
                'rows': rows}

    def assert_calculation(self, choices):
        # Verify actual selected radios before testing calculated output.
        for factor, value in choices.items():
            expect(self.option(factor, value)).to_be_checked()
        expected = self.expected_score(choices)
        total_cell = self.summary_table().locator('tbody tr').filter(
            has=self.page.get_by_text('Total Score', exact=True)
        ).locator('td').last
        try:
            expect(total_cell).to_have_text(str(expected), timeout=8000)
            expect(self.page.get_by_text(
                f'Risk Classification: {self.expected_rating(expected)}', exact=True
            )).to_be_visible(timeout=8000)
            for factor, value in choices.items():
                attribute, score = self.FACTORS[factor][value]
                row = self.attribute_row(attribute)
                expect(row).to_have_count(1)
                expect(row.locator('td').last).to_have_text(str(score))
                # Highlight is tested separately; it may be applied to a cell rather than tr.
        except AssertionError as error:
            raise AssertionError(
                f'{error}\nRisk assessment diagnostic: {self.diagnostic_snapshot()}'
            ) from error

    def update_button(self):
        return self.page.get_by_role('button', name='Update Changes', exact=True)

    def approval_signature(self):
        return self.approval_table().locator('tbody img[alt="Signature"]')

    def save(self):
        """Save risk assessment and verify the update response."""

        button = self.update_button()
        expect(button).to_be_enabled(timeout=10000)

        choices_before_save = self.current_choices()
        print(f"Saving risk choices: {choices_before_save}")

        def is_risk_update(response):
            request = response.request
            return (
                    "/risk-assessment" in response.url.lower()
                    and request.method.upper() in ("POST", "PUT", "PATCH")
                    and request.resource_type in ("xhr", "fetch")
            )

        with self.page.expect_response(
                is_risk_update,
                timeout=20000,
        ) as response_info:
            button.click()

        response = response_info.value
        request = response.request

        print(f"Save request: {request.method} {response.url}")
        print(f"Save request payload: {request.post_data}")
        print(f"Save response status: {response.status}")

        assert response.ok, (
            f"Risk assessment update failed: "
            f"HTTP {response.status}, URL: {response.url}"
        )

        print("Risk assessment update response received successfully.")

    def reload_and_open(self):
        self.page.reload(wait_until='domcontentloaded')
        expect(self.heading).to_be_visible(timeout=20000)
        self.open()

    def debug_radio_groups(self):
        print("\n===== RADIO GROUP DIAGNOSTICS =====")

        for factor in self.FACTORS:
            group = self.factor_group(factor)

            radios = group.locator(
                'input.ant-radio-input[type="radio"]'
            )

            print(f"\nFactor: {factor}")

            for i in range(radios.count()):
                radio = radios.nth(i)

                print({
                    "value": radio.get_attribute("value"),
                    "name": radio.get_attribute("name"),
                    "checked": radio.is_checked(),
                })

    def debug_selected_values(self):
        print("\n===== CURRENT RISK SELECTIONS =====")

        for factor in self.FACTORS:
            group = self.factor_group(factor)

            checked = group.locator(
                "input.ant-radio-input:checked"
            )

            print(
                f"{factor}: "
                f"{checked.get_attribute('value') if checked.count() else 'NONE'}"
            )

        print(f"Displayed total: {self.total_score()}")
        print(f"Classification: {self.classification()}")

    def debug_atomic_risk_snapshot(self):
        snapshot = self.page.evaluate("""
            () => {
                const boxes = [...document.querySelectorAll('.border-box')];

                const factors = boxes.map(box => {
                    const label = box.querySelector('.border-box-label');
                    const radios = [...box.querySelectorAll(
                        'input.ant-radio-input[type="radio"]'
                    )];

                    return {
                        factor: label?.textContent.trim(),
                        selected: radios
                            .filter(r => r.checked)
                            .map(r => r.value),
                        radioNames: [...new Set(
                            radios.map(r => r.name)
                        )]
                    };
                });

                const tables = [...document.querySelectorAll(
                    'table.signature-table'
                )];

                const summary = tables.find(table =>
                    table.textContent.includes('Total Score')
                );

                const totalRow = summary
                    ? [...summary.querySelectorAll('tr')].find(
                        row => row.textContent.includes('Total Score')
                      )
                    : null;

                return {
                    factors,
                    total: totalRow?.lastElementChild?.textContent.trim()
                };
            }
        """)

        print("\n===== ATOMIC RISK SNAPSHOT =====")
        print(snapshot)

        return snapshot

    def wait_until_risk_loaded(self, stable_ms=1200, timeout=20000):
        """Wait for all selections and their total to remain consistent and stable.

        This guards against the observed 200-500 ms UI hydration reset.
        It is a UI-based heuristic, not proof that all backend requests finished.
        """
        factor_values = {
            factor: {value: details[1] for value, details in options.items()}
            for factor, options in self.FACTORS.items()
        }

        self.page.wait_for_function(
            r"""
            ({factorValues, stableMs}) => {
                const names = {
                    'Country / Jurisdiction Risk': 'country',
                    'Politically Exposed Person (PEP) Status': 'pep',
                    'Australian Residential Status': 'residence',
                    'Transfer of Funds': 'funds',
                    'Adverse Media': 'media'
                };
                const selected = {};
                for (const box of document.querySelectorAll('.border-box')) {
                    const label = box.querySelector('.border-box-label')?.textContent.trim();
                    const factor = names[label];
                    if (!factor) continue;
                    const radio = box.querySelector('input.ant-radio-input:checked');
                    if (radio) selected[factor] = radio.value;
                }

                const table = [...document.querySelectorAll('table.signature-table')]
                    .find(t => t.textContent.includes('Total Score'));
                const row = [...(table?.querySelectorAll('tr') ?? [])]
                    .find(r => r.textContent.includes('Total Score'));
                const text = row?.lastElementChild?.textContent.trim();
                const actual = text === undefined ? NaN : Number(text);

                let valid = Object.keys(selected).length === 5;
                let expected = 0;
                if (valid) {
                    for (const [factor, value] of Object.entries(selected)) {
                        const points = factorValues[factor]?.[value];
                        if (points === undefined) { valid = false; break; }
                        expected += points;
                    }
                }
                valid = valid && Number.isFinite(actual) && actual === expected;

                // Persist between wait_for_function polls in this page context.
                const key = '__riskAssessmentReadiness';
                if (!valid) {
                    window[key] = null;
                    return false;
                }
                const signature = JSON.stringify({selected, actual});
                const now = performance.now();
                if (!window[key] || window[key].signature !== signature) {
                    window[key] = {signature, since: now};
                    return false;
                }
                return now - window[key].since >= stableMs;
            }
            """,
            arg={'factorValues': factor_values, 'stableMs': stable_ms},
            timeout=timeout,
            polling=100,
        )
        print(f"Risk Assessment UI stable for {stable_ms} ms: {self.current_choices()}")
