from datetime import datetime

from mpis.pipeline.pipeline import MpisPipeline, PipelineResult
from mpis.psychology.models import TrendContext, TrendStrength
from mpis.psychology.premium_discount import PremiumDiscountAnalysis, ZoneType
from mpis.psychology.score import PsychologyScore, MarketBias
from mpis.psychology.fusion import TradeFusionResult, TradeDecision
from mpis.psychology.probability import ProbabilityResult


class DummyMarketStructure:
    def __init__(self, calls: list):
        self.calls = calls

    def analyze(self, df):
        self.calls.append("market_structure")
        # return a list of dummy swings
        return [type("S", (), {"start_price": 100.0, "end_price": 105.0})()]


class DummyLiquidity:
    def __init__(self, calls: list):
        self.calls = calls

    def analyze(self, candles):
        self.calls.append("liquidity")
        return {"liquidity": True}


class DummySMC:
    def __init__(self, calls: list):
        self.calls = calls

    def analyze(self, candles):
        self.calls.append("smc")
        return {"smc": True}


class DummyTrend:
    def __init__(self, calls: list, trend_context: TrendContext):
        self.calls = calls
        self.trend_context = trend_context

    def analyze(self, *args, **kwargs):
        self.calls.append("trend")
        return self.trend_context


class DummyPremium:
    def __init__(self, calls: list, premium: PremiumDiscountAnalysis):
        self.calls = calls
        self.premium = premium

    def analyze(self, current_price, sh, sl):
        self.calls.append("premium")
        return self.premium


class DummyPsychology:
    def __init__(self, calls: list, psychology: PsychologyScore):
        self.calls = calls
        self.psychology = psychology

    def analyze(self, trend, premium, liquidity, smc):
        self.calls.append("psychology")
        return self.psychology


class DummyFusion:
    def __init__(self, calls: list, fusion: TradeFusionResult):
        self.calls = calls
        self.fusion = fusion

    def analyze(self, psychology, trend, premium, liquidity, smc):
        self.calls.append("fusion")
        return self.fusion


class DummyProbability:
    def __init__(self, calls: list):
        self.calls = calls

    def analyze(self, fusion):
        self.calls.append("probability")
        # return a simple dict-like object
        return {"probability": 90.0}


def test_pipeline_execution_order_and_result():
    calls = []

    trend_context = TrendContext(
        trend=TrendStrength.BULLISH,
        confidence=0.8,
        bos_confirmed=True,
        choch_confirmed=False,
        mss_confirmed=True,
        swing_highs=[105.0],
        swing_lows=[100.0],
        timestamp=datetime.utcnow(),
    )

    premium = PremiumDiscountAnalysis(
        current_price=103.0,
        swing_high=105.0,
        swing_low=100.0,
        equilibrium=102.5,
        zone=ZoneType.PREMIUM,
        premium_percent=60.0,
        discount_percent=40.0,
    )

    psychology = PsychologyScore(bullish_score=40.0, bearish_score=10.0, confidence=70.0, bias=MarketBias.BUY, reasons=["test"]) 

    fusion = TradeFusionResult(decision=TradeDecision.BUY, confidence=70.0, risk_score=20.0, reward_score=50.0, reasons=["fused"]) 

    market = DummyMarketStructure(calls)
    liquidity = DummyLiquidity(calls)
    smc = DummySMC(calls)
    trend = DummyTrend(calls, trend_context)
    premium_engine = DummyPremium(calls, premium)
    psych_engine = DummyPsychology(calls, psychology)
    fusion_engine = DummyFusion(calls, fusion)
    prob_engine = DummyProbability(calls)

    pipeline = MpisPipeline(
        market_structure_engine=market,
        liquidity_engine=liquidity,
        smc_engine=smc,
        trend_engine=trend,
        premium_engine=premium_engine,
        psychology_engine=psych_engine,
        fusion_engine=fusion_engine,
        probability_engine=prob_engine,
    )

    # Run with dummy inputs
    result = pipeline.run(dataframe={}, candles=[], current_price=103.0)

    # Verify call order
    assert calls == ["market_structure", "liquidity", "smc", "trend", "premium", "psychology", "fusion", "probability"]

    # Verify result fields match expected outputs
    assert hasattr(result, "market_structure")
    assert result.premium_discount == premium
    assert result.psychology == psychology
    assert result.fusion == fusion
    assert isinstance(result.probability, dict)


def test_pipeline_handles_missing_engines_gracefully():
    # Only supply minimal engines
    calls = []
    market = DummyMarketStructure(calls)
    # leave others None or minimal
    pipeline = MpisPipeline(
        market_structure_engine=market,
        liquidity_engine=type("X", (), {})(),
        smc_engine=type("X", (), {})(),
        trend_engine=type("X", (), {})(),
        premium_engine=type("X", (), {})(),
        psychology_engine=type("X", (), {})(),
        fusion_engine=type("X", (), {})(),
        probability_engine=type("X", (), {})(),
    )

    result = pipeline.run(dataframe={}, candles=[], current_price=100.0)
    # Market structure should have been called
    assert calls == ["market_structure"]
    # Other fields should be None when engines don't implement analyze
    assert result.liquidity is None or result.liquidity == None
    assert result.smc is None or result.smc == None
    assert result.trend is None or result.trend == None
    assert result.premium_discount is None or result.premium_discount == None
    assert result.psychology is None or result.psychology == None
    assert result.fusion is None or result.fusion == None
    assert result.probability is None or result.probability == None
