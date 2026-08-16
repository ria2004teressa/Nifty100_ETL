# ============================================================
# SPRINT 2 - DAY 11
# CASH FLOW KPIs & CAPITAL ALLOCATION
# ============================================================


def free_cash_flow(
    operating_activity,
    investing_activity
):
    """
    Free Cash Flow = Operating Activity + Investing Activity
    """

    if operating_activity is None:
        operating_activity = 0

    if investing_activity is None:
        investing_activity = 0

    return operating_activity + investing_activity


def cfo_quality_score(
    cfo,
    pat
):
    """
    CFO Quality Score = CFO / PAT

    Returns None if PAT = 0.
    """

    if cfo is None or pat is None:
        return None

    if pat == 0:
        return None

    return cfo / pat


def cfo_quality_label(
    score
):
    """
    > 1.0     = High Quality
    0.5 - 1.0 = Moderate
    < 0.5     = Accrual Risk
    """

    if score is None:
        return None

    if score > 1.0:
        return "High Quality"

    if score >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(
    investing_activity,
    sales
):
    """
    CapEx Intensity = abs(Investing Activity) / Sales * 100

    Returns None if sales = 0.
    """

    if investing_activity is None:
        return None

    if sales is None or sales == 0:
        return None

    return (
        abs(investing_activity)
        / sales
    ) * 100


def capex_intensity_label(
    intensity
):
    """
    < 3%      = Asset Light
    3% - 8%    = Moderate
    > 8%       = Capital Intensive
    """

    if intensity is None:
        return None

    if intensity < 3:
        return "Asset Light"

    if intensity <= 8:
        return "Moderate"

    return "Capital Intensive"


def fcf_conversion_rate(
    free_cash_flow_value,
    operating_profit
):
    """
    FCF Conversion Rate =
    FCF / Operating Profit * 100

    Returns None if operating profit = 0.
    """

    if free_cash_flow_value is None:
        return None

    if operating_profit is None or operating_profit == 0:
        return None

    return (
        free_cash_flow_value
        / operating_profit
    ) * 100


def sign_of(value):
    """
    Convert a number into:
        + for positive
        - for negative
        0 for zero
    """

    if value is None:
        return "0"

    if value > 0:
        return "+"

    if value < 0:
        return "-"

    return "0"


def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None
):
    """
    Classify capital allocation based on
    the signs of CFO, CFI and CFF.

    Patterns:

    (+,-,-) = Reinvestor
    (+,-,-) with high CFO/PAT = Shareholder Returns
    (+,+,-) = Liquidating Assets
    (-,+,+) = Distress Signal
    (-,-,+) = Growth Funded by Debt
    (+,+,+) = Cash Accumulator
    (-,-,-) = Pre-Revenue
    (+,-,+) = Mixed
    """

    cfo_sign = sign_of(cfo)
    cfi_sign = sign_of(cfi)
    cff_sign = sign_of(cff)

    pattern = (
        cfo_sign,
        cfi_sign,
        cff_sign
    )

    # High CFO/PAT takes priority
    if pattern == ("+", "-", "-"):

        if (
            cfo_pat_ratio is not None
            and cfo_pat_ratio > 1.0
        ):
            return "Shareholder Returns"

        return "Reinvestor"

    if pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return "Distress Signal"

    if pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    if pattern == ("+", "-", "+"):
        return "Mixed"

    return "Unclassified"