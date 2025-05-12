import streamlit as st

st.markdown(
    """
    <div style="height:90vh;display:flex;justify-content:center;align-items:center;background:#ffffff;">
        <h1 style="font-size:4rem;color:#000000;">肩たたきタイム</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("⬅️ 戻る"):
    st.switch_page("app")   # ← app.py の「表示名」が "app" のとき
