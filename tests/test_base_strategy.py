"""테스트: BaseStrategy 추상 클래스"""

import pandas as pd
import pytest

from smart_stock.strategies.base_strategy import BaseStrategy

# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------


def _make_sample_df(rows: int = 5) -> pd.DataFrame:
    """Open/High/Low/Close/Volume 컬럼을 가진 샘플 DataFrame."""
    idx = pd.date_range("2024-01-02", periods=rows, freq="B")
    return pd.DataFrame(
        {
            "Open": [70000.0] * rows,
            "High": [71000.0] * rows,
            "Low": [69000.0] * rows,
            "Close": [70500.0] * rows,
            "Volume": [1_000_000] * rows,
        },
        index=idx,
    )


class ConcreteStrategy(BaseStrategy):
    """BaseStrategy 테스트용 구체적 구현체."""

    @property
    def name(self) -> str:
        """전략의 이름을 반환한다."""
        return "Concrete"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """모든 신호를 1.0으로 반환한다."""
        self.validate_dataframe(df)
        return pd.Series([1.0] * len(df), index=df.index)


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """테스트용 샘플 DataFrame."""
    return _make_sample_df()


@pytest.fixture()
def strategy() -> ConcreteStrategy:
    """테스트용 ConcreteStrategy 인스턴스."""
    return ConcreteStrategy()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_generate_signals_returns_series(
    strategy: ConcreteStrategy, sample_df: pd.DataFrame
) -> None:
    """generate_signals의 반환 타입이 pd.Series인지 확인한다."""
    result = strategy.generate_signals(sample_df)
    assert isinstance(result, pd.Series)


def test_validate_dataframe_passes_valid(
    strategy: ConcreteStrategy, sample_df: pd.DataFrame
) -> None:
    """유효한 DataFrame이 validate_dataframe을 통과한다."""
    # validate_dataframe이 ValueError를 발생시키지 않으면 통과
    try:
        strategy.validate_dataframe(sample_df)
    except ValueError:
        pytest.fail("validate_dataframe raised ValueError unexpectedly")


def test_validate_dataframe_raises_on_missing_columns(
    strategy: ConcreteStrategy, sample_df: pd.DataFrame
) -> None:
    """필수 컬럼이 누락되면 ValueError를 발생시킨다."""
    df_missing = sample_df.drop(columns=["Volume"])
    with pytest.raises(ValueError, match="필수 컬럼이 부족"):
        strategy.validate_dataframe(df_missing)


def test_name_returns_string(strategy: ConcreteStrategy) -> None:
    """name property의 반환 타입이 str인지 확인한다."""
    result = strategy.name
    assert isinstance(result, str)
    assert result == "Concrete"
