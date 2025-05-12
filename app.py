import json
import pathlib
import streamlit as st

TICKET_FILE = pathlib.Path("tickets.json")
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin")  # Streamlit Cloud の Secrets にセット推奨
st.set_page_config(page_title="デジタル肩たたき券", page_icon="🎫", layout="centered")


def load_count() -> int:
    if TICKET_FILE.exists():
        with TICKET_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("count", 0))
    return 0

def save_count(n: int) -> None:
    with TICKET_FILE.open("w", encoding="utf-8") as f:
        json.dump({"count": n}, f)


def admin_mode() -> None:
    st.header("管理者モード 👩‍💻")
    st.write("券の残数を自由に増減できます。")

    count = load_count()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➖ 1 枚減らす", disabled=count <= 0):
            count -= 1
    with col2:
        if st.button("🔄 リセット (0)", type="secondary"):
            count = 0
    with col3:
        add = st.number_input("追加する枚数", min_value=1, max_value=100, value=1, step=1, key="add_input")
        if st.button("➕ 追加"):
            count += int(add)

    save_count(count)
    st.success(f"現在の残数: **{count} 枚**")


def user_mode() -> None:
    st.header("デジタル肩たたき券 🎫")
    count = load_count()
    st.info(f"残り枚数: **{count} 枚**")
    if count == 0:
        st.warning("もう券がありません… 管理者に追加してもらってください。")
        st.stop()

    if st.button("券を 1 枚使う"):
        count -= 1
        save_count(count)
        st.switch_page("katatataki_time")  # ページ遷移


def katatataki_time() -> None:
    st.markdown(
        """
        <div style="height:90vh;display:flex;justify-content:center;align-items:center;background:#ffffff;">
            <h1 style="font-size:4rem;color:#000000;">肩たたきタイム</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬅️ 戻る"):
        st.switch_page("app")  # トップへ


page = st.query_params.get("page", "home")

if page == "katatataki_time":
    katatataki_time()
else:
    st.sidebar.title("モード選択")
    mode = st.sidebar.radio("Choose Mode", ("ユーザー", "管理者"))
    if mode == "管理者":
        pwd = st.sidebar.text_input("パスワード", type="password")
        if pwd == ADMIN_PASS:
            admin_mode()
        else:
            st.error("パスワードが違います。")
    else:
        user_mode()
