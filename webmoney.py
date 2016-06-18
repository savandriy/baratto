import requests
import datetime
import sqlite3
from bs4 import BeautifulSoup


def get_webmoney_course(from_currency, to_currency):
    """
    :param from_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :param to_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :return: tuple(result: float, website: string, name: string);
        result - currency exchange rate;
        website - link to the website where you can convert currencies;
        name - name of the website
    """
    current_datetime = datetime.datetime.now()
    exchtype = get_exchtype(convert_curr_to_webmoney(from_currency), convert_curr_to_webmoney(to_currency))

    query_params = {'exchtype': exchtype,
                    'grouptype': 4,
                    'yearstats': current_datetime.year,
                    'monthstats': current_datetime.month,
                    'daystats': current_datetime.day,
                    'hourstats': current_datetime.hour}

    # To know what currency is more worth
    currency_priority = {
        'RUR': 1,
        'UAH': 2,
        'USD': 3,
        'EUR': 4
    }

    try:
        course = requests.get("https://wm.exchanger.ru/asp/XMLQuerysStats.asp", params=query_params)
        course.raise_for_status()
        soup = BeautifulSoup(course.text)

        res_course = float(soup.row.attrs['avgrate'])

        if currency_priority[from_currency] < currency_priority[to_currency]:
            return 1.0 / res_course, 'https://wm.exchanger.ru', 'Webmoney(Exchanger)'
        else:
            return res_course, 'https://wm.exchanger.ru', 'Webmoney(Exchanger)'

    except AttributeError:
        hour = current_datetime.hour - 1
        if current_datetime.hour == 0: hour = 23
        query_params['hourstats'] = hour
        course = requests.get("https://wm.exchanger.ru/asp/XMLQuerysStats.asp", params=query_params)
        course.raise_for_status()
        soup = BeautifulSoup(course.text)

        res_course = float(soup.row.attrs['avgrate'])

        if currency_priority[from_currency] < currency_priority[to_currency]:
            return 1.0 / res_course, 'https://wm.exchanger.ru', 'Webmoney(Exchanger)'
        else:
            return res_course, 'https://wm.exchanger.ru', 'Webmoney(Exchanger)'


def put_exchtype_in_database():
    """
    Create table in DB to link exchtype(special webmoney ID for exchange directions) to currency exchange directions
    """
    request = requests.get("https://wm.exchanger.ru/asp/XMLbestRates.asp")
    request.raise_for_status()
    soup = BeautifulSoup(request.text)
    rows = soup.find_all('row')

    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Webmoney
        (id INTEGER PRIMARY KEY NOT NULL , from_direction TEXT NOT NULL , to_direction TEXT NOT NULL )''')

    for row in rows:
        from_direct = row['direct'].split('-')[0].strip()
        to_direct = row['direct'].split('-')[1].strip()
        cur.execute('INSERT OR REPLACE INTO Webmoney (id, from_direction, to_direction) VALUES ( ?, ?, ? )', (row['exchtype'], from_direct, to_direct))
        conn.commit()


def get_exchtype(from_direction, to_direction):
    """
    :param from_direction: string
    :param to_direction: string
    :return
    """
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT id FROM Webmoney WHERE from_direction = ? AND to_direction = ?', (from_direction, to_direction))
    row = cur.fetchone()

    return row[0]


def convert_curr_to_webmoney(origin_curr):
    """
    Convert currency names to Webmoney currency names(ex. 'USD' -> 'WMZ')
    :param origin_curr: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :return: string
    """
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT wm_curr FROM CurrToWebm WHERE origin_curr = ?', (origin_curr, ))
    row = cur.fetchone()

    return row[0]

