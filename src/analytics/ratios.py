# ============================================================
# SPRINT 2 - DAY 08
# PROFITABILITY RATIOS
# ============================================================


def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) * 100

    Returns None when sales is zero or unavailable.
    """

    if sales is None or sales == 0:
        return None

    if net_profit is None:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100

    Returns None when sales is zero or unavailable.
    """

    if sales is None or sales == 0:
        return None

    if operating_profit is None:
        return None

    return (operating_profit / sales) * 100


def opm_difference(computed_opm, source_opm):
    """
    Compare calculated OPM with the source OPM.

    Returns the absolute difference in percentage points.
    """

    if computed_opm is None or source_opm is None:
        return None

    return abs(computed_opm - source_opm)


def opm_has_mismatch(computed_opm, source_opm, threshold=1.0):
    """
    Returns True when the calculated OPM differs
    from the source OPM by more than 1 percentage point.
    """

    difference = opm_difference(
        computed_opm,
        source_opm
    )

    if difference is None:
        return False

    return difference > threshold


def return_on_equity(
    net_profit,
    equity_capital,
    reserves
):
    """
    ROE = Net Profit /
          (Equity Capital + Reserves) * 100

    Returns None when equity + reserves <= 0.
    """

    if net_profit is None:
        return None

    if equity_capital is None:
        equity_capital = 0

    if reserves is None:
        reserves = 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings
):
    """
    ROCE = EBIT /
           (Equity Capital + Reserves + Borrowings) * 100

    Returns None when the denominator is zero or negative.
    """

    if ebit is None:
        return None

    if equity_capital is None:
        equity_capital = 0

    if reserves is None:
        reserves = 0

    if borrowings is None:
        borrowings = 0

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets * 100

    Returns None when total assets is zero or unavailable.
    """

    if total_assets is None or total_assets == 0:
        return None

    if net_profit is None:
        return None

    return (net_profit / total_assets) * 100

# ============================================================
# DAY 09 - LEVERAGE & EFFICIENCY RATIOS
# ============================================================


def debt_to_equity(
    borrowings,
    equity_capital,
    reserves
):
    """
    Debt-to-Equity = Borrowings /
                     (Equity Capital + Reserves)

    Special rule:
    If borrowings = 0, return 0.
    """

    if borrowings is None:
        borrowings = 0

    if equity_capital is None:
        equity_capital = 0

    if reserves is None:
        reserves = 0

    equity = equity_capital + reserves

    # Debt-free company
    if borrowings == 0:
        return 0

    # Invalid/negative equity
    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(
    de_ratio,
    broad_sector
):
    """
    High leverage flag:
    D/E > 5 AND company is NOT in Financials sector.
    """

    if de_ratio is None:
        return False

    if broad_sector == "Financials":
        return False

    return de_ratio > 5


def interest_coverage_ratio(
    operating_profit,
    other_income,
    interest
):
    """
    ICR = (Operating Profit + Other Income) / Interest

    Returns None when interest = 0.
    """

    if interest is None or interest == 0:
        return None

    if operating_profit is None:
        operating_profit = 0

    if other_income is None:
        other_income = 0

    return (operating_profit + other_income) / interest


def interest_coverage_label(
    icr
):
    """
    If ICR is None, label the company as Debt Free.
    Otherwise return None.
    """

    if icr is None:
        return "Debt Free"

    return None


def interest_coverage_warning(
    icr
):
    """
    ICR below 1.5 indicates risk of not covering
    interest payments.
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(
    borrowings,
    investments
):
    """
    Net Debt = Borrowings - Investments
    """

    if borrowings is None:
        borrowings = 0

    if investments is None:
        investments = 0

    return borrowings - investments


def asset_turnover(
    sales,
    total_assets
):
    """
    Asset Turnover = Sales / Total Assets

    Returns None when total assets = 0.
    """

    if total_assets is None or total_assets == 0:
        return None

    if sales is None:
        return None

    return sales / total_assets