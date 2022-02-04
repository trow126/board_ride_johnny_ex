import pprint
import ccxt
import pandas as pd

import datetime
import time

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_board_rate(exchange, time_str):
    symbol = 'BTC/USDT'
    exchange = eval('ccxt.' + exchange + '()')
    orderbook = exchange.fetch_order_book(symbol)

    tiker = exchange.fetch_ticker(symbol)

    #bid=sell   ask=buy
    df_buy = pd.DataFrame(orderbook['asks'], columns=['price', 'size'])
    df_sell = pd.DataFrame(orderbook['bids'], columns=['price', 'size'])
    df_buy = df_buy.head(10)
    df_sell = df_sell.head(10)
    
    board_rate = pd.DataFrame({df_buy['size'].sum(), df_sell['size'].sum()},
                                index=['buy', 'sell'])
    board_rate = board_rate/board_rate.sum()
    board_rate = board_rate.T

    board_rate['exchange'] = exchange
    board_rate['tiker'] = tiker['last']
    board_rate['time'] = time_str

    return board_rate

def main():

    exchange_list = ['bybit', 'binance', 'coinbasepro', 'ftx']

    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tmp = pd.DataFrame(columns=['buy', 'sell', 'exchange', 'tiker', 'time'])
    tmp.to_csv('./board_rate.csv', mode='a',index=False)

    while True:
        for exchange in exchange_list:
            tmp = pd.concat([tmp, get_board_rate(exchange, time_str)])

        time.sleep(5)

        if len(tmp) > 8:
            tmp.to_csv('./board_rate.csv', mode='a',index=False, header=False)
            tmp = pd.DataFrame()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
