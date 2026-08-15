from src.etl.normaliser import normalize_year, normalize_ticker


# ==============================
# normalize_year tests
# ==============================

def test_year_1():
    assert normalize_year("2024") == 2024


def test_year_2():
    assert normalize_year(" 2024 ") == 2024


def test_year_3():
    assert normalize_year(2024) == 2024


def test_year_4():
    assert normalize_year("2023") == 2023


def test_year_5():
    assert normalize_year(" 2023") == 2023


def test_year_6():
    assert normalize_year("2022 ") == 2022


def test_year_7():
    assert normalize_year(2022) == 2022


def test_year_8():
    assert normalize_year("2021") == 2021


def test_year_9():
    assert normalize_year("2020") == 2020


def test_year_10():
    assert normalize_year("2019") == 2019


def test_year_11():
    assert normalize_year(" 2018 ") == 2018


def test_year_12():
    assert normalize_year(2017) == 2017


def test_year_13():
    assert normalize_year("2016") == 2016


def test_year_14():
    assert normalize_year("2015") == 2015


def test_year_15():
    assert normalize_year(2014) == 2014


def test_year_16():
    assert normalize_year("2013") == 2013


def test_year_17():
    assert normalize_year(" 2012 ") == 2012


def test_year_18():
    assert normalize_year(2011) == 2011


def test_year_19():
    assert normalize_year("2010") == 2010


def test_year_20():
    assert normalize_year(" 2009 ") == 2009


# ==============================
# normalize_ticker tests
# ==============================

def test_ticker_1():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_2():
    assert normalize_ticker(" TCS ") == "TCS"


def test_ticker_3():
    assert normalize_ticker("infy") == "INFY"


def test_ticker_4():
    assert normalize_ticker(" INFY ") == "INFY"


def test_ticker_5():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_ticker_6():
    assert normalize_ticker(" reliance ") == "RELIANCE"


def test_ticker_7():
    assert normalize_ticker("hdfcbank") == "HDFCBANK"


def test_ticker_8():
    assert normalize_ticker(" HDFCBANK ") == "HDFCBANK"


def test_ticker_9():
    assert normalize_ticker("icicibank") == "ICICIBANK"


def test_ticker_10():
    assert normalize_ticker(" ICICIBANK ") == "ICICIBANK"


def test_ticker_11():
    assert normalize_ticker("abc") == "ABC"


def test_ticker_12():
    assert normalize_ticker(" xyz ") == "XYZ"


def test_ticker_13():
    assert normalize_ticker("itc") == "ITC"


def test_ticker_14():
    assert normalize_ticker("  SBI  ") == "SBI"


def test_ticker_15():
    assert normalize_ticker("LT") == "LT"