"""
Утилиты для работы с JSON-файлами.
"""

import json
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")


def read_excel_operations(file_path: str) -> List[Dict[str, Any]]:
    """Читает Excel-файл с транзакциями и возвращает список словарей."""
    df = pd.read_excel(file_path)
    # Заменяем NaN на None для корректной JSON-сериализации
    return df.where(pd.notnull(df), None).to_dict(orient='records')

def filter_by_date_range(transactions: List[Dict[str, Any]], date_str: str, period: str = 'M') -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции в зависимости от периода.
    period: 'W' (неделя), 'M' (месяц), 'Y' (год), 'ALL' (все данные до указанной даты)
    """
    target_date = datetime.strptime(date_str[:10], '%Y-%m-%d')

    if period == 'W':
        start_date = target_date - timedelta(days=target_date.weekday())
    elif period == 'M':
        start_date = target_date.replace(day=1)
    elif period == 'Y':
        start_date = target_date.replace(month=1, day=1)
    elif period == 'ALL':
        start_date = datetime.min
    else:
        start_date = target_date.replace(day=1)

    result = []
    for t in transactions:
        t_date_str = t.get('Дата операции', '')[:10]
        if not t_date_str:
            continue
        try:
            t_date = datetime.strptime(t_date_str, '%d.%m.%Y')
            if start_date <= t_date <= target_date:
                result.append(t)
        except:
            continue
    return result


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от текущего времени."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют через публичное API."""
    rates = []
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        data = response.json()
        for curr in currencies:
            rate = data.get('rates', {}).get(curr, 0)
            rates.append({"currency": curr, "rate": round(rate, 2)})
    except Exception:
        # Заглушка при ошибке API
        for curr in currencies:
            rates.append({"currency": curr, "rate": 0.0})
    return rates


def get_stock_prices(stocks: list) -> list:
    """Получает реальные цены акций через Alpha Vantage API."""
    prices = []
    for stock in stocks:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={ALPHA_VANTAGE_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                price = float(data["Global Quote"]["05. price"])
                prices.append({"stock": stock, "price": round(price, 2)})
            else:
                prices.append({"stock": stock, "price": 0.0})
        except Exception:
            prices.append({"stock": stock, "price": 0.0})
    return prices
