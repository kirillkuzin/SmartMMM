import requests
from settings import VALUE_DECIMALS

def getEtherPrice():
    response = requests.get('https://api.cryptonator.com/api/ticker/eth-usd')
    response = response.json()
    if response['success']:
        price = float(response['ticker']['price'])
    else:
        price = 0
    return price

def correctDecimals(value):
    correctValue = '{:.{}f}'.format(value, VALUE_DECIMALS)
    return correctValue
