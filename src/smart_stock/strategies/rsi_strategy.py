from __future__ import annotations

import pandas as pd

from smart_stock.strategies.base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """상대강도지수(RSI) 전략.

    RSI 지표를 사용하여 과매도/과매수 상태를 감지하고 매수 신호를 생성한다.
    - RSI < oversold: 신호 1 (매수)
    - 그 외: 신호 0 (보유/매도)

    초기 NaN 구간(ewm 계산 미달)은 0으로 채운다.
    """

    def __init__(
        self,
        period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
    ) -> None:
        """RSI 전략을 초기화한다.

        Parameters
        ----------
        period : int, optional
            RSI 계산 기간 (기본값: 14)
        oversold : float, optional
            과매도 임계값 (기본값: 30.0)
        overbought : float, optional
            과매수 임계값 (기본값: 70.0)

        Raises
        ------
        ValueError
            period < 1, oversold <= 0, overbought >= 100, 또는
            oversold >= overbought인 경우
        """
        if period < 1:
            msg = "period는 1 이상이어야 합니다."
            raise ValueError(msg)
        if oversold <= 0:
            msg = "oversold는 0보다 커야 합니다."
            raise ValueError(msg)
        if overbought >= 100:
            msg = "overbought는 100보다 작아야 합니다."
            raise ValueError(msg)
        if oversold >= overbought:
            msg = "oversold는 overbought보다 작아야 합니다."
            raise ValueError(msg)

        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다.

        Returns
        -------
        str
            포맷: "RSI_{period}_{oversold}_{overbought}"
        """
        return f"RSI_{self.period}_{self.oversold}_{self.overbought}"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """RSI 신호를 생성한다.

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

        # RSI 계산
        diff = df["Close"].diff()
        gain = diff.clip(lower=0).ewm(alpha=1 / self.period, adjust=False).mean()
        loss = (-diff.clip(upper=0)).ewm(alpha=1 / self.period, adjust=False).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # 신호 생성: rsi < oversold → 1, 그 외 → 0
        signals = (rsi < self.oversold).astype(int)

        # 초기 NaN 구간을 0으로 채움
        signals = signals.fillna(0)

        return signals
