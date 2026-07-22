"""
Сервисы для работы с транзакциями: поиск, инвесткопилка и т.д.
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import read_excel_operations


def search_transactions(transactions: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Поиск по строке в описании или категории."""
    if not query:
        return []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    result = []
    for t in transactions:
        description = str(t.get('Описание', ''))
        category = str(t.get('Категория', ''))
        if pattern.search(description) or pattern.search(category):
            result.append(t)
    return result


def search_phone_numbers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Поиск транзакций с телефонными номерами в описании."""
    phone_pattern = re.compile(r'(\+7|8)[\s\-\(]*(\d{3})[\s\-\)]*(\d{3})[\s\-]*(\d{2})[\s\-]*(\d{2})')
    result = []
    for t in transactions:
        description = str(t.get('Описание', ''))
        if phone_pattern.search(description):
            result.append(t)
    return result


def investment_bank(transactions: List[Dict[str, Any]], limit: int) -> float:
    """Расчёт суммы для инвесткопилки (округление трат вверх до limit)."""
    total_saved = 0.0
    for t in transactions:
        amount = t.get('Сумма платежа', 0)
        if amount <= 0:
            continue
        rounded = ((amount + limit - 1) // limit) * limit
        total_saved += rounded - amount
    return total_saved


def search_main(query: str) -> str:
    """Упрощённый вызов поиска (только текст, возвращает JSON)."""
    transactions = read_excel_operations('data/operations.xlsx')
    found = search_transactions(transactions, query)
    return json.dumps(found, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    transactions = read_excel_operations('data/operations.xlsx')

    print("=== Поиск по строке 'Перевод' ===")
    found_by_text = search_transactions(transactions, "Перевод")
    print(f"Найдено транзакций: {len(found_by_text)}")
    print(json.dumps(found_by_text[:3], ensure_ascii=False, indent=2, default=str))
    print("\n" + "-" * 50 + "\n")

    print("=== Поиск транзакций с телефонными номерами ===")
    found_by_phone = search_phone_numbers(transactions)
    print(f"Найдено транзакций: {len(found_by_phone)}")
    print(json.dumps(found_by_phone[:3], ensure_ascii=False, indent=2, default=str))
    print("\n" + "-" * 50 + "\n")

    print("=== Инвесткопилка (шаг 50) ===")
    saved = investment_bank(transactions, 50)
    print(f"Можно отложить: {saved:.2f} руб.")
