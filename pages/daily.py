import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

from libs.graph_blueprint import ReportConfig, MachineDailyReport

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATASET_DIR: Path = BASE_DIR / "dataset"
DB_PATH: Path = DATASET_DIR / "sales.db"


@st.cache_data(ttl=3600) # 1時間
def load_csv(path: Path):
    return pd.read_csv(
        path,
        encoding="utf-8-sig"  # 日本語対応
    )

@st.cache_data(ttl=3600) # 1時間
def get_sale(machine_name: str, selected_date):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # YYYY-mm-dd形式
    date_str = selected_date.strftime("%Y-%m-%d")

    query = f"""
        SELECT sale, day_operator, day_multi, night_operator, night_multi
        FROM "{machine_name}"
        WHERE date = ?
        LIMIT 1
        """

    cursor.execute(query, (date_str,))
    result = cursor.fetchone()

    conn.close()

    if result:
        sales_amount, day_operator, day_multi, night_operator, night_multi = result
        return sales_amount, day_operator, day_multi, night_operator, night_multi
    else:
        return 0, None, None, None, None


@st.cache_data(ttl=3600) # 1時間
def generate_report(df, config):
    report = MachineDailyReport(df, config)
    return report.draw()


# --- タイトル ---
st.set_page_config(page_title="日次分析", layout="wide")
st.title("📅 日次ダッシュボード")


# --- サイドバー ---
with st.sidebar.form(key="filter_form"):
    st.header("フィルタ設定")

    ## 機械名
    machine_name = st.selectbox(
        "機械名を選択",
        ["M1-1", "M1-2", "M1-3", "M1-4", "M1-6", "M1-7", "M1-8", "M2-3", "LAB_M1-1", "LAB_M1-3"]
    )

    ## 日付
    yesterday = datetime.now().date() - timedelta(days=1)

    selected_date = st.date_input(
        "日付を選択",
        value=yesterday
    )

    ## 実行ボタン
    submitted_btn = st.form_submit_button("実行")


# --- 実行後の処理 ---
if submitted_btn:
    file_name = f"{selected_date.strftime("%Y%m%d")}.csv"
    file_path = DATASET_DIR / machine_name / file_name

    if file_path.exists():
        st.success("データ読み込み成功")
        df = load_csv(file_path)
        df["日時"] = pd.to_datetime(df["日時"], format="mixed")
        mask_on = (df["ステータス"] != "電源断") & (df["ステータス"].shift() == "電源断")
        on_rows = df.loc[mask_on, "日時"]
        on_time = on_rows.iloc[0].strftime("%H:%M:%S") if not on_rows.empty else None

        mask_off = (df["ステータス"] == "電源断") & (df["ステータス"].shift() != "電源断")
        off_rows = df.loc[mask_off, "日時"]
        off_time = off_rows.iloc[-1].strftime("%H:%M:%S") if not off_rows.empty else None
        sales_amount, day_operator, day_multi, night_operator, night_multi = get_sale(machine_name, selected_date)
        config = ReportConfig(
            machine_name=f"{machine_name}",
            report_date=selected_date.strftime("%Y/%m/%d"),
            sales_amount=sales_amount,
            on_time=on_time,
            off_time=off_time,
            day_operator=day_operator,
            day_multi=day_multi,
            night_operator=night_operator,
            night_multi=night_multi,
        )
        fig = generate_report(df, config)
        st.pyplot(fig)
        st.dataframe(df)
    else:
        st.error("該当ファイルが存在しません")
        st.write(file_path)

else:
    st.html("<strong style='color: blue;'>左のサイドバーで条件を選択して、「実行」ボタンを押してください。</strong>")


