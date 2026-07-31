"""CSV loader for MPIS market data."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from mpis.core.exceptions import DataError
from mpis.core.timer import Timer
from mpis.data.buffer import ReplayBuffer
from mpis.data.models import CSVLoadResult, DataHealthStatus
from mpis.data.validator import DataHealth, DataValidator
from mpis.data.candle import Candle
from mpis.utils.logger import get_logger


class CSVLoader:
    """Load historical market data from CSV files."""

    def __init__(self) -> None:
        self.logger = get_logger("mpis.data.csv_loader")
        self.health = DataHealth()
        self.validator = DataValidator(self.health)
        self.last_load_result: CSVLoadResult | None = None

    def load(self, path: Path | str, symbol: str, timeframe: str) -> ReplayBuffer:
        """Load a CSV file into a replay buffer."""
        path_obj = Path(path)
        if not path_obj.exists():
            self.health.report(DataHealthStatus.ERROR, "csv path does not exist")
            raise DataError(f"CSV path does not exist: {path_obj}")

        try:
            with Timer("csv_loading") as _:
                dataframe = self._read_csv(path_obj)

            self.logger.info("CSV loaded", extra={"path": str(path_obj), "rows_loaded": len(dataframe)})

            with Timer("validation") as _:
                self.validator.validate_dataframe(dataframe)

            if self.health.status == DataHealthStatus.UNKNOWN:
                self.health.report(DataHealthStatus.OK, "csv loaded and validated")

            if "volume" not in dataframe.columns or "oi" not in dataframe.columns:
                self.health.report(DataHealthStatus.WARNING, "optional fields volume or oi missing")

            with Timer("buffer_creation") as _:
                candles = self._build_candles(dataframe, symbol, timeframe)
                buffer = ReplayBuffer(candles)

            self.last_load_result = CSVLoadResult(
                rows_loaded=len(dataframe),
                duplicate_count=0,
                duration_seconds=0.0,
                buffer_size=len(buffer),
                status=self.health.status,
                warnings=tuple(self.health.details.values()),
            )
            self.logger.info("Replay buffer created", extra={"buffer_size": len(buffer)})
            return buffer
        except DataError:
            self.health.report(DataHealthStatus.ERROR, "csv loading failed")
            raise
        except Exception as exc:
            self.health.report(DataHealthStatus.ERROR, "unexpected csv loader failure")
            raise DataError(str(exc)) from exc

    def _read_csv(self, path: Path) -> pd.DataFrame:
        dataframe = pd.read_csv(path)
        if "date" not in dataframe.columns or "time" not in dataframe.columns:
            raise DataError("CSV must contain 'date' and 'time' columns")

        required_columns = ["open", "high", "low", "close"]
        missing_columns = [column for column in required_columns if column not in dataframe.columns]
        if missing_columns:
            raise DataError(f"Missing required columns: {', '.join(missing_columns)}")

        if dataframe[required_columns].isna().any().any():
            raise DataError("OHLC values must not be missing")

        dataframe = dataframe.copy()
        datetime_string = dataframe["date"].astype(str) + " " + dataframe["time"].astype(str)
        try:
            dataframe["timestamp"] = pd.to_datetime(
                datetime_string,
                format="%Y-%m-%d %H:%M:%S",
                errors="raise",
            )
        except ValueError:
            dataframe["timestamp"] = pd.to_datetime(
                datetime_string,
                format="%d-%m-%Y %H:%M:%S",
                errors="raise",
            )

        if "volume" not in dataframe.columns:
            dataframe["volume"] = 0.0
        if "oi" not in dataframe.columns:
            dataframe["oi"] = 0.0

        dataframe = dataframe.sort_values("timestamp", kind="mergesort")

        if dataframe["timestamp"].duplicated().any():
            duplicates = int(dataframe["timestamp"].duplicated().sum())
            raise DataError(f"Duplicate timestamps found: {duplicates}")

        return dataframe.reset_index(drop=True)

    def _build_candles(self, dataframe: pd.DataFrame, symbol: str, timeframe: str) -> list[Candle]:
        candles: list[Candle] = []
        for row in dataframe.itertuples(index=False):
            candles.append(
                Candle(
                    timestamp=row.timestamp,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.close),
                    volume=self._optional_float(getattr(row, "volume", None)),
                    oi=self._optional_float(getattr(row, "oi", None)),
                    symbol=symbol,
                    timeframe=timeframe,
                )
            )
        return candles

    @staticmethod
    def _optional_float(value: object | None) -> float | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return float(value)
