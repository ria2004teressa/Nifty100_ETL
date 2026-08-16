# ============================================================
# DAY 11 - CASH FLOW KPI TESTS
# ============================================================

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    cfo_quality_label,
    capex_intensity,
    capex_intensity_label,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


# ============================================================
# TEST 1 - FREE CASH FLOW
# ============================================================

def test_free_cash_flow():

    result = free_cash_flow(
        100,
        -40
    )

    assert result == 60


# ============================================================
# TEST 2 - NEGATIVE FCF ALLOWED
# ============================================================

def test_negative_free_cash_flow():

    result = free_cash_flow(
        50,
        -100
    )

    assert result == -50


# ============================================================
# TEST 3 - CFO QUALITY
# ============================================================

def test_cfo_quality_score():

    result = cfo_quality_score(
        120,
        100
    )

    assert result == 1.2


# ============================================================
# TEST 4 - PAT ZERO
# ============================================================

def test_cfo_quality_zero_pat():

    result = cfo_quality_score(
        100,
        0
    )

    assert result is None


# ============================================================
# TEST 5 - HIGH QUALITY
# ============================================================

def test_high_quality_label():

    result = cfo_quality_label(
        1.2
    )

    assert result == "High Quality"


# ============================================================
# TEST 6 - MODERATE QUALITY
# ============================================================

def test_moderate_quality_label():

    result = cfo_quality_label(
        0.7
    )

    assert result == "Moderate"


# ============================================================
# TEST 7 - ACCRUAL RISK
# ============================================================

def test_accrual_risk_label():

    result = cfo_quality_label(
        0.3
    )

    assert result == "Accrual Risk"


# ============================================================
# TEST 8 - CAPEX INTENSITY
# ============================================================

def test_capex_intensity():

    result = capex_intensity(
        -20,
        1000
    )

    assert result == 2.0


# ============================================================
# TEST 9 - ASSET LIGHT
# ============================================================

def test_asset_light():

    result = capex_intensity_label(
        2.5
    )

    assert result == "Asset Light"


# ============================================================
# TEST 10 - MODERATE CAPEX
# ============================================================

def test_moderate_capex():

    result = capex_intensity_label(
        5
    )

    assert result == "Moderate"


# ============================================================
# TEST 11 - CAPITAL INTENSIVE
# ============================================================

def test_capital_intensive():

    result = capex_intensity_label(
        10
    )

    assert result == "Capital Intensive"


# ============================================================
# TEST 12 - FCF CONVERSION
# ============================================================

def test_fcf_conversion():

    result = fcf_conversion_rate(
        60,
        100
    )

    assert result == 60


# ============================================================
# TEST 13 - ZERO OPERATING PROFIT
# ============================================================

def test_fcf_conversion_zero_profit():

    result = fcf_conversion_rate(
        60,
        0
    )

    assert result is None


# ============================================================
# TEST 14 - REINVESTOR
# ============================================================

def test_reinvestor():

    result = capital_allocation_pattern(
        100,
        -50,
        -20
    )

    assert result == "Reinvestor"


# ============================================================
# TEST 15 - SHAREHOLDER RETURNS
# ============================================================

def test_shareholder_returns():

    result = capital_allocation_pattern(
        150,
        -50,
        -20,
        1.5
    )

    assert result == "Shareholder Returns"


# ============================================================
# TEST 16 - LIQUIDATING ASSETS
# ============================================================

def test_liquidating_assets():

    result = capital_allocation_pattern(
        100,
        50,
        -20
    )

    assert result == "Liquidating Assets"


# ============================================================
# TEST 17 - DISTRESS SIGNAL
# ============================================================

def test_distress_signal():

    result = capital_allocation_pattern(
        -100,
        50,
        20
    )

    assert result == "Distress Signal"


# ============================================================
# TEST 18 - GROWTH FUNDED BY DEBT
# ============================================================

def test_growth_funded_by_debt():

    result = capital_allocation_pattern(
        -100,
        -50,
        20
    )

    assert result == "Growth Funded by Debt"


# ============================================================
# TEST 19 - CASH ACCUMULATOR
# ============================================================

def test_cash_accumulator():

    result = capital_allocation_pattern(
        100,
        50,
        20
    )

    assert result == "Cash Accumulator"


# ============================================================
# TEST 20 - PRE-REVENUE
# ============================================================

def test_pre_revenue():

    result = capital_allocation_pattern(
        -100,
        -50,
        -20
    )

    assert result == "Pre-Revenue"


# ============================================================
# TEST 21 - MIXED
# ============================================================

def test_mixed():

    result = capital_allocation_pattern(
        100,
        -50,
        20
    )

    assert result == "Mixed"