import requests


class CurrencyApi(object):

    def __init__(self):
        self.url = 'http://api.fixer.io/latest?symbols=CAD&base=USD'

    def get_usd_cad_exchange(self):
        response = requests.get(self.url)
        exchange_rate = response.json().get('rates').get('CAD')
        print('Found USD->CAD exchange rate of {0:0.2f}'.format(exchange_rate))
        return float(exchange_rate)
