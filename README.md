# Sentinel Automation

This project uses **Python + Playwright + pytest** to automate testing of the Sentinel web application.

The framework includes:
- **UI Tests** — Check page elements, buttons, inputs, tables, and forms.
- **Functional Tests** — Check application workflows and functionality.
- **Page Objects** — Store locators and reusable actions separately from tests.

## 1. Project Setup (One-Time Only)

Follow these steps when setting up the project on a new laptop.

### Step 1 — Install Required Tools

Install:
- Python
- Git
- PyCharm or VS Code

Check the installations in PowerShell:

```powershell
python --version
git --version
```

### Step 2 — Clone the Project from GitHub

```powershell
git clone https://github.com/OshadhaNL/sentinel-automation.git
cd sentinel-automation
```

If the project is already on your laptop, simply open the `sentinel-automation` folder.

### Step 3 — Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see `(.venv)` in your terminal.

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Step 4 — Install Python Packages

```powershell
python -m pip install -r requirements.txt
```

If `requirements.txt` is not available yet:

```powershell
python -m pip install playwright pytest pytest-playwright python-dotenv requests pytest-html pytest-xdist
```

Install the Playwright Chromium browser:

```powershell
python -m playwright install chromium
```

### Step 5 — Configure Login Credentials

Create a `.env` file in the project root.

Add your QA login credentials:

```env
TEST_EMAIL=your-test-email
TEST_PASSWORD=your-test-password
```

Make sure `.env` is included in `.gitignore`. Never push credentials to GitHub.

### Step 6 — Check Everything

```powershell
python -m pytest --version
python -m playwright --version
python -m pip check
```

Your project is now ready.

---

## 2. Daily Commands (Use Every Day)

Open PowerShell in the `sentinel-automation` project folder.

### Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Check Your Git Branch

```powershell
git branch
git status
```

### Get the Latest Changes

```powershell
git pull
```

### Run Your Tests

```powershell
python -m pytest tests/ui -v
```

### Deactivate the Virtual Environment

```powershell
deactivate
```

---

## 3. Run Automation Tests

### Run All Tests (Headless)

```powershell
python -m pytest -v
```

Headless means the browser runs without opening a visible window.

### Run All Tests (Visible Browser)

```powershell
python -m pytest -v --headed
```

### Run Only UI Tests

```powershell
python -m pytest tests/ui -v
```

### Run Only Functional Tests

```powershell
python -m pytest tests/functions -v
```

### Run Only Authentication Tests

```powershell
python -m pytest tests/auth -v
```

### Run a Specific Test File

Example — Transaction page:

```powershell
python -m pytest tests/ui/test_transaction_page.py -v
```

Example — Onboarding page:

```powershell
python -m pytest tests/ui/test_onboarding_page.py -v
```

### Run a Specific Test

```powershell
python -m pytest tests/ui/test_transaction_page.py -k "test_dates_sorted_ascending" -v
```

### Run Multiple Selected Tests

```powershell
python -m pytest tests/ui/test_transaction_page.py -k "search or sorting" -v
```

Replace `search` and `sorting` with keywords from your test names.

### Run Smoke Tests

```powershell
python -m pytest -m smoke -v
```

### Run Tests Slowly (For Debugging)

```powershell
python -m pytest tests/ui -v --headed --slowmo 500
```

### Run Tests in Parallel (Faster Execution)

```powershell
python -m pytest tests/ui -n 4 -v
```

This uses four parallel workers. Make sure `pytest-xdist` is installed.

### Run Tests and Show Print Statements

```powershell
python -m pytest tests/ui -v -s
```

### Stop After the First Failure

```powershell
python -m pytest tests/ui -x -v
```

### Show Only a Short Error Report

```powershell
python -m pytest tests/ui -v --tb=short
```

---

## 4. Generate HTML Test Reports

Create the reports folder once:

```powershell
New-Item -ItemType Directory -Force reports
```

### Run All Tests and Generate a Report

```powershell
python -m pytest -v --html=reports/report.html --self-contained-html
```

### Run UI Tests and Generate a Report

```powershell
python -m pytest tests/ui -v --html=reports/ui-report.html --self-contained-html
```

### Run Tests in Parallel and Generate a Report

```powershell
python -m pytest tests/ui -n 4 -v --html=reports/ui-report.html --self-contained-html
```

Open the generated HTML file from the `reports` folder to view the results.

---

## 5. GitHub Commands

Use these commands to save your automation changes to GitHub.

### Check Your Current Branch

```powershell
git branch
```

### Create a New Branch (One-Time Per Branch)

```powershell
git switch -c your-branch-name
```

### Switch to Your Branch

Example:

```powershell
git switch oshadha
```

### Check Changed Files

```powershell
git status
```

### Add Changed Files

```powershell
git add .
```

### Commit Changes

```powershell
git commit -m "Added transaction automation tests"
```

### Push Changes to GitHub

First push of a new branch:

```powershell
git push -u origin your-branch-name
```

For later pushes:

```powershell
git push
```

### Get Latest Changes

```powershell
git pull
```

### Merge Your Branch into Main

The recommended method is to create a **Pull Request on GitHub** and merge it after review.

Alternatively, to merge locally:

```powershell
git switch main
git pull origin main
git merge oshadha
git push origin main
```

Replace `oshadha` with your branch name if different. Resolve any merge conflicts before pushing.

---

## 6. Useful Troubleshooting Commands

### Check Python Version

```powershell
python --version
```

### Check Installed Packages

```powershell
python -m pip list
```

### Check for Broken Dependencies

```powershell
python -m pip check
```

### Reinstall Playwright Chromium

```powershell
python -m playwright install chromium
```

### Check Python Syntax Without Running Tests

```powershell
python -m py_compile tests/ui/test_transaction_page.py pages/transactionPage.py
```

### Check Test Collection

```powershell
python -m pytest --collect-only -q
```

### Show Detailed Errors

```powershell
python -m pytest -vv --tb=long
```

### Update Dependencies

After intentionally changing the project's installed packages:

```powershell
python -m pip freeze > requirements.txt
```

Review the changes before committing `requirements.txt`.

---

## 7. Project Folder Structure

```text
sentinel-automation/
│
├── config/             # Application settings
├── pages/              # Page locators and reusable actions
├── components/         # Reusable UI components
├── workflows/          # Reusable business workflows
├── utils/              # Helper functions
├── test_data/          # Test data
│
├── tests/
│   ├── ui/             # UI tests
│   ├── functions/      # Functional tests
│   └── auth/           # Authentication tests
│
├── reports/            # Test reports
├── .env                # Login credentials (do not commit)
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 8. Quick Command Cheat Sheet

| What you want to do | Command |
|---|---|
| Activate environment | `.\.venv\Scripts\Activate.ps1` |
| Run all tests | `python -m pytest -v` |
| Run tests with browser visible | `python -m pytest -v --headed` |
| Run UI tests | `python -m pytest tests/ui -v` |
| Run functional tests | `python -m pytest tests/functions -v` |
| Run tests in parallel | `python -m pytest -n 4 -v` |
| Run smoke tests | `python -m pytest -m smoke -v` |
| Generate HTML report | `python -m pytest -v --html=reports/report.html --self-contained-html` |
| Check branch | `git branch` |
| Check changes | `git status` |
| Get latest changes | `git pull` |
| Stage changes | `git add .` |
| Commit changes | `git commit -m "Your message"` |
| Push changes | `git push` |

---

## 9. Important Notes

- Always activate `.venv` before running tests.
- Run commands from the project root folder.
- Keep your `.env` file and passwords out of GitHub.
- Do not commit `.venv`, generated reports, or temporary test files.
- Use the QA/staging environment for automation testing.
- Keep locators and reusable actions in `pages/`.
- Keep test scenarios and assertions in `tests/`.
- Use a separate Git branch for your changes and merge into `main` through a Pull Request when ready.
