import requests
from webmoney import convert_curr_to_webmoney


def get_chexch_course(from_currency, to_currency):
    """
    :param from_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :param to_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :return: tuple(result: float, website: string, name: string);
        result - currency exchange rate;
        website - link to the website where you can convert currencies;
        name - name of the website
    """
    API_KEY = "Your chexch API key here"

    parameters = {
        'type': 'rates',
        'from': convert_curr_to_webmoney(from_currency),
        'to': convert_curr_to_webmoney(to_currency),
        'key': API_KEY,
        'format': 'json',
        'lang': 'en'
    }

    query = requests.post("https://chexch.com/api", parameters)
    # If we get a bad status(like 404 or so) we raise an exception
    query.raise_for_status()
    # convert the result we got in JSON into a list of dictionaries
    query_res = query.json()
    # The list is already sorted(from max to min), so we get the first dict(the max rate)
    result = query_res[0]
    # All info in this dict is Unicode, so we convert rate to float
    result['course'] = float(result['course'])

    return result['course'], result['hostname'], result['name']


