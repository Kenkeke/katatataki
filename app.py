# app.py ─ デジタル肩たたき券（Firestore 版・完全動作）
# --------------------------------------------------------
# ・Firestore 1 ドキュメントで残数共有
# ・モーダルは「表示停止」ボタンで閉じるまで表示
# ・管理者パスワードで +1 / -1 / 任意リセット
# ・3 秒ポーリングで多端末リアルタイム同期
# --------------------------------------------------------

import streamlit as st
import json, time, threading
import firebase_admin
from firebase_admin import credentials, firestore

# ---------- Firestore 初期化 ----------
service_account_info = json.loads(st.secrets["service_account"])  # secrets.toml から JSON 文字列
cred = credentials.Certificate(service_account_info)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
DOC = db.collection("tickets").document("count")   # 単一ドキュメント
DEFAULT_COUNT = 10

def load_count() -> int:
    snap = DOC.get()
    return snap.to_dict()["count"] if snap.exists else DEFAULT_COUNT

def save_count(n: int) -> None:
    DOC.set({"count": n})

# ---------- 管理者認証 ----------
ADMIN_PASS = "katatakimaster"        # ★任意に変更
def is_admin() -> bool:
    if "admin" in st.session_state:
        return st.session_state.admin
    pw = st.sidebar.text_input("管理者パスワード", type="password")
    if pw == ADMIN_PASS:
        st.session_state.admin = True
        st.rerun()
    return False

# ---------- ページ設定 ----------
st.set_page_config(page_title="デジタル肩たたき券", layout="centered")
st.title("残り肩たたき券")

count = load_count()
st.markdown(f"<h1 style='font-size:5rem'>{count}</h1>", unsafe_allow_html=True)

# ---------- ユーザーボタン ----------
def use_ticket():
    current = load_count()
    if current > 0:
        save_count(current - 1)
        st.session_state.show_modal = True
        st.rerun()

st.button("1枚使う", disabled=count <= 0, on_click=use_ticket)

# ---------- モーダル ----------
def close_modal():
    st.session_state.show_modal = False
    st.rerun()

if st.session_state.get("show_modal"):
    st.markdown(
        """
        <style>
        .modal-overlay{
          position:fixed;inset:0;background:#fff;
          display:flex;flex-direction:column;
          justify-content:center;align-items:center;
          z-index:1000;
        }
        .modal-text{
          font-family:"Hiragino Maru Gothic ProN","YuGothic","Yu Gothic",sans-serif;
          font-size:3.5rem;color:#000;margin-bottom:2rem;
        }
        </style>
        <div class="modal-overlay">
          <div class="modal-text">肩たたきタイム！</div>
        """,
        unsafe_allow_html=True,
    )
    st.button("表示停止", on_click=close_modal)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 管理者 UI ----------
if is_admin():
    st.sidebar.header("管理者メニュー")
    c1, c2 = st.sidebar.columns(2)
    if c1.button("+1"):
        save_count(count + 1); st.rerun()
    if c2.button("-1", disabled=count <= 0):
        save_count(count - 1); st.rerun()
    new_val = st.sidebar.number_input("任意の枚数にセット", value=count, min_value=0, step=1)
    if st.sidebar.button("リセット"):
        save_count(int(new_val)); st.rerun()

# ---------- ポーリングで同期 ----------
if "live_count" not in st.session_state:
    st.session_state.live_count = count

if "poller_started" not in st.session_state:
    def poll():
        while True:
            time.sleep(3)
            latest = load_count()
            if latest != st.session_state.live_count:
                st.session_state.live_count = latest
                st.rerun()
    threading.Thread(target=poll, daemon=True).start()
    st.session_state.poller_started = True
