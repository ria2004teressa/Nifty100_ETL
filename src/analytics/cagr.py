# ============================================================
# SPRINT 2 - DAY 10
# CAGR ENGINE
# ============================================================


def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR.

    Formula:
        CAGR = ((end / start) ** (1 / years) - 1) * 100

    Returns:
        (cagr_value, flag)

    Flags:
        None
        DECLINE_TO_LOSS
        TURNAROUND
        BOTH_NEGATIVE
        ZERO_BASE
        INSUFFICIENT
    """

    # --------------------------------------------------------
    # Check number of years
    # --------------------------------------------------------

    if years is None or years <= 0:
        return None, "INSUFFICIENT"

    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    if start_value is None or end_value is None:
        return None, "INSUFFICIENT"

    # --------------------------------------------------------
    # Zero starting value
    # --------------------------------------------------------

    if start_value == 0:
        return None, "ZERO_BASE"

    # --------------------------------------------------------
    # Positive -> Positive
    # --------------------------------------------------------

    if start_value > 0 and end_value > 0:

        cagr = (
            (end_value / start_value)
            ** (1 / years)
            - 1
        ) * 100

        return cagr, None

    # --------------------------------------------------------
    # Positive -> Negative
    # --------------------------------------------------------

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # --------------------------------------------------------
    # Negative -> Positive
    # --------------------------------------------------------

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # --------------------------------------------------------
    # Negative -> Negative
    # --------------------------------------------------------

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return None, "INSUFFICIENT"


# ============================================================
# HELPER FUNCTION
# ============================================================

def cagr_value(
    start_value,
    end_value,
    years
):
    """
    Return only the CAGR value.

    Returns None for all edge cases.
    """

    value, flag = calculate_cagr(
        start_value,
        end_value,
        years
    )

    return value


def cagr_flag(
    start_value,
    end_value,
    years
):
    """
    Return only the CAGR edge-case flag.

    Returns None for a normal CAGR calculation.
    """

    value, flag = calculate_cagr(
        start_value,
        end_value,
        years
    )

    return flag