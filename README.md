# Python Test project

End-to-end test automation project built with Playwright and Python.

## Prerequisites

- Python 3.9 or newer

## Installation

Create and activate a virtual environment, then install the dependencies and Chromium:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
playwright install chromium
```

## Running tests

Run the complete suite:

```bash
pytest
```

Run with a visible browser:

```bash
pytest --headed
```

Run one test module:

```bash
pytest src/tests/test_login.py
```

The suite retries failures twice and writes screenshots/traces to `test-results/` and an HTML report to `playwright-report/report.html`.

## Allure reports

Every `pytest` run writes fresh Allure result files to `allure-results/`. Failure screenshots are automatically attached to the relevant Allure test.

Install the Allure command-line application on macOS (Java is required):

```bash
brew install allure
```

Run the tests and open an automatically generated report:

```bash
pytest
allure serve allure-results
```

To generate a persistent report instead:

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

## Project structure

```text
src/
├── config/       # Application and API routes
├── mapping/      # Test selectors and labels
├── models/       # Typed dataclasses and response shapes
├── test_data/    # Reusable users, products, and billing data
├── tests/        # Pytest test scenarios
└── utils/        # Browser actions and API helpers
```

Shared browser and product fixtures live in `conftest.py`. Test modules choose their starting route or product through pytest markers.
