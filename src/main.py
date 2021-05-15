import time
import datetime
import threading
import apidata
import ccxt

# initialize
exchange = ccxt.binance({
    'apiKey': apidata.my_api_key,
    'secret': apidata.my_secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
})
e_time = float(exchange.public_get_time()['serverTime'])
print(
    f'CCXT Version:{ccxt.__version__} '
    f'Current Time:{datetime.datetime.now()} '
    f'Binance Server Time:{e_time} (UNIX TIME)')
print("""
-----------------------------------------------
          binance_force_stop_loss_bot
-----------------------------------------------
""")
print('\n')

# exchange.set_sandbox_mode(True)
# exchange.fapiPrivatePostPositionSideDual ({'dualSidePosition':'true'})


b_time = time.time()
n_time = 60
N_TIME = n_time
BOT_INITIAL = 0
BOT_ORDERSKIPPED = 1
BOT_ORDERCREATED = 2
BOT_POSITIONCLOSED = 3
BOT_ERROR = 99


def autorefill(f):
    while True:
        t = threading.Thread(target=f)
        t.start()
        n_time = ((b_time-time.time()) % N_TIME) or N_TIME
        time.sleep(n_time)


def set_stop_loss():
    SLPrice = 0.0
    bot_status = BOT_INITIAL
    # exchange.verbose = True
    positions = exchange.fetch_positions()
    for idx, pst in enumerate(positions):
        ticker = pst.get('symbol')
        symbol = ticker.replace('USDT', '') + "/USDT"
        posamount = float(pst.get('positionAmt'))
        if posamount != 0:
            positionside = pst.get('positionSide')
            print(f'Order found: {ticker} {positionside}')
            buf_price = exchange.fetch_ticker(symbol=symbol)
            buf_order = exchange.fetch_orders(symbol=symbol)
            lprice = buf_price.get('info').get('lastPrice')
            if positionside == 'LONG':
                SLPrice = float(pst.get('entryPrice'))*0.99
                cur_order = [
                    idy for idy, corder in enumerate(buf_order)
                    if (corder.get('info').get('type') == 'STOP_MARKET'
                        and corder.get('info').get('status') == 'NEW'
                        and corder.get('info').get('positionSide') == 'LONG')
                            ]
                if (SLPrice - float(lprice) > 0):
                    try:
                        exchange.create_order(
                            symbol=symbol,
                            type="MARKET",
                            side="sell",
                            amount=posamount,
                            params={"positionSide": "LONG"}
                        )
                        bot_status = BOT_POSITIONCLOSED
                    except ccxt.ExchangeError as e:
                        print(e)
                        print("Order failed. It seems someone close position.")
                        bot_status = BOT_ERROR
                elif(len(cur_order) == 0):
                    try:
                        exchange.create_order(
                            symbol=symbol,
                            type="STOP_MARKET",
                            side="sell",
                            amount=posamount,
                            params={
                                "closePosition": True,
                                "stopPrice": SLPrice,
                                "positionSide": "LONG",
                                "priceProtect": "TRUE"
                            }
                        )
                        bot_status = BOT_ORDERCREATED
                    except ccxt.ExchangeError as e:
                        print(e)
                        print("Order failed. Did you change the stop loss ??????????????????????????????")
                        bot_status = BOT_ERROR
                else:
                    bot_status = BOT_ORDERSKIPPED
            elif positionside == 'SHORT':
                SLPrice = float(pst.get('entryPrice'))*1.01
                cur_order = [
                    idy for idy, corder in enumerate(buf_order)
                    if (corder.get('info').get('type') == 'STOP_MARKET'
                        and corder.get('info').get('status') == 'NEW'
                        and corder.get('info').get('positionSide') == 'SHORT')
                ]
                if(float(lprice) - SLPrice > 0):
                    try:
                        exchange.create_order(
                            symbol=symbol,
                            type="MARKET",
                            side="buy",
                            amount=abs(posamount),
                            params={"positionSide": "SHORT"}
                        )
                        bot_status = BOT_POSITIONCLOSED
                    except ccxt.ExchangeError as e:
                        print(e)
                        print("Order failed. It seems someone close position.")
                        bot_status = BOT_ERROR
                elif(len(cur_order) == 0):
                    try:
                        exchange.create_order(
                            symbol=symbol,
                            type="STOP_MARKET",
                            side="buy",
                            amount=abs(posamount),
                            params={"closePosition": True,
                                    "stopPrice": SLPrice,
                                    "positionSide": "SHORT",
                                    "priceProtect": "TRUE"}
                        )
                        bot_status = BOT_ORDERCREATED
                    except ccxt.ExchangeError as e:
                        print(e)
                        print("Order failed. Did you change the stop loss ??????????????????????????????")
                        bot_status = BOT_ERROR
                else:
                    bot_status = BOT_ORDERSKIPPED
            if bot_status == BOT_POSITIONCLOSED:
                print(f'{symbol} {positionside} is closed by this bot '
                      'due to exceed the stop loss price instead of poor trader like you.'
                      'DO NOT CHANGE OR REMOVE THE STOP LOSS!!!!!!!!!!!!!!!')
            elif bot_status == BOT_ORDERCREATED:
                print(f'{symbol} {positionside} Stop Loss ordered sucessfully! '
                      f'Trigger price: {SLPrice}')
            elif bot_status == BOT_ORDERSKIPPED:
                print(f'{symbol} {positionside} is already placed Stop loss. Order was Skipped.')
            elif bot_status == BOT_ERROR:
                print('Order was not executed properly. Check again next time.')

    if bot_status == BOT_INITIAL:
        print("Position Not Found.")
    print(
        'Next estimated check time: '
        f'{datetime.datetime.fromtimestamp(time.time() + n_time)}')


autorefill(set_stop_loss)
