import requests
import datetime
from bs4 import BeautifulSoup


def get_mastercard_course(from_currency, to_currency):
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

    current_datetime = datetime.datetime.now()
    # '5/19/2016'
    parameters = {
        'service': 'getExchngRateDetails',
        'baseCurrency': from_currency,
        'settlementDate': str(current_datetime.month)+'/'+str(current_datetime.day - 1)+'/'+str(current_datetime.year)
    }

    request = requests.post("https://www.mastercard.com/psder/eu/callPsder.do", parameters)
    request.raise_for_status()

    soup = BeautifulSoup(request.text, 'xml')

    all_courses = soup.find_all('TRANSACTION_CURRENCY_DTL')

    result = 0.0

    for element in all_courses:
        if element.ALPHA_CURENCY_CODE.text == to_currency:
            result = float(element.CONVERSION_RATE.text)

    return result, 'https://privat24.ua/', 'Privat24(Mastercard)'

