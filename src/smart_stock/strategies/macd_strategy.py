from __future__ import annotations

import pandas as pd

from smart_stock.strategies.base_strategy import BaseStrategy


class MACDStrategy(BaseStrategy):
    """MACD(Moving Average Convergence Divergence) 전략.

    두 지수이동평균(EMA)의 차이(MACD line)와 신호선의 교차를 기반으로
    매수/매도 신호를 생성한다.
    - MACD line > 신호선: 신호 1 (매수)
    - 그 외: 신호 0 (보유/매도)

    초기 NaN 구간은 0으로 채운다.
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> None:
        """MACD 전략을 초기화한다.

        Parameters
        ----------
        fast_period : int, optional
            빠른 EMA 주기 (기본값: 12)
        slow_period : int, optional
            느린 EMA 주기 (기본값: 26)
        signal_period : int, optional
            신호선 EMA 주기 (기본값: 9)

        Raises
        ------
        ValueError
            fast_period >= slow_period, fast_period < 1, 또는
            signal_period < 1인 경우
        """
        if fast_period < 1:
            msg = "fast_period는 1 이상이어야 합니다."
            raise ValueError(msg)
        if slow_period < 1:
            msg = "slow_period는 1 이상이어야 합니다."
            raise ValueError(msg)
        if fast_period >= slow_period:
            msg = (
                f"fast_period({fast_period})는 "
                f"slow_period({slow_period})보다 작아야 합니다."
            )
            raise ValueError(msg)
        if signal_period < 1:
            msg = "signal_period는 1 이상이어야 합니다."
            raise ValueError(msg)

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다.

        Returns
        -------
        str
            포맷: "MACD_{fast_period}_{slow_period}_{signal_period}"
        """
        return f"MACD_{self.fast_period}_{self.slow_period}_{self.signal_period}"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """MACD 신호를 생성한다.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV 데이터. 필수 컬럼: ["Open", "High", "Low", "Close", "Volume"]
            인덱스는 DatetimeIndex여야 한다.

        Returns
        -------
        pd.Series
            신호 Series. 값은 0(보유/매도) 또는 1(매수)이고,
            인덱스는 입력 df와 동일하다.
            초기 NaN 구간은 0으로 채워진다.

        Raises
        ------
        ValueError
            필수 컬럼이 없거나 인덱스가 DatetimeIndex가 아닌 경우
        """
        self.validate_dataframe(df)

        # 빠른 EMA와 느린 EMA 계산
        ema_fast = df["Close"].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=self.slow_period, adjust=False).mean()

        # MACD line = fast EMA - slow EMA
        macd_line = ema_fast - ema_slow

        # 신호선 = MACD line의 EMA
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # 신호 생성: MACD line > 신호선 → 1, 그 외 → 0
        signals = (macd_line > signal_line).astype(int)

        # 초기 NaN 구간을 0으로 채움
        signals = signals.fillna(0)

        return signals
