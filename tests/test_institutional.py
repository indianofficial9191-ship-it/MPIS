import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from mpis.institutional.analyzer import InstitutionalAnalyzer
from mpis.institutional.classifier import InstitutionalClassifier
from mpis.institutional.models import ConfidenceLevel, InstitutionalSignal, MarketState, ParticipantRecord, ParticipantType
from mpis.institutional.participant import ParticipantHelper
from mpis.institutional.scoring import InstitutionalScorer
from mpis.institutional.service import InstitutionalService


def create_sample_record(participant_type: ParticipantType, net: float) -> ParticipantRecord:
    return ParticipantRecord(
        participant_name=f"participant_{participant_type.value}",
        participant_type=participant_type,
        equity_buy=net if net > 0 else 0.0,
        equity_sell=-net if net < 0 else 0.0,
        equity_net=net,
        future_buy=0.0,
        future_sell=0.0,
        future_net=0.0,
        option_buy=0.0,
        option_sell=0.0,
        option_net=0.0,
        oi_change=0.0,
        volume=1_000.0,
    )


def test_participant_helper_calculations() -> None:
    record = create_sample_record(ParticipantType.FII, 500_000.0)
    helper = ParticipantHelper(record)

    assert helper.net_equity() == 500_000.0
    assert helper.net_future() == 0.0
    assert helper.net_option() == 0.0
    assert helper.net_position() == 500_000.0
    assert helper.is_buyer() is True
    assert helper.is_seller() is False


def test_participant_record_validation() -> None:
    with pytest.raises(ValueError):
        ParticipantRecord(
            participant_name="invalid",
            participant_type=ParticipantType.DII,
            equity_buy=-1.0,
            equity_sell=0.0,
            equity_net=-1.0,
            future_buy=0.0,
            future_sell=0.0,
            future_net=0.0,
            option_buy=0.0,
            option_sell=0.0,
            option_net=0.0,
            oi_change=0.0,
            volume=0.0,
        )


def test_psychology_engine_detects_accumulation_and_distribution() -> None:
    records = [
        create_sample_record(ParticipantType.FII, 100_000.0),
        create_sample_record(ParticipantType.DII, 200_000.0),
        create_sample_record(ParticipantType.PRO, -150_000.0),
    ]

    analyzer = InstitutionalAnalyzer()
    signal = analyzer.analyze(records)

    assert isinstance(signal, InstitutionalSignal)
    assert signal.direction in {
        MarketState.BULLISH,
        MarketState.SLIGHT_BULLISH,
        MarketState.NEUTRAL,
        MarketState.BEARISH,
    }
    assert signal.confidence in ConfidenceLevel
    assert isinstance(signal.score, float)
    assert isinstance(signal.participant_scores, dict)
    assert signal.participant_scores.get("FII", None) is not None


def test_classifier_confidence_thresholds() -> None:
    assert InstitutionalClassifier.classify_confidence(90.0) == ConfidenceLevel.VERY_HIGH
    assert InstitutionalClassifier.classify_confidence(75.0) == ConfidenceLevel.HIGH
    assert InstitutionalClassifier.classify_confidence(60.0) == ConfidenceLevel.MEDIUM
    assert InstitutionalClassifier.classify_confidence(10.0) == ConfidenceLevel.LOW


def test_classifier_market_state_thresholds() -> None:
    assert InstitutionalClassifier.classify_market_state(100.0, 20.0) == MarketState.STRONG_BULLISH
    assert InstitutionalClassifier.classify_market_state(65.0, 40.0) == MarketState.BULLISH
    assert InstitutionalClassifier.classify_market_state(35.0, 30.0) == MarketState.SLIGHT_BULLISH
    assert InstitutionalClassifier.classify_market_state(20.0, 35.0) == MarketState.SLIGHT_BEARISH
    assert InstitutionalClassifier.classify_market_state(10.0, 45.0) == MarketState.BEARISH
    assert InstitutionalClassifier.classify_market_state(5.0, 80.0) == MarketState.STRONG_BEARISH
    assert InstitutionalClassifier.classify_market_state(50.0, 50.0) == MarketState.NEUTRAL


def test_institutional_scorer_compute_scores_and_normalize() -> None:
    records = [
        create_sample_record(ParticipantType.FII, 2_000_000.0),
        create_sample_record(ParticipantType.DII, -1_000_000.0),
        create_sample_record(ParticipantType.PRO, 500_000.0),
        create_sample_record(ParticipantType.CLIENT, 100_000.0),
    ]

    scores = InstitutionalScorer.compute_scores(records)
    assert scores["FII"] > 0.0
    assert isinstance(scores["DII"], float)

    normalized = InstitutionalScorer.normalize_score(scores)
    assert 0.0 <= normalized <= 100.0


def test_institutional_service_from_dataframe(tmp_path: Path) -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "equity_buy": 100000.0,
                "equity_sell": 0.0,
                "equity_net": 100000.0,
                "future_buy": 0.0,
                "future_sell": 0.0,
                "future_net": 0.0,
                "option_buy": 0.0,
                "option_sell": 0.0,
                "option_net": 0.0,
                "oi_change": 5000.0,
                "volume": 200000.0,
            }
        ]
    )

    service = InstitutionalService()
    signal = service.from_dataframe(dataframe)

    assert isinstance(signal, InstitutionalSignal)
    assert signal.direction in MarketState
    assert signal.confidence in ConfidenceLevel

    csv_path = tmp_path / "institutional.csv"
    dataframe.to_csv(csv_path, index=False)
    signal_csv = service.from_csv(csv_path)
    assert signal_csv == signal


def test_institutional_service_missing_columns_raises() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "equity_buy": 100000.0,
                "equity_sell": 0.0,
                "equity_net": 100000.0,
                "future_buy": 0.0,
                "future_sell": 0.0,
            }
        ]
    )

    service = InstitutionalService()
    with pytest.raises(ValueError):
        service.from_dataframe(dataframe)
