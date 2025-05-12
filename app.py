import json, pathlib, streamlit as st

# ---------- 共通設定 ----------
TICKET_FILE = pathlib.Path("tickets.json")
def load():  return json.load(TICKET_FILE.open())["count"] if TICKET_FILE.exists() else 0
def save(n): json.dump({"count": n}, TICKET_FILE.open("w"))

st.set_page_config(page_title="デジタル肩たたき券", page_icon="🎫")

# ---------- 画面状態 ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

def katatataki_time_view():
    st.markdown(
        """
        <div style="height:90vh;display:flex;justify-content:center;align-items:center;background:#ffffff;">
            <h1 style="font-size:4rem;color:#000000;">肩たたきタイム</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬅️ 戻る"):
        st.session_state.page = "home"
        st.rerun()     # ← ここを st.rerun に変更

def user_view():
    count = load()
    st.header("デジタル肩たたき券 🎫")
    st.info(f"残り枚数: **{count} 枚**")
    if count == 0:
        st.warning("もう券がありません。")
        return
    if st.button("券を 1 枚使う"):
        save(count - 1)
        st.session_state.page = "katatataki"
        st.rerun()     # ← 同上

def admin_view():
    pwd = st.text_input("管理者パスワード", type="password")
    if pwd != st.secrets.get("ADMIN_PASSWORD", "admin"):
        st.stop()

    count = load()
    st.write(f"現在の残数: **{count} 枚**")
    delta = st.number_input("増減値 (±)", value=1, step=1)
    if st.button("更新する"):
        save(max(0, count + int(delta)))
        st.rerun()     # ← 同上

# ---------- ルーター ----------
if st.session_state.page == "katatataki":
    katatataki_time_view()
else:
    mode = st.sidebar.radio("Mode", ("ユーザー", "管理者"))
    admin_view() if mode == "管理者" else user_view()
