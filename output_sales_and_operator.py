import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter


# --- 定数 ---
DB_PATH: Path = Path(r"C:\Users\81802\Box\システム開発\H-HUB\machining_completed.db")
# DB_PATH: Path = Path(r"C:\Users\81802\Box\システム開発\H-HUB\test.db")

## 機械名
MACHINE_NAME_LIST: list = [
    "M1-1",
    "M1-2",
    "M1-3",
    "M1-4",
    "M1-6",
    "M1-7",
    "M2-3",
    "LAB_M1-1",
    "LAB_M1-3"
]

## シフト時間
TIME_RANGE_START_STATUS: dict = {
    "hour": 5,
    "mitute": 0,
    "second": 0
}

TIME_RANGE_END_STATUS: dict = {
    "hour": 23,
    "mitute": 59,
    "second": 59
}

DAY_END_STATUS: dict = {
    "hour": 17,
    "mitute": 0,
    "second": 0
}

NIGHT_START_STATUS: dict = {k: (v + 1 if k == "second" else v) for k, v in DAY_END_STATUS.items()}

## SQL
SQL_REVENUE = """
SELECT SUM(revenue_total)
FROM machining_completed
WHERE unit_name = ?
AND timestamp BETWEEN ? AND ?
"""

SQL_OPERATOR = """
SELECT operator_name
FROM machining_completed
WHERE unit_name = ?
AND timestamp BETWEEN ? AND ?
GROUP BY operator_name
ORDER BY COUNT(*) DESC
LIMIT 1
"""


def create_time(target_date: str):
    """
    指定日の加工集計時間を作成する

    5:00:00 ～ 翌日 4:59:59
    """
    time_range_start = datetime.strptime(target_date, "%Y-%m-%d").replace(
        hour=TIME_RANGE_START_STATUS["hour"], minute=TIME_RANGE_START_STATUS["mitute"], second=TIME_RANGE_START_STATUS["second"]
    )

    day_end = time_range_start.replace(hour=DAY_END_STATUS["hour"], minute=DAY_END_STATUS["mitute"], second=DAY_END_STATUS["second"])
    night_start = day_end + timedelta(seconds=1)
    time_range_end = time_range_start + timedelta(days=1) - timedelta(seconds=1)

    return time_range_start, day_end, night_start, time_range_end


def fetch_total_revenue_and_oeprator_for_machine(cur, machine_name, time_range_start, day_end, night_start, time_range_end):
    """機械から売上・担当者を取得する関数"""
    # 売上取得
    cur.execute(SQL_REVENUE, (machine_name, time_range_start, time_range_end))
    revenue = cur.fetchone()[0] or 0

    # 日勤担当者
    cur.execute(SQL_OPERATOR, (machine_name, time_range_start, day_end))
    r = cur.fetchone()
    day_operator = r[0] if r else ""

    # 夜勤担当者
    cur.execute(SQL_OPERATOR, (machine_name, night_start, time_range_end))
    r = cur.fetchone()
    night_operator = r[0] if r else ""

    return {
        "revenue": revenue,
        "day_operator": day_operator,
        "night_operator": night_operator,
    }


def apply_multi_flag(result: dict):
    """同じ担当者が複数機械にいる場合「マルチ」を付与する関数"""
    day_counts = Counter(
        v["day_operator"] for v in result.values() if v["day_operator"]
    )

    night_counts = Counter(
        v["night_operator"] for v in result.values() if v["night_operator"]
    )

    for v in result.values():
        v["day_multi"] = "マルチ" if day_counts[v["day_operator"]] > 1 else ""
        v["night_multi"] = "マルチ" if night_counts[v["night_operator"]] > 1 else ""


def main():
    target_date = "2026-03-15"
    time_range_start, day_end, night_start, time_range_end = create_time(target_date)

    result = {}
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for machine_name in MACHINE_NAME_LIST:
            result[machine_name] = fetch_total_revenue_and_oeprator_for_machine(
                cur,
                machine_name,
                time_range_start,
                day_end,
                night_start,
                time_range_end,
            )

    # マルチ判定
    apply_multi_flag(result)

    # 出力
    for unit, v in result.items():
        print(
            f"{unit} -> "
            f"売上: {v['revenue']}、"
            f"日勤: {v['day_operator']} {v['day_multi']}、"
            f"夜勤: {v['night_operator']} {v['night_multi']}"
        )


if __name__ == "__main__":
    main()