from datetime import datetime, timedelta


def get_daily_date_range():
    # 昨日の日付を取得し、日付範囲として返す
    yesterday = datetime.now().date() - timedelta(days=1)
    return yesterday, yesterday


def get_weekly_date_range():
    # 今日の日付を取得
    today = datetime.now().date()
    # 最後の日曜日を取得（今日が月曜日なら1日前、火曜日なら2日前...）
    last_sunday = today - timedelta(days=today.weekday() + 1)
    # 最後の日曜日の6日前が最後の月曜日
    last_monday = last_sunday - timedelta(days=6)
    return last_monday, last_sunday


def get_monthly_date_range():
    # 今日の日付を取得
    today = datetime.now().date()
    # 今月の1日を取得
    first_of_this_month = today.replace(day=1)
    # 先月の最終日を取得（今月の1日から1日引く）
    last_of_last_month = first_of_this_month - timedelta(days=1)
    # 先月の1日を取得
    first_of_last_month = last_of_last_month.replace(day=1)
    return first_of_last_month, last_of_last_month