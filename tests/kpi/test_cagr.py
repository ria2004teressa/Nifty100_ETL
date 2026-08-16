# ============================================================
# DAY 10 - CAGR TESTS
# ============================================================

from src.analytics.cagr import (
    calculate_cagr,
    cagr_value,
    cagr_flag,
)


# ============================================================
# TEST 1 - NORMAL CAGR
# ============================================================

def test_normal_cagr():

    value, flag = calculate_cagr(
        100,
        121,
        2
    )

    assert round(value, 2) == 10.0
    assert flag is None


# ============================================================
# TEST 2 - ZERO BASE
# ============================================================

def test_zero_base():

    value, flag = calculate_cagr(
        0,
        100,
        5
    )

    assert value is None
    assert flag == "ZERO_BASE"


# ============================================================
# TEST 3 - POSITIVE TO NEGATIVE
# ============================================================

def test_decline_to_loss():

    value, flag = calculate_cagr(
        100,
        -20,
        5
    )

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


# ============================================================
# TEST 4 - NEGATIVE TO POSITIVE
# ============================================================

def test_turnaround():

    value, flag = calculate_cagr(
        -100,
        50,
        5
    )

    assert value is None
    assert flag == "TURNAROUND"


# ============================================================
# TEST 5 - BOTH NEGATIVE
# ============================================================

def test_both_negative():

    value, flag = calculate_cagr(
        -100,
        -50,
        5
    )

    assert value is None
    assert flag == "BOTH_NEGATIVE"


# ============================================================
# TEST 6 - INSUFFICIENT YEARS
# ============================================================

def test_insufficient_years():

    value, flag = calculate_cagr(
        100,
        200,
        0
    )

    assert value is None
    assert flag == "INSUFFICIENT"


# ============================================================
# TEST 7 - MISSING START VALUE
# ============================================================

def test_missing_start():

    value, flag = calculate_cagr(
        None,
        100,
        5
    )

    assert value is None
    assert flag == "INSUFFICIENT"


# ============================================================
# TEST 8 - MISSING END VALUE
# ============================================================

def test_missing_end():

    value, flag = calculate_cagr(
        100,
        None,
        5
    )

    assert value is None
    assert flag == "INSUFFICIENT"


# ============================================================
# TEST 9 - CAGR VALUE HELPER
# ============================================================

def test_cagr_value_helper():

    value = cagr_value(
        100,
        121,
        2
    )

    assert round(value, 2) == 10.0


# ============================================================
# TEST 10 - CAGR FLAG HELPER
# ============================================================

def test_cagr_flag_helper():

    flag = cagr_flag(
        -100,
        100,
        5
    )

    assert flag == "TURNAROUND"