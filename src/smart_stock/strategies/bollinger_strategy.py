from __future__ import annotations

import pandas as pd

from smart_stock.strategies.base_strategy import BaseStrategy


class BollingerBandStrategy(BaseStrategy):
    """볼린저밴드(Bollinger Bands) 전략.

    이동평균과 표준편차를 기반으로 상단/중단/하단 밴드를 계산하고,
    가격이 하단 밴드 아래로 내려갈 때 매수 신호를 생성한다.
    - Close < 하단 밴드: 신호 1 (과매도 상태, 매수)
    - 그 외: 신호 0 (보유/매도)

    초기 NaN 구간(rolling window 미달)은 0으로 채운다.
    """

    def __init__(self, period: int = 20, num_std: float = 2.0) -> None:
        """볼린저밴드 전략을 초기화한다.

        Parameters
        ----------
        period : int, optional
            이동평균 윈도우 크기 (기본값: 20)
        num_std : float, optional
            표준편차 배수 (기본값: 2.0)

        Raises
        ------
        ValueError
            period < 2인 경우 또는 num_std <= 0인 경우
        """
        if period < 2:
            msg = f"period는 2 이상이어야 합니다. 현재: {period}"
            raise ValueError(msg)
        if num_std <= 0:
            msg = f"num_std는 0보다 커야 합니다. 현재: {num_std}"
            raise ValueError(msg)

        self.period = period
        self.num_std = num_std

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다.

        Returns
        -------
        str
            포맷: "BB_{period}_{num_std}"
        """
        return f"BB_{self.period}_{self.num_std}"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """볼린저밴드 신호를 생성한다.

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

        # 중단(이동평균) 계산
        middle = df["Close"].rolling(window=self.period).mean()

        # 표준편차 계산
        std = df["Close"].rolling(window=self.period).std()

        # 하단 밴드 계산
        lower = middle - self.num_std * std

        # 신호 생성: Close < 하단 밴드 → 1, 그 외 → 0
        signals = (df["Close"] < lower).astype(int)

        # 초기 NaN 구간을 0으로 채움
        signals = signals.fillna(0)

        return signals
