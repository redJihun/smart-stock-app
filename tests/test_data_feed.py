"""실시간 데이터 피드 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from smart_stock.data.feed import PollingDataFeed


def _make_sample_df(
    start: str = "2024-01-02 09:30",
    periods: int = 3,
) -> pd.DataFrame:
    """Open/High/Low/Close/Volume 컬럼을 가진 샘플 DataFrame."""
    idx = pd.date_range(start, periods=periods, freq="5min")
    return pd.DataFrame(
        {
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.5,
            "Volume": 10000,
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# TestPollingDataFeedInit
# ---------------------------------------------------------------------------


class TestPollingDataFeedInit:
    """PollingDataFeed 초기화 테스트."""

    def test_default_poll_interval(self) -> None:
        """poll_interval 기본값 60.0 확인."""
        feed = PollingDataFeed(ticker="005930")
        assert feed._poll_interval == 60.0

    def test_custom_fetcher_stored(self) -> None:
        """mock fetcher 주입 후 _fetcher 속성 확인."""
        mock_fetcher = MagicMock()
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)
        assert feed._fetcher is mock_fetcher

    def test_invalid_poll_interval_raises(self) -> None:
        """poll_interval <= 0 → ValueError."""
        with pytest.raises(ValueError, match="poll_interval은 0보다 커야 합니다"):
            PollingDataFeed(ticker="005930", poll_interval=0)
        with pytest.raises(ValueError, match="poll_interval은 0보다 커야 합니다"):
            PollingDataFeed(ticker="005930", poll_interval=-1.0)


# ---------------------------------------------------------------------------
# TestPollingDataFeedSubscribe
# ---------------------------------------------------------------------------


class TestPollingDataFeedSubscribe:
    """구독 콜백 등록 테스트."""

    def test_subscribe_appends_callback(self) -> None:
        """subscribe() 후 _callbacks 길이 확인."""
        feed = PollingDataFeed(ticker="005930")
        cb = MagicMock()
        feed.subscribe(cb)
        assert len(feed._callbacks) == 1
        assert feed._callbacks[0] is cb

    def test_multiple_callbacks_all_called(self) -> None:
        """콜백 2개 등록 → _fetch_and_notify() 후 둘 다 호출 확인."""
        df = _make_sample_df()
        mock_fetcher = MagicMock(return_value=df)
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb1 = MagicMock()
        cb2 = MagicMock()
        feed.subscribe(cb1)
        feed.subscribe(cb2)

        feed._fetch_and_notify()

        cb1.assert_called_once()
        cb2.assert_called_once()


# ---------------------------------------------------------------------------
# TestPollingDataFeedNewDataDetection
# ---------------------------------------------------------------------------


class TestPollingDataFeedNewDataDetection:
    """신규 데이터 감지 및 필터링 테스트."""

    def test_first_fetch_delivers_all_rows(self) -> None:
        """_last_ts=None → 전체 df 전달."""
        df = _make_sample_df()
        mock_fetcher = MagicMock(return_value=df)
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb = MagicMock()
        feed.subscribe(cb)
        feed._fetch_and_notify()

        cb.assert_called_once()
        delivered_df = cb.call_args[0][0]
        assert len(delivered_df) == 3
        assert delivered_df.index.equals(df.index)

    def test_no_new_rows_skips_callback(self) -> None:
        """동일 timestamp 재조회 → 콜백 미호출."""
        df = _make_sample_df()
        mock_fetcher = MagicMock(return_value=df)
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb = MagicMock()
        feed.subscribe(cb)

        # 첫 호출
        feed._fetch_and_notify()
        assert cb.call_count == 1

        # 동일 데이터 재조회
        feed._fetch_and_notify()
        assert cb.call_count == 1  # 콜백 불호출

    def test_only_new_rows_delivered(self) -> None:
        """새 캔들만 슬라이스해서 전달."""
        df_old = _make_sample_df(periods=2)
        df_new = _make_sample_df(periods=3)

        mock_fetcher = MagicMock()
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb = MagicMock()
        feed.subscribe(cb)

        # 첫 호출: 오래된 데이터 2개
        mock_fetcher.return_value = df_old
        feed._fetch_and_notify()
        assert cb.call_count == 1
        delivered_1 = cb.call_args[0][0]
        assert len(delivered_1) == 2

        # 두 번째 호출: 새로운 데이터 3개 (2개는 겹침, 1개 신규)
        mock_fetcher.return_value = df_new
        feed._fetch_and_notify()
        assert cb.call_count == 2
        delivered_2 = cb.call_args[0][0]
        assert len(delivered_2) == 1  # 신규 1개만 전달


# ---------------------------------------------------------------------------
# TestPollingDataFeedFetchError
# ---------------------------------------------------------------------------


class TestPollingDataFeedFetchError:
    """fetch 에러 처리 테스트."""

    def test_exception_does_not_crash(self) -> None:
        """fetcher에서 RuntimeError → _fetch_and_notify 정상 반환."""
        mock_fetcher = MagicMock(side_effect=RuntimeError("API 에러"))
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb = MagicMock()
        feed.subscribe(cb)

        # 예외가 발생해도 프로그램 크래시 없음
        feed._fetch_and_notify()

        # 콜백 미호출
        cb.assert_not_called()

    def test_empty_dataframe_skips_callback(self) -> None:
        """빈 DataFrame → 콜백 미호출."""
        empty_df = pd.DataFrame()
        mock_fetcher = MagicMock(return_value=empty_df)
        feed = PollingDataFeed(ticker="005930", fetcher=mock_fetcher)

        cb = MagicMock()
        feed.subscribe(cb)

        feed._fetch_and_notify()

        cb.assert_not_called()


# ---------------------------------------------------------------------------
# TestPollingDataFeedLifecycle
# ---------------------------------------------------------------------------


class TestPollingDataFeedLifecycle:
    """피드 생명주기 관리 테스트."""

    def test_start_stop_no_error(self) -> None:
        """start() + stop() 예외 없이 완료."""
        feed = PollingDataFeed(ticker="005930", poll_interval=0.01)
        feed.start()
        assert feed._thread is not None
        assert feed._thread.is_alive()

        feed.stop()
        assert feed._thread is None

    def test_context_manager_auto_stop(self) -> None:
        """with 블록 탈출 시 stop() 자동 호출 확인."""
        feed = PollingDataFeed(ticker="005930", poll_interval=0.01)
        with feed:
            assert feed._thread is not None
            assert feed._thread.is_alive()

        # with 블록 탈출 후 중지됨
        assert feed._thread is None
