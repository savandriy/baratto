import requests
import sqlite3


def create_privat_table():
    """
    Creates a blank table 'Privat' in DB;
    attributes of table:
        from_directon for from_currency,
        to_direction for to_currency,
        rate - exchange rate in direction
    """
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Privat
            (from_direction TEXT NOT NULL , to_direction TEXT NOT NULL , rate REAL NOT NULL , PRIMARY KEY (from_direction , to_direction))''')


def fill_privat_table():
    """
    Get currency exchange rates information from Privatbank API and write it to DB
    """
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    request = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    request.raise_for_status()
    result = request.json()[:-1]

    for course in result:
        cur.execute('INSERT OR REPLACE INTO Privat (from_direction, to_direction, rate) VALUES ( ?, ?, ? )', (course['ccy'], course['base_ccy'], float(course['buy'])))
        cur.execute('INSERT OR REPLACE INTO Privat (from_direction, to_direction, rate) VALUES ( ?, ?, ? )', (course['base_ccy'], course['ccy'], float(course['sale'])))
        conn.commit()


def get_privat_course(from_currency, to_currency):
    """
    :param from_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :param to_currency: string, should be one of 'USD', 'EUR', 'UAH', 'RUR'
    :return: tuple(result: float, website: string, name: string);
        result - currency exchange rate;
        website - link to the website where you can convert currencies;
        name - name of the website
    """
    # Update course info
    fill_privat_table()

    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    # Read the needed rate from DB
    cur.execute('SELECT rate FROM Privat WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
    row = cur.fetchone()

    # To know what currency is more worth
    currency_priority = {
        'RUR': 1,
        'UAH': 2,
        'USD': 3,
        'EUR': 4
    }

    # Special checks to work with the API style
    if from_currency == 'RUR' and to_currency == 'UAH':
        return row[0], 'https://privat24.ua/', 'Privat24'
    elif from_currency == 'UAH' and to_currency == 'RUR':
        return 1.0 / row[0], 'https://privat24.ua/', 'Privat24'

    if currency_priority[from_currency] < currency_priority[to_currency]:
        return 1.0 / row[0], 'https://privat24.ua/', 'Privat24'
    else:
        return row[0], 'https://privat24.ua/', 'Privat24'
