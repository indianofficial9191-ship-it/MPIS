"""Institutional service entrypoint for MPIS."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from mpis.institutional.analyzer import InstitutionalAnalyzer
from mpis.institutional.models import ParticipantRecord, ParticipantType
from mpis.utils.logger import get_logger


class InstitutionalService:
    """Service layer for institutional psychology analysis."""

    REQUIRED_COLUMNS = {
        "participant_name",
        "participant_type",
        "equity_buy",
        "equity_sell",
        "equity_net",
        "future_buy",
        "future_sell",
        "future_net",
        "option_buy",
        "option_sell",
        "option_net",
        "oi_change",
        "volume",
    }

    def __init__(self) -> None:
        self.logger = get_logger("mpis.institutional.service")
        self.analyzer = InstitutionalAnalyzer()

    def analyze(self, records: Iterable[ParticipantRecord]) -> "InstitutionalSignal":
        """Analyze a sequence of participant records."""
        records_list = list(records)
        self.logger.info("Analyzing participant records", extra={"count": len(records_list)})
        return self.analyzer.analyze(records_list)

    def from_dataframe(self, dataframe: pd.DataFrame) -> "InstitutionalSignal":
        """Create participant records from a DataFrame and analyze them."""
        self.logger.info("Parsing DataFrame into participant records", extra={"columns": list(dataframe.columns)})
        missing_columns = self.REQUIRED_COLUMNS - set(dataframe.columns)
        if missing_columns:
            raise ValueError(f"DataFrame is missing required columns: {sorted(missing_columns)}")

        records: list[ParticipantRecord] = []
        for row in dataframe.itertuples(index=False):
            records.append(
                ParticipantRecord(
                    participant_name=str(row.participant_name),
                    participant_type=ParticipantType(str(row.participant_type)),
                    equity_buy=float(row.equity_buy),
                    equity_sell=float(row.equity_sell),
                    equity_net=float(row.equity_net),
                    future_buy=float(row.future_buy),
                    future_sell=float(row.future_sell),
                    future_net=float(row.future_net),
                    option_buy=float(row.option_buy),
                    option_sell=float(row.option_sell),
                    option_net=float(row.option_net),
                    oi_change=float(row.oi_change),
                    volume=float(row.volume),
                )
            )
        return self.analyze(records)

    def from_csv(self, path: Path | str) -> object:
        """Load a CSV file and analyze participant records."""
        path_obj = Path(path)
        self.logger.info("Loading CSV file", extra={"path": str(path_obj)})
        dataframe = pd.read_csv(path_obj)
        return self.from_dataframe(dataframe)
