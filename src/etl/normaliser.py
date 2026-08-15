def normalize_year(year):
    """
    Convert year values into a clean integer.
    Examples:
        '2024' -> 2024
        ' 2023 ' -> 2023
        2022 -> 2022
    """
    if year is None:
        return None

    if str(year).strip() == "":
        return None

    return int(float(str(year).strip()))


def normalize_ticker(ticker):
    """
    Clean ticker values.
    Examples:
        ' tcs ' -> 'TCS'
        'infy' -> 'INFY'
    """
    if ticker is None:
        return ""

    return str(ticker).strip().upper()