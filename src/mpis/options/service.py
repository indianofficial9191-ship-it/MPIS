"""Service layer for open interest intelligence in MPIS."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from mpis.options.models import ParticipantOIRecord
from mpis.options.oi_analyzer import OIAnalyzer
from mpis.utils.logger import get_logger


class OptionOIService:
    """Service facade for option open interest intelligence."""

    REQUIRED_COLUMNS = {
        "participant_name",
        "participant_type",
        "long_oi",
        "short_oi",
        "long_change",
        "short_change",
        "volume",
        "net_oi",
    }

    def __init__(self) -> None:
        self.logger = get_logger("mpis.options.service")
        self.analyzer = OIAnalyzer()

    def analyze(self, records: Iterable[ParticipantOIRecord]) -> object:
        """Analyze participant open interest records."""
        records_list = list(records)
        self.logger.info("Analyzing participant OI records", extra={"count": len(records_list)})
        return self.analyzer.analyze(records_list)

    def from_dataframe(self, dataframe: pd.DataFrame) -> object:
        """Convert a DataFrame of open interest data to records and analyze."""
        self.logger.info("Parsing DataFrame into participant OI records", extra={"columns": list(dataframe.columns)})
        missing_columns = self.REQUIRED_COLUMNS - set(dataframe.columns)
        if missing_columns:
            raise ValueError(f"DataFrame is missing required columns: {sorted(missing_columns)}")

        records: list[ParticipantOIRecord] = []
        for row in dataframe.itertuples(index=False):
            records.append(
                ParticipantOIRecord(
                    participant_name=str(row.participant_name),
                    participant_type=str(row.participant_type),
                    long_oi=float(row.long_oi),
                    short_oi=float(row.short_oi),
                    long_change=float(row.long_change),
                    short_change=float(row.short_change),
                    volume=float(row.volume),
                    net_oi=float(row.net_oi),
                )
            )
        return self.analyze(records)

    def from_csv(self, path: Path | str) -> object:
        """Load open interest data from a CSV file and analyze it."""
        path_obj = Path(path)
        self.logger.info("Loading CSV file for OI service", extra={"path": str(path_obj)})
        dataframe = pd.read_csv(path_obj)
        return self.from_dataframe(dataframe)
