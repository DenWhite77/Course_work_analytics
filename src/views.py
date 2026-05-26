import sys
import os
import requests
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

# Добавляем корень проекта в путь поиска модулей
sys.path.append(str(Path(__file__).parent.parent))

import json
from src.utils import read_excel_operations, filter_by_date_range, get_greeting


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


def main_page(date_time_str: str) -> str:
    """Главная страница. Возвращает JSON-строку с данными для веб-страницы."""
    # 1. Чтение данных
    transactions = read_excel_operations('data/operations.xlsx')

    # 2. Фильтрация по дате (с начала месяца по указанную)
    filtered = filter_by_date_range(transactions, date_time_str)

    # 3. Расчёт по картам
    cards_data = defaultdict(lambda: {"total_spent": 0.0, "cashback": 0.0})
    for transaction in filtered:
        card = transaction.get('Номер карты', '')
        if not card or len(str(card)) < 4:
            continue
        last_digits = str(card)[-4:]
        amount = transaction.get('Сумма платежа', 0)
        if amount > 0:
            cards_data[last_digits]["total_spent"] += amount
            cards_data[last_digits]["cashback"] += amount / 100

    cards_list = [
        {
            "last_digits": card,
            "total_spent": round(data["total_spent"], 2),
            "cashback": round(data["cashback"], 2)
        }
        for card, data in cards_data.items()
    ]

    # 4. Топ-5 транзакций по абсолютной сумме платежа
    sorted_transactions = sorted(filtered, key=lambda x: abs(x.get('Сумма платежа', 0)), reverse=True)
    top_5 = []
    for t in sorted_transactions[:5]:
        date_str = t.get('Дата операции', '')
        try:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            formatted_date = date_obj.strftime('%d.%m.%Y')
        except Exception:
            formatted_date = date_str[:10]

        top_5.append({
            "date": formatted_date,
            "amount": t.get('Сумма платежа', 0),
            "category": t.get('Категория', ''),
            "description": t.get('Описание', '')
        })

    # 5. Загрузка пользовательских настроек
    settings_path = Path(__file__).parent.parent / 'user_settings.json'
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    currency_rates = get_currency_rates(settings.get('user_currencies', []))
    stock_prices = get_stock_prices(settings.get('user_stocks', []))

    # 6. Формирование итогового JSON-ответа
    result = {
        "greeting": get_greeting(),
        "cards": cards_list,
        "top_transactions": top_5,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


def events_page(date_time_str: str, period: str = 'M') -> str:
    """
    Страница «События».
    period: 'W' (неделя), 'M' (месяц), 'Y' (год), 'ALL' (все данные до указанной даты)
    """
    transactions = read_excel_operations('data/operations.xlsx')
    filtered = filter_by_date_range(transactions, date_time_str, period)

    # Расходы (сумма < 0)
    expenses = [t for t in filtered if t.get('Сумма платежа', 0) < 0]
    total_expenses = abs(sum(t.get('Сумма платежа', 0) for t in expenses))

    # Поступления (сумма > 0)
    incomes = [t for t in filtered if t.get('Сумма платежа', 0) > 0]
    total_income = sum(t.get('Сумма платежа', 0) for t in incomes)

    # Группировка расходов по категориям
    from collections import defaultdict
    expenses_by_category = defaultdict(float)
    for t in expenses:
        cat = t.get('Категория', 'Другое')
        expenses_by_category[cat] += abs(t.get('Сумма платежа', 0))

    # Сортируем по убыванию, берём топ-7
    sorted_expenses = sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)
    top_expenses = [{"category": cat, "amount": round(amt)} for cat, amt in sorted_expenses[:7]]

    # Переводы и наличные (отдельно)
    transfers_and_cash = []
    for cat, amt in sorted_expenses:
        if cat in ['Переводы', 'Наличные']:
            transfers_and_cash.append({"category": cat, "amount": round(amt)})

    # Поступления по категориям
    incomes_by_category = defaultdict(float)
    for t in incomes:
        cat = t.get('Категория', 'Другое')
        incomes_by_category[cat] += t.get('Сумма платежа', 0)

    sorted_incomes = sorted(incomes_by_category.items(), key=lambda x: x[1], reverse=True)
    top_incomes = [{"category": cat, "amount": round(amt)} for cat, amt in sorted_incomes]

    # Загрузка курсов валют и акций (как в main_page)
    settings_path = Path(__file__).parent.parent / 'user_settings.json'
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    currency_rates = get_currency_rates(settings.get('user_currencies', []))
    stock_prices = get_stock_prices(settings.get('user_stocks', []))

    result = {
        "expenses": {
            "total_amount": round(total_expenses),
            "main": top_expenses,
            "transfers_and_cash": transfers_and_cash
        },
        "income": {
            "total_amount": round(total_income),
            "main": top_incomes
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # print(main_page("2021-12-31 23:59:59"))
    print(events_page("2021-12-31 23:59:59", period='M'))

