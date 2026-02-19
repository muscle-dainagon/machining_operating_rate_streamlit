import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from dataclasses import dataclass


@dataclass
class ReportConfig:
    machine_name: str
    report_date: str
    sales_amount: int
    on_time: str
    off_time: str
    start_hour: int = 5
    base_work_hours: float = 16.5
    color_map: dict = None


    def __post_init__(self):
        if self.color_map is None:
            self.color_map = {
                "電源断": "gray",
                "アラーム": "red",
                "段取り": "yellow",
                "自動停止": "green",
                "自動起動": "#1E90FF",
            }


class MachineDailyReport:
    def __init__(self, df: pd.DataFrame, config: ReportConfig):
        # slice対策（超重要）
        self.df = df.copy()
        self.config = config

        self._setup_font()
        self._prepare_dataframe()
        self._aggregate()

    # --- フォント設定 ---
    def _setup_font(self):
        font_candidates = [
            "Yu Gothic", "Meiryo", "MS Gothic",
            "Hiragino Sans", "IPAexGothic", "sans-serif",
        ]

        font_name = "sans-serif"
        for font in font_candidates:
            if font in [f.name for f in fm.fontManager.ttflist]:
                font_name = font
                break

        plt.rcParams["font.family"] = font_name
        plt.rcParams["axes.unicode_minus"] = False

    # --- DataFrame前処理 ---
    def _prepare_dataframe(self):
        self.df["duration_h"] = self.df["経過秒数"] / 3600
        self.df["start_h"] = (
            self.df["duration_h"].cumsum().shift(1).fillna(0)
        )

        self.df["Color"] = self.df["ステータス"].map(
            lambda x: self.config.color_map.get(x, "purple")
        )

    # --- 集計処理 ---
    def _aggregate(self):
        # ステータス別合計（秒）
        self.summary = (
            self.df.groupby("ステータス")["経過秒数"].sum()
        )

        # --- 電源断以外の合計時間（h） ---
        self.real_work_time = sum(
            self.summary.get(status, 0)
            for status in self.summary.index
            if status != "電源断"
        ) / 3600

        self.power_on_time = self.real_work_time

        # --- 基準稼働時間（h） ---
        BASE_WORK_HOURS = self.config.base_work_hours

        # --- 遊休時間 ---
        self.idle_time = BASE_WORK_HOURS - self.real_work_time

        # マイナス防止（安全策）
        # if self.idle_time < 0:
        #     self.idle_time = 0

        # --- 遊休率 ---
        self.idle_rate = (
            self.idle_time / BASE_WORK_HOURS * 100
            if BASE_WORK_HOURS > 0 else 0
        )

        # --- 単価 ---
        self.unit_price = (
            self.config.sales_amount / self.real_work_time
            if self.real_work_time > 0 else 0
        )

    # --- ユーティリティ ---
    def _get_hours(self, status: str) -> float:
        return self.summary.get(status, 0) / 3600

    # --- 描画メソッド ---
    def draw(self):
        # ================================
        # ★ 稼働ゼロチェック（最重要）
        # ================================
        if self.real_work_time <= 0:
            fig = plt.figure(figsize=(10, 4))
            plt.text(
                0.5,
                0.5,
                "機械が稼働していません。",
                ha="center",
                va="center",
                fontsize=24,
                color="red",
            )
            plt.axis("off")
            return fig

        # ===== 通常描画 =====
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(
            f"{self.config.machine_name}　{self.config.report_date}",
            fontsize=26,
            fontweight="bold",
            y=0.98,
        )

        gs = fig.add_gridspec(2, 2, height_ratios=[0.4, 2.0])

        self._draw_gantt(fig, gs)
        self._draw_pie(gs)
        self._draw_table_and_text(gs)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        # plt.show()
        return fig

    # --- ガントチャート ---
    def _draw_gantt(self, fig, gs):
        ax = fig.add_subplot(gs[0, :])

        # --- ガント本体 ---
        for _, row in self.df.iterrows():
            ax.barh(
                y=0,
                left=row["start_h"],
                width=row["duration_h"],
                color=row["Color"],
                height=0.6,
            )

        # --- X軸設定 ---
        ax.set_xlim(0, 24)
        ticks = np.arange(0, 25, 2)
        labels = [
            f"{(self.config.start_hour + t) % 24:02d}:00"
            for t in ticks
        ]

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)
        ax.set_yticks([])
        ax.set_title("24時間稼働状況")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # =================================================
        # ★ 追加：8:30 の縦ライン（オレンジ）
        # =================================================
        target_hour = 8.5  # 8:30
        x_pos = (target_hour - self.config.start_hour) % 24

        ax.axvline(
            x=x_pos,
            color="orange",
            linewidth=3,
            linestyle="-",
            alpha=0.9,
            label="8:30",
            zorder=5,
        )

        # --- 凡例 ---
        handles = [
            plt.Rectangle((0, 0), 1, 1, fc=c)
            for c in self.config.color_map.values()
        ]
        labels = list(self.config.color_map.keys())

        # 8:30ライン用の凡例を追加
        handles.append(
            plt.Line2D([0], [0], color="orange", linewidth=3)
        )
        labels.append("8:30")

        ax.legend(
            handles,
            labels,
            title="ステータス",
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
        )

    # --- 円グラフ ---
    def _draw_pie(self, gs):
        ax = plt.subplot(gs[1, 0])

        labels = ["自動起動", "自動停止", "段取り", "アラーム"]
        values = [self._get_hours(l) for l in labels]
        colors = [self.config.color_map[l] for l in labels]

        ax.pie(
            values,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
            radius=1.25,
        )
        ax.set_title("割合グラフ")
        ax.legend(labels, loc="upper right")

    # --- テーブル + KPI ---
    def _draw_table_and_text(self, gs):
        sub = gs[1, 1].subgridspec(2, 1, height_ratios=[1.1, 0.9])

        # --- テーブル ---
        ax_t = plt.subplot(sub[0])
        ax_t.axis("off")

        rows = []
        for s in ["自動起動", "自動停止", "段取り", "アラーム", "電源断"]:
            h = self._get_hours(s)
            rows.append([
                s,
                f"{h:.1f}",
                f"{(h / 24) * 100:.2f}",
                "-" if s == "電源断" else f"{(h / self.power_on_time) * 100:.2f}",
            ])

        table = ax_t.table(
            cellText=rows,
            colLabels=["", "時間(h)", "全体%", "電源投入%"],
            loc="center",
            cellLoc="center",
        )
        table.scale(1.1, 2.2)
        table.set_fontsize(13)

        # ================================
        # ★ colLabels を太字にする
        # ================================
        for col in range(4):
            table.get_celld()[(0, col)].get_text().set_weight("bold")

        # --- KPI ---
        ax_k = plt.subplot(sub[1])
        ax_k.axis("off")

        # 左右の配置基準位置
        LEFT_X = 0.25
        RIGHT_X = 0.70

        # --- 【左側】売上・単価 (変数の値を表示) ---
        ax_k.text(
            LEFT_X - 0.02, 0.6, "売上：", ha="right", va="center", fontsize=30, color="black"
        )
        ax_k.text(
            LEFT_X - 0.02,
            0.6,
            f"￥{self.config.sales_amount:,}",
            ha="left",
            va="center",
            fontsize=30,
            color="red",
        )

        ax_k.text(
            LEFT_X - 0.02, 0.4, "￥/h：", ha="right", va="center", fontsize=30, color="black"
        )
        ax_k.text(
            LEFT_X - 0.02,
            0.4,
            f"￥{int(self.unit_price):,}",
            ha="left",
            va="center",
            fontsize=30,
            color="red",
        )

        # --- 【右側】時間・率 (CSV集計値を表示) ---
        ax_k.text(
            RIGHT_X + 0.1,
            0.8,
            f"実労働時間(16.5h)",
            ha="center",
            va="center",
            fontsize=20,
            color="black",
        )

        ax_k.text(
            RIGHT_X + 0.2,
            0.6,
            "遊休時間：",
            ha="right",
            va="center",
            fontsize=30,
            color="black",
        )
        ax_k.text(
            RIGHT_X + 0.2,
            0.6,
            f"{self.idle_time:.2f} h",
            ha="left",
            va="center",
            fontsize=30,
            color="red",
        )

        ax_k.text(
            RIGHT_X + 0.2, 0.4, "遊休％：", ha="right", va="center", fontsize=30, color="black"
        )
        ax_k.text(
            RIGHT_X + 0.2,
            0.4,
            f"{self.idle_rate:.1f} %",
            ha="left",
            va="center",
            fontsize=30,
            color="red",
        )

        ax_k.text(
            RIGHT_X - 0.2,
            1.1,
            "電源オン：",
            ha="right",
            va="center",
            fontsize=22,
            color="black",
        )
        ax_k.text(
            RIGHT_X - 0.2,
            1.1,
            f"{self.config.on_time}",
            ha="left",
            va="center",
            fontsize=22,
            color="blue",
        )

        ax_k.text(
            RIGHT_X -0.2,
            0.95,
            "電源オフ：",
            ha="right",
            va="center",
            fontsize=22,
            color="black",
        )
        ax_k.text(
            RIGHT_X - 0.2,
            0.95,
            f"{self.config.off_time}",
            ha="left",
            va="center",
            fontsize=22,
            color="blue",
        )