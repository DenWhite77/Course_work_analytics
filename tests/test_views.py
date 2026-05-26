import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import pytest
from src.views import main_page, events_page


def test_main_page_returns_json():
    result = main_page("2021-12-31 23:59:59")
    data = json.loads(result)
    assert "greeting" in data
    assert "cards" in data
    assert "top_transactions" in data
    assert "currency_rates" in data
    assert "stock_prices" in data


def test_events_page_returns_json():
    result = events_page("2021-12-31 23:59:59", "M")
    data = json.loads(result)
    assert "expenses" in data
    assert "income" in data
    assert "currency_rates" in data
    assert "stock_prices" in data

