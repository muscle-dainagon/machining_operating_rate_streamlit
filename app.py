# import streamlit as st


# # --- 設定 ---
# st.set_page_config(page_title="M加工稼働分析ダッシュボード", layout="wide")

# # --- 内容 ---
# st.title("📊M加工稼働分析ダッシュボード")

# st.markdown("### 左のメニューからページを選択してください。")

# st.subheader("daily")
# st.text("日時の号機ごとの稼働率を見る")
# st.subheader("analysis")
# st.text("範囲を指定して稼働率を見る")


import streamlit as st

# ---------------------------
# ページ設定
# ---------------------------
st.set_page_config(
    page_title="M加工稼働分析ダッシュボード",
    page_icon="📊",
    layout="wide"
)

# ---------------------------
# ヘッダー
# ---------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>
        📊 M加工稼働分析ダッシュボード
    </h1>
    <hr style='margin-top:10px; margin-bottom:40px;'>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h3 style='text-align: center;'>左のサイドバーからページを選択してください</h3>",
    unsafe_allow_html=True
)

st.write("")
st.write("")

# ---------------------------
# ページ説明カード
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="
            background-color:#f5f7fa;
            padding:25px;
            border-radius:15px;
            box-shadow:2px 2px 15px rgba(0,0,0,0.05);
        ">
            <h3>📅 daily</h3>
            <p style="font-size:16px;">
                日付と号機を指定し、<br>
                1日の稼働率・売上・遊休率を可視化します。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="
            background-color:#f5f7fa;
            padding:25px;
            border-radius:15px;
            box-shadow:2px 2px 15px rgba(0,0,0,0.05);
        ">
            <h3>📈 analysis</h3>
            <p style="font-size:16px;">
                期間を指定し、<br>
                月次・範囲分析を行います。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )