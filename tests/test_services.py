import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.services import search_transactions, search_phone_numbers, investment_bank
from src.utils import read_excel_operations


@pytest.fixture
def sample_data():
    return [
        {"Описание": "Перевод клиенту", "Категория": "Переводы", "Сумма платежа": -1000},
        {"Описание": "Оплата услуг", "Категория": "Услуги", "Сумма платежа": -500},
        {"Описание": "Пополнение с карты", "Категория": "Пополнения", "Сумма платежа": 2000},
    ]


def test_search_transactions_found(sample_data):
    result = search_transactions(sample_data, "Перевод")
    assert len(result) == 1
    assert result[0]["Категория"] == "Переводы"


def test_search_transactions_not_found(sample_data):
    result = search_transactions(sample_data, "Кредит")
    assert result == []


def test_search_transactions_empty_query(sample_data):
    result = search_transactions(sample_data, "")
    assert result == []


def test_search_phone_numbers():
    data = read_excel_operations('data/operations.xlsx')
    result = search_phone_numbers(data)
    assert isinstance(result, list)


def test_investment_bank():
    data = read_excel_operations('data/operations.xlsx')
    result = investment_bank(data, 50)
    assert isinstance(result, float)
    assert result >= 0

