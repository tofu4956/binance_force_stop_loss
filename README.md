# binance_force_stop_loss

dev edition

# yarukoto

 - ペアごとの設定
 - 処理の高速化
 - もうちょっとマシな処理(2回に分けるとか)

# known issues
  - Perp USDTペア以外(BTCBUSDとか限月つき先物系)はSLをつけられずにエラーが発生する(symbolの書き換えが適当なせい)
  - まれにcode: -2021 (Order would immediately trigger.)エラーが起きる
  - Docker経由だと時刻ズレのために動かない
