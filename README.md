# Sentinel Automation — Command Reference

## 1. Clone the GitHub Repository

If you have not cloned the repository to your laptop yet:

```powershell
git clone https://github.com/OshadhaNL/sentinel-automation.git
cd sentinel-automation
```

If you already have the project locally, open the project folder instead.

## 2. Check Installed Tools

```powershell
python --version
python -m pip --version
git --version
```

Check Playwright and pytest:

```powershell
python -m playwright --version
python -m pytest --version
```

## 3. Create a Python Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Deactivate it when finished:

```powershell
deactivate
```

> When the environment is active, the terminal prompt displays `(.venv)`.

## 4. Install Project Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the required packages:

```powershell
python -m pip install playwright pytest pytest-playwright python-dotenv requests pytest-html
```

Install the Chromium browser:

```powershell
python -m playwright install chromium
```

Check the installed browser:

```powershell
python -m playwright install --list
```

Check installed dependencies:

```powershell
python -m pip list
python -m pip check
```

Save installed package versions to `requirements.txt`:

```powershell
python -m pip freeze > requirements.txt
```

Install dependencies later from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 5. Create the Project Folder Structure

Run these commands from the project root:

```powershell
New-Item -ItemType Directory -Force -Path config, pages, components, workflows, utils, test_data, tests, tests\ui, tests\functions, tests\auth
```

Create Python package marker files if required by the project structure:

```powershell
New-Item -ItemType File -Force -Path config\__init__.py, pages\__init__.py, components\__init__.py, workflows\__init__.py, utils\__init__.py, tests\__init__.py, tests\ui\__init__.py, tests\functions\__init__.py, tests\auth\__init__.py
```

## 6. Run Automated Tests

Run all tests:

```powershell
python -m pytest
```

Run tests with detailed output:

```powershell
python -m pytest -v
```

Run UI tests:

```powershell
python -m pytest tests/ui -v
```

Run functional tests:

```powershell
python -m pytest tests/functions -v
```

Run authentication tests:

```powershell
python -m pytest tests/auth -v
```

Run a specific test file:

```powershell
python -m pytest tests/ui/test_example_page.py -v
```

Run a specific test function:

```powershell
python -m pytest tests/ui/test_example_page.py::test_example_heading_is_visible -v
```

Run tests marked as smoke tests:

```powershell
python -m pytest -m smoke -v
```

Run UI-marked tests:

```powershell
python -m pytest -m ui -v
```

Run functional-marked tests:

```powershell
python -m pytest -m functional -v
```

Run tests in a visible browser:

```powershell
python -m pytest tests/ui -v --headed
```

Run tests in headless mode:

```powershell
python -m pytest tests/ui -v
```

Run tests with a slower browser interaction speed:

```powershell
python -m pytest tests/ui -v --headed --slowmo 500
```

## 7. Generate Test Reports

Create the reports folder:

```powershell
New-Item -ItemType Directory -Force reports
```

Generate an HTML report:

```powershell
python -m pytest -v --html=reports/report.html --self-contained-html
```

Run a particular test folder and generate a report:

```powershell
python -m pytest tests/ui -v --html=reports/ui-report.html --self-contained-html
```

## 8. Useful Debugging Commands

Show pytest fixtures:

```powershell
python -m pytest --fixtures
```

Show registered test markers:

```powershell
python -m pytest --markers
```

Collect tests without executing them:

```powershell
python -m pytest --collect-only -v
```

Stop after the first test failure:

```powershell
python -m pytest -x -v
```

Show more detailed test output:

```powershell
python -m pytest -vv
```

Run tests with Playwright tracing configured in `pytest.ini`:

```powershell
python -m pytest tests/ui -v
```

## 9. Git Commands

Check the current branch and working-tree status:

```powershell
git status
git branch
```

Download the latest changes from GitHub:

```powershell
git pull
```

Fetch all remote branch information:

```powershell
git fetch --all
```

Create a new feature branch:

```powershell
git switch -c feature/your-feature-name
```

Switch to an existing branch:

```powershell
git switch your-branch-name
```

Stage all changes:

```powershell
git add .
```

Commit your changes:

```powershell
git commit -m "Add automation framework setup"
```

Push your branch to GitHub for the first time:

```powershell
git push -u origin your-branch-name
```

Push subsequent commits:

```powershell
git push
```

View recent commits:

```powershell
git log --oneline
```

View remote repositories:

```powershell
git remote -v
```

## 10. Merge Your Feature Branch into Main

**Recommended:** Open a Pull Request on GitHub, review the changes, and merge it into `main`.

To merge locally instead, first commit and push your feature branch, then run:

```powershell
git switch main
git pull origin main
git merge your-branch-name
git push origin main
```

Replace `your-branch-name` with your actual branch name. Resolve any merge conflicts before pushing.

## 11. Environment and Configuration Checks

Check which Python executable is active:

```powershell
python -c "import sys; print(sys.executable)"
```

Check the installed versions of the main packages:

```powershell
python -m pip show playwright
python -m pip show pytest
python -m pip show pytest-playwright
```

Check the Python package dependencies:

```powershell
python -m pip check
```

## 12. Common Troubleshooting Commands

If PowerShell cannot activate the virtual environment, try:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If the virtual environment does not exist, create it first:

```powershell
python -m venv .venv
```

If Playwright browsers are missing:

```powershell
python -m playwright install chromium
```

If a package is missing:

```powershell
python -m pip install package-name
```

If pytest cannot find the Playwright `page` fixture:

```powershell
python -m pip install pytest-playwright
```

Then run:

```powershell
python -m pytest --fixtures
```

If imports or test collection fail, confirm that the terminal is in the project root and that the correct virtual environment is activated.

## 13. Recommended Daily Workflow

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Check the current branch:

```powershell
git status
git branch
```

Pull the latest changes for your current branch:

```powershell
git pull
```

Run the relevant tests:

```powershell
python -m pytest tests/ui -v
```

Stage and commit your changes:

```powershell
git add .
git commit -m "Describe your changes"
```

Push your work:

```powershell
git push
```

## Important Notes

- Run project commands from the `sentinel-automation` root directory unless otherwise specified.
- Activate `.venv` before installing packages or running tests.
- Keep `.venv/`, `.env`, authentication state files, reports, and test artifacts out of Git unless a specific artifact is intentionally meant to be shared.
- Keep credentials and secrets in environment variables; never commit real passwords, tokens, or private test data.
- Configure `BASE_URL` to point to the approved test or staging environment. Avoid running registration, deletion, or other state-changing tests against production without explicit authorization.
- Use the repository's `requirements.txt` as the dependency source of truth and update it intentionally when dependencies change.
