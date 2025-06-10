import pandas as pd

df = pd.read_parquet('/home/j39233pt/Desktop/Nebula_Apex_MM/data-ingestion/data/1_BTC-USDT_28-05-25_12-48-30.parquet', engine='pyarrow')

print(df.head())