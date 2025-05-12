
import streamlit as st, json, time, pathlib
FILE = pathlib.Path("count.json")
if not FILE.exists():
    FILE.write_text(json.dumps({"count": 10}, ensure_ascii=False))

def load():  return json.loads(FILE.read_text())["count"]
def save(c): FILE.write_text(json.dumps({"count": c}, ensure_ascii=False))

st.set_page_config(page_title="肩たたき券")
st.title("残り肩たたき券")
count = load()
st.markdown(f"<h1 style='font-size:5rem'>{count}</h1>", unsafe_allow_html=True)

if st.button("1枚使う", disabled=count<=0):
    count -= 1
    save(count)
    st.session_state["show"]=True
    st.experimental_rerun()

if st.session_state.get("show"):
    st.markdown(
        "<div style='position:fixed;inset:0;display:flex;justify-content:center;"
        "align-items:center;background:#fff;z-index:1000;'>"
        "<h2 style='font-size:4rem'>肩たたきタイム!</h2></div>",
        unsafe_allow_html=True)
    time.sleep(2)
    st.session_state["show"]=False
    st.experimental_rerun()
