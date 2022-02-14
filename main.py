from logging import exception
import pprint
from xml.dom.minicompat import defproperty
import ccxt
from numpy import float64
import pandas as pd

import datetime
import time

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_board_rate(exchange, symbol, time_str):
    
    orderbook = exchange.fetch_order_book(symbol)
    tiker = exchange.fetch_ticker(symbol)

    #bid=sell ask=buy
    df_ask = pd.DataFrame(orderbook['asks'], columns=['ask_price', 'ask_size'])
    df_bid = pd.DataFrame(orderbook['bids'], columns=['bid_price', 'bid_size'])
    df_board = pd.concat([df_ask.head(10), df_bid.head(10)], axis=1)
    board_sum = df_board[['ask_size','bid_size']].sum()
    board_rate = (board_sum/board_sum.sum()).T
    board_rate = board_rate.rename(index={'ask_size':'{}_ask'.format(exchange),
                                            'bid_size':'{}_bid'.format(exchange)})
    board_rate['{}_tiker'.format(exchange)] = tiker['last']
    
    return board_rate

def main():
    exchange_list = ['bybit', 'binance', 'coinbasepro', 'ftx']
    symbol = 'BTC/USDT'

    df_rates = pd.DataFrame()

    while True:
        time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        board_rates =pd.Series(dtype=float64)

        for exchange in exchange_list:
            exchange = eval('ccxt.' + exchange + '()')
            board_rates = pd.concat([board_rates, get_board_rate(exchange, symbol, time_str)])

        board_rates = pd.DataFrame([board_rates.T], index=[time_str])
        df_rates = pd.concat([df_rates, board_rates])

        time.sleep(5)

        if len(df_rates) > 3:
            if os.path.isfile('./log/{}_board_rate.csv'.format(date_str)):
                df_rates.to_csv('./log/{}_board_rate.csv'.format(date_str), mode='a', header=False)
            else:
                df_rates.to_csv('./log/{}_board_rate.csv'.format(date_str), mode='a', header=True)
            
            df_rates = pd.DataFrame()
            

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
