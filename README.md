# binance_force_stop_loss
**!DYOR! Use at own lisk. This software is a bit buggy, so NO RESPONSIBLE for your trading results using this bot.**

**このソフトウェアを使う責任はあなた自身にあります。このソフトウェアによるあなたの資金の損失について、作者は一切関知しません。**
***

BinanceFのポジションを決められた位置で無理やり損切りさせるだけのbot　自分用

# Preparation
## Required package
- python 3.5.3+
- ccxt 1.49.x+
- binanceのAPIキー(自分で取得したものを利用)
## 1.
```
  $ pip install ccxt
```
## 2.
  binanceのApi keyとApi Secretをsrc/apidataに書き込む
## 3.
```
  $ ./main.py
```
  
## Change the stop Loss price
  ロングなら53行目、ショートなら65行目を変更
  ```
    				SLPrice = float(pst.get('entryPrice'))*0.99 #ロング版の初期値　floatでないとエラーが出る
            SLPrice = float(pst.get('entryPrice'))*1.01 #ショート版の初期値
  ```
# known issues
  - Perp USDTペア以外(BTCBUSDとか限月つき先物系)はSLをつけられずにエラーが発生する(symbolの書き換えが適当なせい)
  - まれにcode: -2021 (Order would immediately trigger.)エラーが起きる
