import streamlit as st
import pandas as pd
import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import timedelta

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(page_title="期間分析", layout="wide")
st.title("📈 期間分析ダッシュボード")

# -----------------------------
# サイドバー
# -----------------------------
machines = ["M1-1", "M1-2", "M1-3", "M1-4", "M1-6", "M1-7", "M1-8", "M2-3", "LAB_M1-1", "LAB_M1-3"]

with st.sidebar:

    st.header("分析条件")

    selected_machines = st.multiselect(
        "機械名選択",
        machines,
        # default=machines
    )

    date_range = st.date_input(
        "日付範囲",
        value=(
            pd.Timestamp.today() - timedelta(days=7),
            pd.Timestamp.today() - timedelta(days=1)
        )
    )

    submitted = st.button("実行")

# -----------------------------
# CSV読み込み
# -----------------------------
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)


def load_multiple_csv(selected_machines, start_date, end_date):

    all_df = []
    date_list = pd.date_range(start_date, end_date)

    for machine in selected_machines:
        for date in date_list:

            filename = date.strftime("%Y%m%d") + ".csv"
            path = os.path.join("dataset", machine, filename)

            if os.path.exists(path):
                df = load_csv(path)
                all_df.append(df)

    if all_df:
        return pd.concat(all_df, ignore_index=True)
    else:
        return pd.DataFrame()

# -----------------------------
# 売上合算取得
# -----------------------------
def get_total_sales(selected_machines, start_date, end_date):

    conn = sqlite3.connect("dataset/sales.db")
    cursor = conn.cursor()

    total_sales = 0
    date_list = pd.date_range(start_date, end_date)

    for machine in selected_machines:
        for date in date_list:

            formatted = date.strftime("%Y-%m-%d")

            try:
                cursor.execute(
                    f"SELECT sale FROM '{machine}' WHERE date = ?",
                    (formatted,)
                )
                result = cursor.fetchone()

                if result:
                    total_sales += result[0]

            except:
                pass

    conn.close()
    return total_sales

# -----------------------------
# 円グラフ描画（指定仕様）
# -----------------------------
def draw_pie_chart(df):

    status_order = [
        "自動起動",
        "自動停止",
        "段取り",
        "アラーム",
        "電源断"
    ]

    color_map = {
        "電源断": "gray",
        "アラーム": "red",
        "段取り": "yellow",
        "自動停止": "green",
        "自動起動": "#1E90FF",
    }

    summary = df.groupby("ステータス")["経過秒数"].sum()

    summary = summary.reindex(status_order, fill_value=0)

    hours = summary / 3600

    fig, ax = plt.subplots(figsize=(4.5, 4.5))

    ax.pie(
        hours,
        labels=hours.index,
        colors=[color_map[s] for s in hours.index],
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False
    )

    ax.set_title("ステータス内訳（時間比率）", fontsize=12)

    plt.tight_layout()

    return fig, summary

# -----------------------------
# 実行処理
# -----------------------------
if submitted:

    if not selected_machines:
        st.warning("機械を選択してください")
        st.stop()

    if len(date_range) != 2:
        st.warning("日付範囲を指定してください")
        st.stop()

    start_date, end_date = date_range

    if start_date > end_date:
        st.warning("日付範囲が不正です")
        st.stop()

    # CSV読込
    df = load_multiple_csv(selected_machines, start_date, end_date)

    if df.empty:
        st.warning("該当データがありません")
        st.stop()

    # 売上合算取得
    total_sales = get_total_sales(
        selected_machines,
        start_date,
        end_date
    )

    # KPI計算
    summary_all = df.groupby("ステータス")["経過秒数"].sum()
    real_work_time = summary_all.sum() / 3600

    unit_price = (
        total_sales / real_work_time
        if real_work_time > 0 else 0
    )

    # -------------------------
    # 選択条件表示
    # -------------------------
    st.markdown("### 🔎 分析条件")

    machine_text = ", ".join(selected_machines)

    st.info(
        f"""
        **対象機械：** {machine_text}
        **期間：** {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}
        """
    )

    st.divider()

    # -------------------------
    # 横並びレイアウト
    # -------------------------
    col_left, col_right = st.columns([1, 1])

    # 左：円グラフ
    with col_left:
        fig, summary = draw_pie_chart(df)
        st.pyplot(fig)

    # 右：KPI
    with col_right:
        st.subheader("📊 集計結果")
        st.divider()

        st.metric("売上合計", f"{total_sales:,} 円")
        st.metric("総稼働時間", f"{real_work_time:.2f} h")
        st.metric("時間単価", f"{unit_price:,.0f} 円/h")

    st.divider()

    # -------------------------
    # ステータス別時間表示
    # -------------------------
    st.subheader("ステータス別合計時間（時間）")

    summary_hours = (
        summary.reindex(
            ["自動起動", "自動停止", "段取り", "アラーム", "電源断"],
            fill_value=0
        ) / 3600
    ).round(2)

    st.dataframe(
        summary_hours.rename("時間(h)").reset_index(),
        use_container_width=True
    )


else:
    st.html("<strong style='color: blue;'>左のサイドバーで条件を選択して、「実行」ボタンを押してください。</strong>")