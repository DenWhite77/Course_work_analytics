"""
Утилиты для работы с JSON-файлами.
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any


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


def read_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с транзакциями.

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Список словарей. При ошибке, пустом файле или не-списке — пустой список.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, IOError):
        return []
