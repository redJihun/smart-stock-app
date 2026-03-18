"""KIS API 분봉 데이터 조회 모듈 테스트."""

from __future__ import annotations

import os
from unittest.mock import patch

import pandas as pd
import pytest

# kis_client 모듈이 아직 구현되지 않았으므로, 동적으로 임포트
# 실제 구현 후에는 from smart_stock.data import kis_client로 변경


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_intraday_ohlcv(rows: int = 3) -> pd.DataFrame:
    """분봉 OHLCV 샘플 DataFrame."""
    idx = pd.date_range("2024-01-02 09:30", periods=rows, freq="5min")
    return pd.DataFrame(
        {
            "Open": [70000.0] * rows,
            "High": [71000.0] * rows,
            "Low": [69000.0] * rows,
            "Close": [70500.0] * rows,
            "Volume": [100_000] * rows,
        },
        index=idx,
    )


@pytest.fixture()
def sample_intraday_df() -> pd.DataFrame:
    """분봉 샘플 DataFrame."""
    return _make_intraday_ohlcv()


# ---------------------------------------------------------------------------
# TestFetchKrIntradayValidation
# ---------------------------------------------------------------------------


class TestFetchKrIntradayValidation:
    """interval 값 검증 테스트."""

    def test_invalid_interval_raises_valueerror(self) -> None:
        """허용되지 않는 interval 값 → ValueError."""
        # kis_client가 구현될 때까지 이 테스트는 import 실패 시 skip
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        with pytest.raises(ValueError, match="interval"):
            kis_client.fetch_kr_intraday("005930", "20240101", interval="2m")

    def test_valid_intervals_no_error(self) -> None:
        """허용된 interval 값 모두 정상 처리."""
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        # 각 interval마다 테스트 (실제 API 호출 없이 환경변수만 검증)
        valid_intervals = ["1m", "5m", "15m", "30m", "1h"]
        env = {
            "KIS_APP_KEY": "test_key",
            "KIS_APP_SECRET": "test_secret",
            "KIS_ACCOUNT_NO": "12345678",
        }

        # 유효한 interval은 ValueError가 발생하지 않아야 함
        for interval in valid_intervals:
            with patch.dict(os.environ, env):
                # _validate_interval 호출로 interval 검증
                try:
                    kis_client._validate_interval(interval)
                except ValueError:
                    pytest.fail(f"Valid interval {interval} raised ValueError")


# ---------------------------------------------------------------------------
# TestFetchKrIntradayMissingEnv
# ---------------------------------------------------------------------------


class TestFetchKrIntradayMissingEnv:
    """환경변수 누락 시 동작 테스트."""

    def test_missing_kis_app_key_raises_error(self) -> None:
        """KIS_APP_KEY 미설정 → EnvironmentError."""
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        # KIS_APP_KEY 제외하고 나머지 환경변수 설정
        env = {
            "KIS_APP_SECRET": "test_secret",
            "KIS_ACCOUNT_NO": "12345678",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(EnvironmentError):
                kis_client.fetch_kr_intraday("005930", "20240101")

    def test_missing_kis_app_secret_raises_error(self) -> None:
        """KIS_APP_SECRET 미설정 → EnvironmentError."""
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        env = {
            "KIS_APP_KEY": "test_key",
            "KIS_ACCOUNT_NO": "12345678",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(EnvironmentError):
                kis_client.fetch_kr_intraday("005930", "20240101")

    def test_missing_kis_account_no_raises_error(self) -> None:
        """KIS_ACCOUNT_NO 미설정 → EnvironmentError."""
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        env = {
            "KIS_APP_KEY": "test_key",
            "KIS_APP_SECRET": "test_secret",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(EnvironmentError):
                kis_client.fetch_kr_intraday("005930", "20240101")


# ---------------------------------------------------------------------------
# TestFetchKrIntradayResponse
# ---------------------------------------------------------------------------


class TestFetchKrIntradayResponse:
    """KIS API 응답 처리 테스트."""

    def test_mock_http_response_to_dataframe(self) -> None:
        """Mock HTTP 응답 → OHLCV DataFrame 변환."""
        try:
            from smart_stock.data import kis_client
        except ImportError:
            pytest.skip("kis_client 모듈 미구현")

        # _parse_response 함수로 KIS API 응답 변환 테스트
        mock_api_response = {
            "output1": [
                {
                    "stck_cntg_hour": "202401020930",
                    "stck_oprc": "70000",
                    "stck_prpr": "70500",
                    "stck_hgpr": "71000",
                    "stck_lwpr": "69000",
                    "cntg_vol": "100000",
                },
                {
                    "stck_cntg_hour": "202401020935",
                    "stck_oprc": "70500",
                    "stck_prpr": "70600",
                    "stck_hgpr": "71100",
                    "stck_lwpr": "69100",
                    "cntg_vol": "150000",
                },
            ]
        }

        # _parse_response가 올바르게 DataFrame으로 변환하는지 확인
        result = kis_client._parse_response(mock_api_response)

        # 결과가 DataFrame인지 확인
        assert isinstance(result, pd.DataFrame)
        # OHLCV 컬럼 확인
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        assert all(col in result.columns for col in required_cols)
        # DatetimeIndex 확인
        assert isinstance(result.index, pd.DatetimeIndex)
        # 데이터 행 수 확인
        assert len(result) == 2
