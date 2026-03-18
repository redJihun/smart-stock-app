from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from smart_stock.data.schema import STANDARD_COLUMNS, validate_schema


class BaseStrategy(ABC):
    """
    거래 전략의 추상 기클래스.

    모든 전략은 이 클래스를 상속받아 다음을 구현해야 한다:
    - name(property): 전략의 이름 반환
    - generate_signals(df): 매수/매도 신호 생성

    사용 예:
        class SimpleMovingAverageStrategy(BaseStrategy):
            @property
            def name(self) -> str:
                return "SMA_20_50"

            def generate_signals(self, df: pd.DataFrame) -> pd.Series:
                self.validate_dataframe(df)
                sma_20 = df["Close"].rolling(20).mean()
                sma_50 = df["Close"].rolling(50).mean()
                return (sma_20 > sma_50).astype(int)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """전략의 이름을 반환한다."""
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        주어진 OHLCV 데이터에서 매수/매도 신호를 생성한다.

        Parameters
        ----------
        df : pd.DataFrame
            STANDARD_COLUMNS(Open, High, Low, Close, Volume)을 포함하는
            시계열 데이터프레임. 인덱스는 datetime이어야 한다.

        Returns
        -------
        pd.Series
            생성된 신호를 담은 Series.
            일반적으로:
            - 1 또는 True: 매수 신호
            - 0 또는 False: 매도/보유 신호
            - dtype은 구현에 따라 int, bool, float 등 가능

        Raises
        ------
        ValueError
            - df의 필수 컬럼이 부족하면
            - 인덱스가 datetime 타입이 아니면
        """
        pass

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """
        주어진 DataFrame이 표준 스키마를 만족하는지 검증한다.

        Parameters
        ----------
        df : pd.DataFrame
            검증할 데이터프레임

        Raises
        ------
        ValueError
            - STANDARD_COLUMNS 중 누락된 컬럼이 있으면
            - 인덱스가 datetime 타입이 아니면
        """
        if not validate_schema(df):
            missing = [col for col in STANDARD_COLUMNS if col not in df.columns]
            raise ValueError(
                f"DataFrame에 필수 컬럼이 부족합니다. 누락: {missing}\n"
                f"필수: {STANDARD_COLUMNS}"
            )

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError(
                f"인덱스가 DatetimeIndex여야 합니다. 현재: {type(df.index).__name__}"
            )
