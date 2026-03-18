from __future__ import annotations

import pandas as pd

from smart_stock.strategies.base_strategy import BaseStrategy


class SMAcrossoverStrategy(BaseStrategy):
    """단순이동평균(SMA) 교차 전략.

    단기 SMA와 장기 SMA의 교차점을 기반으로 매수/매도 신호를 생성한다.
    - 단기 SMA > 장기 SMA: 신호 1 (매수)
    - 그 외: 신호 0 (보유/매도)

    초기 NaN 구간(rolling window 미달)은 0으로 채운다.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50) -> None:
        """SMA 교차 전략을 초기화한다.

        Parameters
        ----------
        short_window : int, optional
            단기 SMA 윈도우 크기 (기본값: 20)
        long_window : int, optional
            장기 SMA 윈도우 크기 (기본값: 50)

        Raises
        ------
        ValueError
            short_window >= long_window인 경우
        """
        if short_window >= long_window:
            msg = (
                f"short_window({short_window})은 "
                f"long_window({long_window})보다 작아야 합니다."
            )
            raise ValueError(msg)
        self.short_window = short_window
        self.long_window = long_window

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다.

        Returns
        -------
        str
            포맷: "SMA_{short_window}_{long_window}"
        """
        return f"SMA_{self.short_window}_{self.long_window}"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """SMA 교차 신호를 생성한다.

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

        # SMA 계산
        short_sma = df["Close"].rolling(window=self.short_window).mean()
        long_sma = df["Close"].rolling(window=self.long_window).mean()

        # 신호 생성: short > long → 1, 그 외 → 0
        signals = (short_sma > long_sma).astype(int)

        # 초기 NaN 구간을 0으로 채움
        signals = signals.fillna(0)

        return signals
