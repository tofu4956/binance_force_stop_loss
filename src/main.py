import time
import datetime
import threading
import apidata
from pprint import pprint
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
print(f'CCXT Version:{ccxt.__version__} Current Time:{datetime.datetime.now()}, Binance Server Time:{e_time}') 

#exchange.set_sandbox_mode(True)
#exchange.fapiPrivatePostPositionSideDual ({'dualSidePosition':'true'})
b_time = time.time()

def set_stop_loss():
	SLPrice = 0.0
	markets = exchange.load_markets()
	#exchange.verbose = True
	balance = exchange.fetch_balance()
	positions = balance['info']['positions']
	for idx, pst in enumerate(positions):
		ticker = pst.get('symbol')
		symbol = ticker.strip("USDT")  + "/USDT"
		posamount = float(pst.get('positionAmt'))
		if posamount > 0:
			if pst.get('positionSide') == 'LONG':
				SLPrice = float(pst.get('entryPrice'))*0.99
				print(ticker)
				exchange.create_order(symbol=symbol, type="STOP_MARKET", side="sell",amount=posamount,  params={"closePosition": True, "stopPrice": SLPrice, "positionSide": "LONG"})
			elif pst.get('positionSide') == 'SHORT': 
				SLPrice = (pst.get('entryPrice'))*1.01
				exchange.create_order(symbol=symbol, type="STOP_MARKET", side="buy",amount=posamount,  params={"closePosition": True, "stopPrice": SLPrice, "positionSide": "SHORT"})
			print(ticker)
			print("ordered sucessfully!")
			print("\n")
			
def autorefill(f):
	n_time = 0;
	while True:
		t = threading.Thread(target=f)
		t.start()
		n_time = ((b_time-time.time()) % 60) or 60
		print(n_time)
		time.sleep(n_time)

autorefill(set_stop_loss)



