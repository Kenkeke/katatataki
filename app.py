# app.py ─ Firestore 版（secrets を dict で受け取る簡易形）
import streamlit as st
import time, threading
import firebase_admin
from firebase_admin import credentials, firestore

# --- Firestore 初期化 ---
cred = credentials.Certificate(dict(st.secrets))   # ← 変更
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
DOC = db.collection("tickets").document("count")
DEFAULT = 10

def load_count():  # ...
    snap = DOC.get()
    return snap.to_dict()["count"] if snap.exists else DEFAULT

def save_count(n): DOC.set({"count": n})

# --- 管理者パスワード ---
ADMIN_PASS = "katatakimaster"
def is_admin():
    if "admin" in st.session_state: return st.session_state.admin
    if st.sidebar.text_input("管理者パス", type="password") == ADMIN_PASS:
        st.session_state.admin = True; st.rerun()
    return False

# --- UI ---
st.set_page_config("肩たたき券"); st.title("残り肩たたき券")
count = load_count()
st.markdown(f"<h1 style='font-size:5rem'>{count}</h1>", unsafe_allow_html=True)

def use(): save_count(count-1); st.session_state.show=True; st.rerun()
st.button("1枚使う", disabled=count<=0, on_click=use)

if st.session_state.get("show"):
    st.markdown("""<style>.modal{position:fixed;inset:0;background:#fff;
    display:flex;justify-content:center;align-items:center;z-index:1000}
    .txt{font-family:'Hiragino Maru Gothic ProN','YuGothic',sans-serif;
    font-size:3.5rem;color:#000;margin-bottom:2rem}</style>
    <div class="modal"><div class="txt">肩たたきタイム！</div>""",
    unsafe_allow_html=True)
    st.button("表示停止", on_click=lambda: (st.session_state.update(show=False), st.rerun()))
    st.markdown("</div>", unsafe_allow_html=True)

if is_admin():
    st.sidebar.header("管理者メニュー")
    c1,c2=st.sidebar.columns(2)
    if c1.button("+1"): save_count(count+1); st.rerun()
    if c2.button("-1", disabled=count<=0): save_count(count-1); st.rerun()
    n=st.sidebar.number_input("任意リセット", value=count, min_value=0, step=1)
    if st.sidebar.button("リセット"): save_count(int(n)); st.rerun()

# --- ポーリング ---
if "poller" not in st.session_state:
    def poll():
        while True:
            time.sleep(3)
            if load_count()!=st.session_state.get("live", count):
                st.session_state.live=load_count(); st.rerun()
    threading.Thread(target=poll,daemon=True).start()
    st.session_state.poller=True

st.write("secrets keys:", list(st.secrets.keys()))
