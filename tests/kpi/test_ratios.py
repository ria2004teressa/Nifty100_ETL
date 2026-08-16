from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_has_mismatch,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets
)


def test_net_profit_margin_normal():
    result = net_profit_margin(
        20,
        100
    )

    assert result == 20.0


def test_net_profit_margin_zero_sales():
    result = net_profit_margin(
        20,
        0
    )

    assert result is None


def test_operating_profit_margin_normal():
    result = operating_profit_margin(
        30,
        100
    )

    assert result == 30.0


def test_opm_mismatch():
    result = opm_has_mismatch(
        30.0,
        32.0
    )

    assert result is True


def test_return_on_equity_normal():
    result = return_on_equity(
        20,
        50,
        50
    )

    assert result == 20.0


def test_return_on_equity_negative_equity():
    result = return_on_equity(
        20,
        -60,
        50
    )

    assert result is None


def test_return_on_capital_employed():
    result = return_on_capital_employed(
        30,
        50,
        50,
        100
    )

    assert result == 15.0


def test_return_on_assets_zero_assets():
    result = return_on_assets(
        20,
        0
    )

    assert result is None

    # ============================================================
# DAY 09 TESTS
# ============================================================

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity_normal():
    result = debt_to_equity(
        50,
        100,
        100
    )

    assert result == 0.25


def test_debt_to_equity_debt_free():
    result = debt_to_equity(
        0,
        100,
        100
    )

    assert result == 0


def test_high_leverage_flag():
    result = high_leverage_flag(
        6,
        "Technology"
    )

    assert result is True


def test_financials_high_leverage_suppressed():
    result = high_leverage_flag(
        10,
        "Financials"
    )

    assert result is False


def test_interest_coverage_normal():
    result = interest_coverage_ratio(
        100,
        20,
        20
    )

    assert result == 6


def test_interest_zero_returns_none():
    result = interest_coverage_ratio(
        100,
        20,
        0
    )

    assert result is None


def test_debt_free_label():
    result = interest_coverage_label(
        None
    )

    assert result == "Debt Free"


def test_high_leverage_warning():
    result = interest_coverage_warning(
        1.2
    )

    assert result is True