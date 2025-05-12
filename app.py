import streamlit as st, time, firebase_admin, json, threading
from firebase_admin import credentials, firestore

# ---------- Firestore 初期化 ----------
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets)  # secrets.toml から読み取り
    firebase_admin.initialize_app(cred)
db = firestore.client()
DOC = db.collection("tickets").document("count")   # 1 ドキュメント運用
DEFAULT = 10

# ---------- Firestore 読み書き ----------
def load_count() -> int:
    snap = DOC.get()
    return snap.to_dict()["count"] if snap.exists else DEFAULT

def save_count(n: int) -> None:
    DOC.set({"count": n})

# ---------- 管理者判定（超シンプル版） ----------
ADMIN_PASS = "katatakimaster"        # ★お好みで変更／環境変数化
def is_admin() -> bool:
    if "admin" in st.session_state:           # 既にログイン済み
        return st.session_state.admin
    pw = st.sidebar.text_input("管理者パスワード", type="password")
    if pw == ADMIN_PASS:
        st.session_state.admin = True
        st.experimental_rerun()
    return False

# ---------- UI ----------
st.set_page_config(page_title="肩たたき券", layout="centered")
st.title("残り肩たたき券")

# Firestore から取得（毎回最新値）
count = load_count()
st.markdown(f"<h1 style='font-size:5rem'>{count}</h1>", unsafe_allow_html=True)

# --- ユーザー用ボタン ---
if st.button("1枚使う", disabled=count <= 0):
    save_count(count - 1)
    st.session_state.show = True
    st.experimental_rerun()

# --- 肩たたきタイム モーダル ---
if st.session_state.get("show"):
    st.markdown("""
        <div style='position:fixed;inset:0;display:flex;
        justify-content:center;align-items:center;background:#fff;z-index:1000'>
          <h2 style='font-size:4rem'>肩たたきタイム!</h2>
        </div>""", unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.show = False
    st.experimental_rerun()

# --- 管理者 UI (⑤) ---
if is_admin():
    st.sidebar.header("管理者メニュー")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("+1"):
        save_count(count + 1); st.experimental_rerun()
    if col2.button("-1") and count > 0:
        save_count(count - 1); st.experimental_rerun()

    new_val = st.sidebar.number_input("任意の枚数にセット", min_value=0, value=count, step=1)
    if st.sidebar.button("リセット"):
        save_count(int(new_val)); st.experimental_rerun()

# --- 自動再読み込み (⑥) ---
if "auto_update" not in st.session_state:
    def poll():
        while True:
            time.sleep(3)                # 3 秒ごとに監視
            latest = load_count()
            if latest != st.session_state.get("live"):
                st.session_state.live = latest
                st.experimental_rerun()
    st.session_state.live = count
    threading.Thread(target=poll, daemon=True).start()
