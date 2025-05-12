# app.py － デジタル肩たたき券（ローカル JSON 版）
# -----------------------------------------------
# ・残数を JSON ファイルに保存
# ・「1枚使う」で残数 -1 ＆ モーダルを開く
# ・モーダルは「表示停止」ボタンを押すまで表示
# ・フォントは丸ゴシック寄り、文字色は黒、背景は白
# -----------------------------------------------

import streamlit as st
import json
import pathlib

# ---------- 設定 ----------
FILE = pathlib.Path("count.json")   # 残数保存ファイル
DEFAULT_COUNT = 10                 # 初期枚数

# ---------- 残数の永続化 ----------
if not FILE.exists():
    FILE.write_text(json.dumps({"count": DEFAULT_COUNT}, ensure_ascii=False))


def load_count() -> int:
    """現在の枚数を読み込む"""
    return json.loads(FILE.read_text())["count"]


def save_count(n: int) -> None:
    """枚数を保存する"""
    FILE.write_text(json.dumps({"count": n}, ensure_ascii=False))


# ---------- Streamlit ページ設定 ----------
st.set_page_config(page_title="デジタル肩たたき券", layout="centered")
st.title("残り肩たたき券")

count = load_count()
st.markdown(f"<h1 style='font-size:5rem'>{count}</h1>", unsafe_allow_html=True)

# ---------- ボタン：1 枚消費 ----------
def use_ticket():
    current = load_count()
    if current > 0:
        save_count(current - 1)
        st.session_state["show_modal"] = True      # モーダルを開く
        st.rerun()                                 # 画面を再描画


st.button("1枚使う", disabled=count <= 0, on_click=use_ticket)

# ---------- モーダルの表示 ----------
def close_modal():
    st.session_state["show_modal"] = False        # モーダルを閉じる
    st.rerun()


if st.session_state.get("show_modal"):
    st.markdown(
        """
        <style>
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-text {
            font-family: "Hiragino Maru Gothic ProN", "YuGothic",
                         "Yu Gothic", "sans-serif";
            font-size: 3.5rem;
            color: #000000;
            margin-bottom: 2rem;
        }
        </style>
        <div class="modal-overlay">
            <div class="modal-text">肩たたきタイム！</div>
        """,
        unsafe_allow_html=True,
    )

    # モーダル内の「表示停止」ボタン
    st.button("表示停止", on_click=close_modal)
    st.markdown("</div>", unsafe_allow_html=True)

