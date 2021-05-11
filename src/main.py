import time
import datetime
import threading
import apidata
import ccxt 

#initialize
exchange = ccxt.binance({
    'apiKey': apidata.my_api_key,
    'secret': apidata.my_secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
})
e_time = float(exchange.public_get_time()['serverTime'])
print(f'CCXT Version:{ccxt.__version__} Current Time:{datetime.datetime.now()}, Binance Server Time:{e_time} (UNIX TIME)') 
print("""
-----------------------------------------------
          binance_force_stop_loss_bot
-----------------------------------------------
""")
print('\n')

#exchange.set_sandbox_mode(True)
#exchange.fapiPrivatePostPositionSideDual ({'dualSidePosition':'true'})
b_time = time.time()
n_time = 0

def autorefill(f):
    while True:
        t = threading.Thread(target=f)
        t.start()
        n_time = ((b_time-time.time()) % 60) or 60
        time.sleep(n_time)

def set_stop_loss():
    SLPrice = 0.0
    markets = exchange.load_markets()
    bot_status = 0
    #exchange.verbose = True
    positions = exchange.fetch_positions()
    for idx, pst in enumerate(positions):
        ticker = pst.get('symbol')
        symbol = ticker.replace('USDT', '')  + "/USDT"
        posamount = float(pst.get('positionAmt'))
        if posamount != 0:
            positionside = pst.get('positionSide')
            print(f'Order found: {ticker} {positionside}')
            buf_price = exchange.fetch_ticker(symbol=symbol)
            lprice = buf_price.get('info').get('lastPrice')
            if positionside == 'LONG':
                SLPrice = float(pst.get('entryPrice'))*0.99
                print(buf_price)
                buf_order = exchange.fetch_orders(symbol=symbol)
                cur_order = [idy for idy, corder in enumerate(buf_order) if (corder.get('info').get('type') == 'STOP_MARKET' and corder.get('info').get('status') == 'NEW' and corder.get('info').get('positionSide') == 'LONG')]
                if ((SLPrice - float(lprice) > 0) and (len(cur_order) == 0)):
                    exchange.create_order(symbol=symbol, type="MARKET", side="sell", amount=posamount, params={"positionSide": "LONG"})
                    bot_status = 3
                elif(len(cur_order) == 0):
                    exchange.create_order(symbol=symbol, type="STOP_MARKET", side="sell",amount=posamount,  params={"closePosition": True, "stopPrice": SLPrice, "positionSide": "LONG", "priceProtect": "TRUE"})
                    bot_status = 2
                else: bot_status = 1
            elif positionside == 'SHORT': 
                SLPrice = float(pst.get('entryPrice'))*1.01
                buf_order = exchange.fetch_orders(symbol=symbol)
                cur_order = [idy for idy, corder in enumerate(buf_order) if (corder.get('info').get('type') == 'STOP_MARKET' and corder.get('info').get('status') == 'NEW' and corder.get('info').get('positionSide') == 'SHORT')]
                if((float(lprice) - SLPrice > 0) and (len(cur_order) == 0)):
                    exchange.create_order(symbol=symbol, type="MARKET", side="buy", amount=abs(posamount), params={"positionSide": "SHORT"})
                    bot_status = 3
                elif(len(cur_order) == 0):
                    exchange.create_order(symbol=symbol, type="STOP_MARKET", side="buy",amount=abs(posamount),  params={"closePosition": True, "stopPrice": SLPrice, "positionSide": "SHORT", "priceProtect": "TRUE"})
bot_status = 2
                else: bot_status = 1
            if bot_status == 3:
                print(f'{symbol} {positionside} is closed by this bot due to exceed the stop loss Price instead of poor trader like you. DO NOT CHANGE OR REMOVE THE STOP LOSS!!!!!!!!!!!!!!!')
            elif bot_status == 2:
                print(f'{symbol} {positionside} Stop Loss ordered sucessfully! Trigger price: {SLPrice}')
            elif bot_status == 1:
                print(f'{symbol} {positionside} is already placed Stop loss. Order was Skipped.')
    if bot_status == 0:print("Position Not Found.")
    print(f'Next estimated check time:{datetime.datetime.fromtimestamp(time.time() + n_time)}')
		
autorefill(set_stop_loss)

