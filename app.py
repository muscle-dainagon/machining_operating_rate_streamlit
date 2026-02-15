import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path


# ---------------------------
# ページ設定
# ---------------------------
st.set_page_config(
    page_title="M加工稼働分析ダッシュボード",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# 日本語フォント設定
# -----------------------------
def setup_japanese_font():
    base_dir = Path(__file__).resolve().parent
    font_path = base_dir / "fonts" / "ipaexg.ttf"

    if font_path.exists():
        # 🔥 フォントを明示的に登録
        fm.fontManager.addfont(str(font_path))
        font_prop = fm.FontProperties(fname=str(font_path))
        font_name = font_prop.get_name()
        plt.rcParams["font.family"] = font_name
        plt.rcParams["axes.unicode_minus"] = False
        print(f"✅ フォント読み込み成功: {font_name}")
    else:
        print("❌ フォントが見つかりません")

# 一度だけ実行
if "font_loaded" not in st.session_state:
    setup_japanese_font()
    st.session_state["font_loaded"] = True


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