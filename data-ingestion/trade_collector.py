import pandas as pd
from cryptofeed import FeedHandler
from cryptofeed.defines import TRADES
from cryptofeed.exchanges import Binance
import asyncio
import numpy as np
import datetime
import os
import time
import gc

"""

BTC L2  Trade Ingestion Pipeline

Event driven by nature, 
hence we use the TRADES channel to capture real-time trade data.

"""

fh = FeedHandler()

BUFFER_SIZE = 5000
TARGET_INTERVALS_MS = 10
buffer = []
batch_count = 1


async def handle_trade(trade, timestamp):
    global buffer, batch_count, BUFFER_SIZE

    start = time.perf_counter()

    symbol = trade.symbol

    buffer.append({
        'timestamp': timestamp,
        'side': trade.side,
        'price': trade.price,
        'amount': trade.amount
    })
    """
    
    Check if the buffer has reached the defined BUFFER_SIZE. If it has, write the contents of the buffer to a Parquet file. 
    The filename includes the batch count, symbol, and a timestamp for easy identification.
    After writing to the file, the buffer is cleared and garbage collection is triggered to free up memory.
    
    Await asichronous file writing to avoid blocking the event loop, ensuring that data collection continues smoothly while the file is being written.
  
    """
    
    if len(buffer) >= BUFFER_SIZE:
        os.makedirs("data-trades", exist_ok=True)
        df = pd.DataFrame(buffer)
        t = datetime.datetime.now()
        filename = f"data-trades/{batch_count}_{symbol}_{t.strftime('%d-%m-%y_%H-%M-%S')}.parquet"
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
        channels=[TRADES],
        callbacks={TRADES: handle_trade}
    )
)


fh.run()