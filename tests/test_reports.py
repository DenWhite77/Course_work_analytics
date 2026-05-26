import sys
from pathlib import Path

# Добавляем корень проекта в путь поиска модулей
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.reports import spending_by_category


def test_spending_by_category():
    data = [
        {"Дата операции": "02.10.2021", "Категория": "Супермаркеты", "Сумма платежа": -100},  # теперь входит
        {"Дата операции": "15.11.2021", "Категория": "Супермаркеты", "Сумма платежа": -200},
        {"Дата операции": "20.12.2021", "Категория": "Супермаркеты", "Сумма платежа": -50},
    ]
    result = spending_by_category(data, "Супермаркеты", "2021-12-31")
    assert result == 350.0


def test_spending_by_category_no_data():
    result = spending_by_category([], "Супермаркеты", "2021-12-31")
    assert result == 0.0


def test_spending_by_category_wrong_category():
    data = [
        {"Дата операции": "01.10.2021", "Категория": "Рестораны", "Сумма платежа": -500},
    ]
    result = spending_by_category(data, "Супермаркеты", "2021-12-31")
    assert result == 0.0
