import pandas as pd
from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK
from cryptofeed.exchanges import Binance
import asyncio
import numpy as np
import datetime
import os
import time
import gc
from itertools import islice

"""

BTC L2  Data Ingestion Pipeline
Written by Arryl Tham

"""

fh = FeedHandler()

BUFFER_SIZE = 5000
TARGET_INTERVALS_MS = 10
buffer = []
batch_count = 1
last_collected = 0


async def handle_book(order_book, timestamp):
    global buffer, batch_count, last_collected, TARGET_INTERVALS_MS, BUFFER_SIZE

    """
    
    Record time of function start for performance monitoring. 
    Sceduling When to collect data.
    
    """
    
    start = time.perf_counter()

    now = int(timestamp * 1000)

    if last_collected == 0:
        last_collected = now - (now % TARGET_INTERVALS_MS)

    """
    
    Check if the current timestamp is at least TARGET_INTERVALS_MS milliseconds after the last collected timestamp. 
    If not, skip processing to maintain the desired data collection frequency.
    
    """
    
    if now < last_collected + TARGET_INTERVALS_MS:
        print(f"Skipping: now={now}, next={last_collected + TARGET_INTERVALS_MS}")
        return

    last_collected += TARGET_INTERVALS_MS

    
    bids = order_book.book.bids
    asks = order_book.book.asks
    symbol = "BTC-USDT"

    if len(bids) < 10 or len(asks) < 10:
        return
    
    """
    
    Takes only the first 10 levels of the order book for both bids and asks, 
    and extracts the price and size information.
    
    isslice takes first 10 items without loading the full dictionary into memory, 
    which is more efficient for large order books.
    
    """
    
    top_10_bids = np.array([(price, bids[price]) for price in islice(bids, 10)])
    top_10_asks = np.array([(price, asks[price]) for price in islice(asks, 10)])

    top_10_bid_price = top_10_bids[:, 0]
    top_10_ask_price = top_10_asks[:, 0]

    top_10_bid_size = top_10_bids[:, 1]
    top_10_ask_size = top_10_asks[:, 1]

    bid_depth = np.sum(top_10_bid_size)
    ask_depth = np.sum(top_10_ask_size)

    mid_price = (top_10_ask_price[0] + top_10_bid_price[0]) / 2
    spread = top_10_ask_price[0] - top_10_bid_price[0]
    imbalance = bid_depth/(bid_depth + ask_depth)
    
    """
    
    Unpack the extracted data into structed format and append to buffer.
  
    """

    buffer.append({
        'timestamp': timestamp,
        **{f'bid_price_{i + 1}': top_10_bid_price[i] for i in range(10)},
        **{f'ask_price_{i + 1}': top_10_ask_price[i] for i in range(10)},
        **{f'bid_size_{i + 1}': top_10_bid_size[i] for i in range(10)},
        **{f'ask_size_{i + 1}': top_10_ask_size[i] for i in range(10)},
        'bid_depth': bid_depth,
        'ask_depth': ask_depth,
        'mid_price': mid_price,
        'spread': spread,
        'imbalance': imbalance
    })
    
    """
    
    Check if the buffer has reached the defined BUFFER_SIZE. If it has, write the contents of the buffer to a Parquet file. 
    The filename includes the batch count, symbol, and a timestamp for easy identification.
    After writing to the file, the buffer is cleared and garbage collection is triggered to free up memory.
      
    """

    if len(buffer) >= BUFFER_SIZE:
        os.makedirs("data", exist_ok=True)
        df = pd.DataFrame(buffer)
        t = datetime.datetime.now()
        filename = f"data/{batch_count}_{symbol}_{t.strftime('%d-%m-%y_%H-%M-%S')}.parquet"
        
        """
        
        Await asichronous file writing to avoid blocking the event loop, ensuring that data collection continues smoothly while the file is being written.
        
        """
        
        await asyncio.to_thread(df.to_parquet, filename, engine='pyarrow', index=False, compression='snappy')
        print(f"batch {batch_count} added to data at {t.strftime('%d-%m-%y_%H-%M-%S')}")        
        batch_count += 1
        print("Writing batch to Parquet")
        buffer.clear()
        gc.collect()
        print("Buffer cleared.")
    
    duration = time.perf_counter() - start
    if len(buffer) % 50 == 0:
        print(f"handle_book duration: {duration:.5f} seconds")    

fh.add_feed(
    Binance(
        symbols=["BTC-USDT"],
        channels=[L2_BOOK],
        callbacks={L2_BOOK: handle_book}
    )
)


fh.run()

