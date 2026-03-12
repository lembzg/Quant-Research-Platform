import pandas as pd
from order_side import OrderSide, LimitOrder
from order_book import OrderBook
import datetime
import uuid
import os

"""
Written by: Arryl Tham

Replay historical market data through order book simulator to reconstruct
what was happening in the market.

"""

df_trades = pd.read_parquet('/home/j39233pt/Desktop/Nebula_Apex_MM/data-ingestion/data-trades/2_BTC-USDT_30-05-25_23-40-13.parquet', engine='pyarrow')
df_prices = pd.read_parquet('/home/j39233pt/Desktop/Nebula_Apex_MM/data-ingestion/data/2_BTC-USDT_30-05-25_23-42-05.parquet', engine = 'pyarrow')

pd.set_option('display.max_columns', None)
#Depth INCREASE: at bid1/ask1 price, simulate limit order.
#Depth  DECREASE: If no trade, order cancelled. If have trade = order fill.
book = OrderBook()
trade_log = []

# Holds the previous snapshot so we can compare 
prev_row = None
MAX_SIZE = 1000
batch_count = 0

"""

Writes trade to file if trade_log reaches MAX_SIZE. 
Used to avoid memory overflow during long simulations.

"""

def trade_log_check():
    if len(trade_log) >= MAX_SIZE:
        os.makedirs("lob_trades", exist_ok=True)
        df = pd.DataFrame(trade_log)
        t = datetime.datetime.now()
        filename = f'{batch_count}.parquet'
        df.to_parquet(filename, engine='pyarrow', index=False, compression='snappy')
        print(f"batch {batch_count} added to data at {t.strftime('%d-%m-%y_%H-%M-%S')}")        
        batch_count += 1
        trade_log.clear()
        print('Trade log cleared.')


"""

Loop through price snapshots and simulate order book dynamics.

"""
for row in df_prices.itertuples(index=False):
    if prev_row is not None:

        for i in range(1, 11):
            trade_log_check()
            bid_attr = f'bid_size_{i}'
            ask_attr = f'ask_size_{i}'
            bid_price_attr = f'bid_price_{i}'
            ask_price_attr = f'ask_price_{i}'

            bid_size_now = getattr(row, bid_attr)
            bid_size_prev = getattr(prev_row, bid_attr)
            bid_price_now = getattr(row, bid_price_attr)
            bid_price_prev = getattr(prev_row, bid_price_attr)
            
            """
            If bid changes and price is the same, either new limit order or order fill/cancellation.
            """
            
            if bid_size_now != bid_size_prev and bid_price_now == bid_price_prev:
                
                # Add limit order if depth increases.
                if bid_size_now > bid_size_prev:
                    book.add_limit_order(LimitOrder(order_id=str(uuid.uuid4()),
                                                         timestamp=row.timestamp,
                                                         quantity=(bid_size_now-bid_size_prev),
                                                         price=bid_price_now,
                                                         side='buy',
                                                         is_self=False))
                
                # Simulate trade if depth decreases and there is a matching trade in the trade data. Otherwise, treat as order cancellation.
                if bid_size_now < bid_size_prev:
                    
                    """
                    
                    Look for matching trade in trade data. 
                    We check for trades that occurred between the previous and current timestamp, 
                    and at the same price level.
                    
                    
                    """
                    
                    matching_trade = df_trades[(df_trades['timestamp'] > prev_row.timestamp) & (df_trades['timestamp'] <= row.timestamp) & (df_trades['price'] == bid_price_now)]
                    if not matching_trade.empty:

                        trade = book.add_limit_order(LimitOrder(order_id=str(uuid.uuid4()),
                                                         timestamp=row.timestamp,
                                                         quantity=(bid_size_now-bid_size_prev),
                                                         price=bid_price_now,
                                                         side='sell',
                                                         is_self=False))

                    else:
                        print(f'Trade cancelled @ bid_quant {bid_size_prev-bid_size_now}')

            
            """
            
            Same logic applied for ask.
            
            """
            
            
            ask_size_now = getattr(row, ask_attr)
            ask_size_prev = getattr(prev_row, ask_attr)
            ask_price_now = getattr(row, ask_price_attr)
            ask_price_prev = getattr(prev_row, ask_price_attr)
            
            if ask_size_now != ask_size_prev and ask_price_now == ask_price_prev:

                if ask_size_now > ask_size_prev:
                    book.add_limit_order(LimitOrder(order_id=str(uuid.uuid4()),
                                                         timestamp=row.timestamp,
                                                         quantity=(ask_size_now-ask_size_prev),
                                                         price=ask_price_now,
                                                         side='sell',
                                                         is_self=False))
                
                if ask_size_now < ask_size_prev:
                    matching_trade = df_trades[(df_trades['timestamp'] > prev_row.timestamp) & (df_trades['timestamp'] <= row.timestamp) & (df_trades['price'] == ask_price_now)]
                    if not matching_trade.empty:                        
                        trade = book.add_limit_order(LimitOrder(order_id=str(uuid.uuid4()),
                                                         timestamp=row.timestamp,
                                                         quantity=(bid_size_now-bid_size_prev),
                                                         price=bid_price_now,
                                                         side='buy',
                                                         is_self=False))                       
                    else:
                        print(f'Trade cancelled @ ask_quant {ask_size_now-ask_size_prev}')
                    
                   
                

    prev_row = row


print(df_prices.head())
print(df_trades.head())




