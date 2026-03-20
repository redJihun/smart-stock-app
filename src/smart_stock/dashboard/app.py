"""Smart Stock 웹 대시보드."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from smart_stock.dashboard.data import (
    compute_metrics,
    compute_strategy_summary,
    load_outcomes,
    load_signals,
)

_LOG_DIR = Path("data/tracking")


def _fmt_pct(value: float | None) -> str:
    """float | None → 퍼센트 문자열 포맷."""
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def _fmt_ret(value: float | None) -> str:
    """float | None → 수익률 문자열 포맷."""
    if value is None:
        return "—"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def main() -> None:
    """대시보드 메인 함수."""
    st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")
    st.title("Smart Stock Dashboard")

    # 새로고침 버튼
    col_btn, col_path = st.columns([1, 4])
    with col_btn:
        st.button("새로고침")
    with col_path:
        st.caption(f"데이터 경로: {_LOG_DIR.resolve()}")

    st.divider()

    # 데이터 로드
    signals_df = load_signals(_LOG_DIR)
    outcomes_df = load_outcomes(_LOG_DIR)
    metrics = compute_metrics(outcomes_df)

    # ── 요약 지표 4열 ──────────────────────────────────
    st.subheader("요약")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 시그널 수", metrics.total_signals)
    c2.metric("1일 적중률", _fmt_pct(metrics.win_rate_1d))
    c3.metric("1일 평균 수익률", _fmt_ret(metrics.avg_return_1d))
    c4.metric("1주 평균 수익률", _fmt_ret(metrics.avg_return_1w))

    st.divider()

    # ── 시그널 이력 ────────────────────────────────────
    st.subheader("최근 시그널")
    if signals_df.empty:
        st.info("기록된 시그널이 없습니다. PaperTrader를 실행하여 데이터를 축적하세요.")
    else:
        display_df = signals_df.tail(20).iloc[::-1].copy()
        signal_map = {1: "매수", -1: "매도", 0: "홀드"}
        display_df["signal"] = display_df["signal"].map(signal_map)
        st.dataframe(
            display_df,
            column_config={
                "strategy_name": st.column_config.TextColumn("전략"),
                "ticker": st.column_config.TextColumn("종목"),
                "signal_date": st.column_config.DatetimeColumn("시그널 시각"),
                "signal": st.column_config.TextColumn("시그널"),
                "price": st.column_config.NumberColumn("가격", format="₩%.0f"),
                "logged_at": st.column_config.DatetimeColumn("기록 시각"),
            },
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── 전략별 성과 ────────────────────────────────────
    st.subheader("전략별 성과")
    if outcomes_df.empty:
        st.info("결과 데이터가 없습니다. OutcomeTracker.update()를 실행하세요.")
    else:
        summary_df = compute_strategy_summary(outcomes_df)
        if summary_df.empty:
            st.info("집계할 데이터가 없습니다.")
        else:
            st.dataframe(
                summary_df,
                column_config={
                    "strategy_name": st.column_config.TextColumn("전략"),
                    "signal_count": st.column_config.NumberColumn("시그널 수"),
                    "win_rate_1d": st.column_config.NumberColumn(
                        "1일 적중률", format="%.1f%%"
                    ),
                    "avg_return_1d": st.column_config.NumberColumn(
                        "1일 평균 수익률", format="%.2f%%"
                    ),
                },
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
