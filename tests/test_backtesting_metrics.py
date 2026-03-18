"""백테스팅 성과 지표 계산 모듈 테스트."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from smart_stock.backtesting.metrics import (
    max_drawdown,
    sharpe_ratio,
    total_return,
    win_rate,
)


class TestTotalReturn:
    """total_return 함수 테스트."""

    def test_positive_return(self) -> None:
        """포트폴리오가 증가한 경우."""
        portfolio = pd.Series([1000.0, 1100.0])
        result = total_return(portfolio, 1000.0)
        assert result == pytest.approx(10.0)

    def test_zero_return(self) -> None:
        """포트폴리오가 변하지 않은 경우."""
        portfolio = pd.Series([1000.0, 1000.0])
        result = total_return(portfolio, 1000.0)
        assert result == pytest.approx(0.0)

    def test_negative_return(self) -> None:
        """포트폴리오가 감소한 경우."""
        portfolio = pd.Series([1000.0, 900.0])
        result = total_return(portfolio, 1000.0)
        assert result == pytest.approx(-10.0)


class TestMaxDrawdown:
    """max_drawdown 함수 테스트."""

    def test_monotone_increase_no_drawdown(self) -> None:
        """단조 증가 시 최대 낙폭은 0."""
        portfolio = pd.Series([100.0, 110.0, 120.0, 130.0])
        result = max_drawdown(portfolio)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_known_drawdown(self) -> None:
        """알려진 최대 낙폭을 확인."""
        portfolio = pd.Series([100.0, 80.0, 90.0])
        result = max_drawdown(portfolio)
        # MDD = (80 - 100) / 100 * 100 = -20.0
        assert result == pytest.approx(-20.0)


class TestSharpeRatio:
    """sharpe_ratio 함수 테스트."""

    def test_constant_returns_zero(self) -> None:
        """상수 포트폴리오는 샤프 지수가 0."""
        portfolio = pd.Series([1000.0] * 100)
        result = sharpe_ratio(portfolio)
        assert result == pytest.approx(0.0)

    def test_increasing_portfolio_positive(self) -> None:
        """단조 증가 포트폴리오는 샤프 지수가 양수."""
        portfolio = pd.Series([100.0 + i for i in range(100)])
        result = sharpe_ratio(portfolio)
        assert result > 0


class TestWinRate:
    """win_rate 함수 테스트."""

    def test_empty_returns_nan(self) -> None:
        """빈 거래 리스트는 NaN을 반환."""
        result = win_rate([])
        assert math.isnan(result)

    def test_all_wins(self) -> None:
        """모든 거래가 수익인 경우."""
        result = win_rate([0.1, 0.2])
        assert result == pytest.approx(100.0)

    def test_all_losses(self) -> None:
        """모든 거래가 손실인 경우."""
        result = win_rate([-0.1, -0.2])
        assert result == pytest.approx(0.0)

    def test_mixed(self) -> None:
        """수익과 손실이 섞여 있는 경우."""
        result = win_rate([0.1, -0.1, 0.1])
        assert result == pytest.approx(66.666666, rel=0.01)
