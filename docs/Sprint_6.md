# Sprint 6 — Institutional Order-Flow Proxy Engine

## Objective

Add an OHLCV-based institutional order-flow proxy that can later accept
real tick, bid/ask, footprint, or order-book data.

## What this sprint adds

- Candle-derived buy/sell pressure
- Volume-normalized delta proxy
- Absorption proxy
- Imbalance score
- Institutional activity score
- Dominant BUY / SELL / NEUTRAL classification
- Deterministic unit tests

## Classification threshold

The default dominant-side threshold is `0.25` on the normalized delta proxy. This keeps BUY/SELL classification useful for the OHLCV proxy while remaining stricter than simply checking the sign of delta.

## Important limitation

OHLCV alone cannot identify the true aggressor side or prove institutional
activity. The `institutional_score` is therefore a research proxy, not a
claim that institutions caused a move.

## Integration point

New package:

`src/mpis/institutional/orderflow/`

Import:

```python
from mpis.institutional.orderflow import OrderFlowAnalyzer
```

Expected input columns:

`open, high, low, close, volume`

Optional:

`timestamp`

## Validation

Run the full existing suite:

```powershell
python -m pytest -q
```

Then run only Sprint 6:

```powershell
python -m pytest -q tests/test_orderflow_sprint6.py
```
