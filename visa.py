from datetime import date, datetime
from visaxrated import xrate


def get_visa_course(from_currency, to_currency):
    """
    :param from_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :param to_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :return: tuple(result: float, website: string, name: string);
        result - currency exchange rate;
        website - link to the website where you can convert currencies;
        name - name of the website
    """
    if from_currency == 'RUR':
        from_currency = 'RUB'
    if to_currency == 'RUR':
        to_currency = 'RUB'

    current_datetime = datetime.now()

    today_date = date(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day)
    # card, trans, fee, date, amount
    result = xrate(to_currency, from_currency, 0, today_date, 1)

    return result, 'https://privat24.ua/', 'Privat24(Visa)'


