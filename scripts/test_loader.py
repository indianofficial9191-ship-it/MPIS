from pathlib import Path
from mpis.data.csv_loader import CSVLoader

loader = CSVLoader()

buffer = loader.load(
    Path("data/raw/NIFTY/NIFTY_50_1minute_2015_26.csv"),
    symbol="NIFTY",
    timeframe="1m",
)

print("Rows:", len(buffer))
print("First candle:", buffer[0])
print("Last candle:", buffer[-1])