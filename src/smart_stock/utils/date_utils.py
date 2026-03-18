from datetime import date, datetime

DateLike = str | date | datetime


def to_date(value: DateLike) -> date:
    """str("YYYY-MM-DD" 또는 "YYYYMMDD"), date, datetime → date 변환."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    value = value.strip()
    if len(value) == 8 and value.isdigit():
        return datetime.strptime(value, "%Y%m%d").date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def to_date_str(value: DateLike, fmt: str = "%Y-%m-%d") -> str:
    """DateLike → 포맷된 문자열 변환. fdr/yfinance 인자 전달용."""
    return to_date(value).strftime(fmt)


def date_range_str(start: DateLike, end: DateLike) -> tuple[str, str]:
    """start, end를 둘 다 '%Y-%m-%d' 문자열로 반환. loader 편의 함수."""
    return to_date_str(start), to_date_str(end)


def default_end_date() -> date:
    """오늘 날짜 반환 (end 파라미터 기본값용)."""
    return date.today()


def default_start_date(years_back: int = 1) -> date:
    """n년 전 날짜 반환 (start 파라미터 기본값용)."""
    today = date.today()
    try:
        return today.replace(year=today.year - years_back)
    except ValueError:
        # 윤년 2월 29일 처리
        return today.replace(year=today.year - years_back, day=28)


def years_ago(n: int) -> date:
    """default_start_date의 별칭."""
    return default_start_date(years_back=n)
