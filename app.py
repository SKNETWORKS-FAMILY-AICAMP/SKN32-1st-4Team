import streamlit as st


st.set_page_config(
    page_title="K-Car Navigator",
    page_icon="car",
    layout="wide",
)

pages = [
    st.Page("pages/1_dashboard.py", title="시장 인사이트", icon=":material/analytics:"),
    st.Page("pages/2_faq.py", title="FAQ 센터", icon=":material/help:"),
]

navigation = st.navigation(pages)
navigation.run()
