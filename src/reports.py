import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.utils import read_excel_operations


def spending_by_category(transactions: List[Dict[str, Any]], category: str, date: Optional[str] = None) -> float:
    """
    Возвращает сумму трат по заданной категории за последние 3 месяца от указанной даты.

    Args:
        transactions: Список транзакций.
        category: Категория для фильтрации.
        date: Дата в формате 'YYYY-MM-DD'. Если не указана — берётся текущая.

    Returns:
        Сумма трат (расходов) по категории.
    """
    if date is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(date, '%Y-%m-%d')

    # Начало периода: 3 месяца назад от target_date
    start_date = target_date - timedelta(days=90)

    total = 0.0
    for t in transactions:
        t_date_str = t.get('Дата операции', '')[:10]
        if not t_date_str:
            continue
        try:
            t_date = datetime.strptime(t_date_str, '%d.%m.%Y')
        except ValueError:
            continue

        if start_date <= t_date <= target_date:
            if t.get('Категория', '') == category:
                amount = t.get('Сумма платежа', 0)
                if amount < 0:  # только расходы
                    total += abs(amount)

    return round(total, 2)


if __name__ == "__main__":
    # Пример вызова
    data = read_excel_operations('data/operations.xlsx')
    print(spending_by_category(data, "Супермаркеты", "2021-12-31"))
