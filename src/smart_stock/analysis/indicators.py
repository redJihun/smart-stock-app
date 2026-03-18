from __future__ import annotations

import pandas as pd


def sma(close: pd.Series, window: int) -> pd.Series:
    """단순 이동평균(Simple Moving Average)을 계산한다.

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    window : int
        윈도우 크기 (이동평균 기간)

    Returns
    -------
    pd.Series
        단순 이동평균 Series. 초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        window <= 0인 경우
    """
    if window <= 0:
        msg = f"window는 1 이상이어야 합니다. 현재: {window}"
        raise ValueError(msg)

    return close.rolling(window=window).mean()


def ema(close: pd.Series, span: int) -> pd.Series:
    """지수 이동평균(Exponential Moving Average)을 계산한다.

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    span : int
        EMA 기간(span)

    Returns
    -------
    pd.Series
        지수 이동평균 Series. 초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        span <= 0인 경우
    """
    if span <= 0:
        msg = f"span은 1 이상이어야 합니다. 현재: {span}"
        raise ValueError(msg)

    return close.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """상대강도지수(RSI)를 계산한다.

    Wilder's Smoothing을 사용하여 RSI를 계산한다.
    공식: RSI = 100 - (100 / (1 + RS)), RS = 평균상승 / 평균하강

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    period : int, optional
        RSI 계산 기간 (기본값: 14)

    Returns
    -------
    pd.Series
        RSI 값 (0~100). 초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        period <= 0인 경우
    """
    if period <= 0:
        msg = f"period는 1 이상이어야 합니다. 현재: {period}"
        raise ValueError(msg)

    diff = close.diff()
    gain = diff.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-diff.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD(Moving Average Convergence Divergence) 지표를 계산한다.

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    fast : int, optional
        빠른 EMA 기간 (기본값: 12)
    slow : int, optional
        느린 EMA 기간 (기본값: 26)
    signal : int, optional
        신호선 EMA 기간 (기본값: 9)

    Returns
    -------
    pd.DataFrame
        'macd', 'signal', 'histogram' 컬럼을 가진 DataFrame.
        초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        fast <= 0, slow <= 0, signal <= 0인 경우
        또는 fast >= slow인 경우
    """
    if fast <= 0:
        msg = f"fast는 1 이상이어야 합니다. 현재: {fast}"
        raise ValueError(msg)
    if slow <= 0:
        msg = f"slow는 1 이상이어야 합니다. 현재: {slow}"
        raise ValueError(msg)
    if signal <= 0:
        msg = f"signal은 1 이상이어야 합니다. 현재: {signal}"
        raise ValueError(msg)
    if fast >= slow:
        msg = f"fast({fast})는 slow({slow})보다 작아야 합니다."
        raise ValueError(msg)

    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_val = ema_fast - ema_slow
    signal_val = macd_val.ewm(span=signal, adjust=False).mean()
    histogram = macd_val - signal_val

    return pd.DataFrame(
        {
            "macd": macd_val,
            "signal": signal_val,
            "histogram": histogram,
        },
        index=close.index,
    )


def stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k: int = 14,
    d: int = 3,
) -> pd.DataFrame:
    """스토캐스틱 오실레이터(Stochastic Oscillator) 지표를 계산한다.

    Parameters
    ----------
    high : pd.Series
        고가 데이터
    low : pd.Series
        저가 데이터
    close : pd.Series
        종가 데이터
    k : int, optional
        %K 계산 기간 (기본값: 14)
    d : int, optional
        %D 계산 기간 (기본값: 3)

    Returns
    -------
    pd.DataFrame
        'k', 'd' 컬럼을 가진 DataFrame. 각 값은 0~100.
        초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        k <= 0, d <= 0인 경우
    """
    if k <= 0:
        msg = f"k는 1 이상이어야 합니다. 현재: {k}"
        raise ValueError(msg)
    if d <= 0:
        msg = f"d는 1 이상이어야 합니다. 현재: {d}"
        raise ValueError(msg)

    lowest_low = low.rolling(window=k).min()
    highest_high = high.rolling(window=k).max()
    k_val = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_val = k_val.rolling(window=d).mean()

    return pd.DataFrame(
        {
            "k": k_val,
            "d": d_val,
        },
        index=close.index,
    )


def bollinger_bands(
    close: pd.Series,
    window: int = 20,
    std_dev: float = 2.0,
) -> pd.DataFrame:
    """볼린저 밴드(Bollinger Bands) 지표를 계산한다.

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    window : int, optional
        이동평균 윈도우 크기 (기본값: 20)
    std_dev : float, optional
        표준편차 배수 (기본값: 2.0)

    Returns
    -------
    pd.DataFrame
        'upper', 'middle', 'lower', 'bandwidth' 컬럼을 가진 DataFrame.
        - upper: 상단 밴드
        - middle: 중심선 (이동평균)
        - lower: 하단 밴드
        - bandwidth: (upper - lower) / middle
        초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        window <= 0, std_dev <= 0인 경우
    """
    if window <= 0:
        msg = f"window는 1 이상이어야 합니다. 현재: {window}"
        raise ValueError(msg)
    if std_dev <= 0:
        msg = f"std_dev는 0보다 커야 합니다. 현재: {std_dev}"
        raise ValueError(msg)

    middle = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    bandwidth = (upper - lower) / middle

    return pd.DataFrame(
        {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "bandwidth": bandwidth,
        },
        index=close.index,
    )


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """평균 진정 범위(Average True Range)를 계산한다.

    Parameters
    ----------
    high : pd.Series
        고가 데이터
    low : pd.Series
        저가 데이터
    close : pd.Series
        종가 데이터
    period : int, optional
        ATR 계산 기간 (기본값: 14)

    Returns
    -------
    pd.Series
        ATR 값. 초기 NaN 구간은 유지된다.

    Raises
    ------
    ValueError
        period <= 0인 경우
    """
    if period <= 0:
        msg = f"period는 1 이상이어야 합니다. 현재: {period}"
        raise ValueError(msg)

    # True Range 계산
    hl = high - low
    hc = (high - close.shift(1)).abs()
    lc = (low - close.shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    # ATR = TR의 지수이동평균 (Wilder's smoothing: alpha=1/period)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """온 밸런스 볼륨(On Balance Volume) 지표를 계산한다.

    Parameters
    ----------
    close : pd.Series
        종가 데이터
    volume : pd.Series
        거래량 데이터

    Returns
    -------
    pd.Series
        OBV 값. 누적 거래량 지표.

    Raises
    ------
    ValueError
        close와 volume의 길이가 다른 경우
    """
    if len(close) != len(volume):
        msg = "close와 volume의 길이가 같아야 합니다."
        raise ValueError(msg)

    diff = close.diff()
    direction = diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * volume).cumsum()
