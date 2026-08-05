from datetime import datetime

from mpis.institutional.context import (
    InstitutionalContextEngine,
    HTFBias,
    LiquidityClassification,
)


def test_htf_bias_all_bull_high_confidence() -> None:
    engine = InstitutionalContextEngine()
    ctx = engine.analyze(
        htf_bias={"daily": "bull", "weekly": "bull", "monthly": "bull"},
        internal_liquidity=0.9,
        external_liquidity=0.8,
        dealing_range=(100.0, 110.0),
        trend_alignment=True,
        liquidity_alignment=True,
        premium_discount_alignment="premium",
    )

    assert ctx.htf_bias["daily"] == HTFBias.BULL
    assert ctx.htf_score == 1.0
    assert ctx.internal_liquidity.classification == LiquidityClassification.HIGH
    assert ctx.external_liquidity.classification == LiquidityClassification.HIGH
    assert ctx.trend_alignment is True
    assert ctx.liquidity_alignment is True
    assert 0.8 <= ctx.confidence <= 1.0


def test_mixed_htf_bias_penalty() -> None:
    engine = InstitutionalContextEngine()
    ctx = engine.analyze(
        htf_bias={"daily": "bull", "weekly": "bear", "monthly": "neutral"},
        internal_liquidity=0.4,
        external_liquidity=0.2,
        dealing_range=(200.0, 220.0),
        trend_alignment=False,
        liquidity_alignment=False,
        premium_discount_alignment="discount",
    )

    # Mixed bulls and bears should reduce confidence
    assert 0.0 <= ctx.htf_score <= 1.0
    assert ctx.confidence < 0.6


def test_dealing_range_center_and_width() -> None:
    engine = InstitutionalContextEngine()
    ctx = engine.analyze(
        htf_bias={"daily": "neutral", "weekly": "neutral", "monthly": "neutral"},
        internal_liquidity=0.5,
        external_liquidity=0.5,
        dealing_range=(50.0, 60.0),
        trend_alignment=False,
        liquidity_alignment=True,
        premium_discount_alignment="equilibrium",
    )

    assert ctx.dealing_range.center == 55.0
    assert ctx.dealing_range.width == 10.0
    assert ctx.confidence >= 0.2


def test_invalid_dealing_range_raises() -> None:
    engine = InstitutionalContextEngine()
    try:
        engine.analyze(
            htf_bias={"daily": "bull", "weekly": "bull", "monthly": "bull"},
            internal_liquidity=0.1,
            external_liquidity=0.1,
            dealing_range=(10.0, 5.0),
            trend_alignment=False,
            liquidity_alignment=False,
            premium_discount_alignment="equilibrium",
        )
        assert False, "Expected ValueError for invalid dealing_range"
    except ValueError:
        pass


def test_premium_discount_alignment_affects_confidence() -> None:
    engine = InstitutionalContextEngine()
    ctx_premium = engine.analyze(
        htf_bias={"daily": "bull", "weekly": "bull", "monthly": "neutral"},
        internal_liquidity=0.6,
        external_liquidity=0.6,
        dealing_range=(100.0, 120.0),
        trend_alignment=True,
        liquidity_alignment=True,
        premium_discount_alignment="premium",
    )
    ctx_discount = engine.analyze(
        htf_bias={"daily": "bull", "weekly": "bull", "monthly": "neutral"},
        internal_liquidity=0.6,
        external_liquidity=0.6,
        dealing_range=(100.0, 120.0),
        trend_alignment=True,
        liquidity_alignment=True,
        premium_discount_alignment="discount",
    )

    # premium should align with bullish HTF and produce higher confidence than discount in this case
    assert ctx_premium.confidence >= ctx_discount.confidence
