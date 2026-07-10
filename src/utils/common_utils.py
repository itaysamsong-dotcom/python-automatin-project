import re
from dataclasses import asdict, is_dataclass
from typing import Any, Pattern

from playwright.sync_api import Page

from src.models.types import FieldMap


def fill_text_fields(page: Page, data: Any, selectors: FieldMap) -> None:
    values = asdict(data) if is_dataclass(data) else data
    for key, selector in selectors.items():
        page.get_by_test_id(selector).fill(values[key].strip())


def endpoint(path: str) -> Pattern[str]:
    return re.compile(f"{re.escape(path)}$")
