import streamlit as st
import random
from config import SELECT_KANA_DICT

st.set_page_config(
        page_title="Kana to romaji",
        page_icon="::")

st.title("📝 Welcome to kana app!")
st.subheader("Use this page to practice kana reading!")
st.divider()

if 'mode' not in st.session_state:
    st.session_state.mode = None

st.session_state.mode = st.selectbox(
        "What type of kana do you want to practice?",
        ("Hiragana", "Katakana"),
        placeholder="Select your mode"
    )

st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
st.show()  # show the picture of selected character
st.write(f"Please write in the window below romaji reading for {st.session_state.mode} character"
         f" {st.session_state.character}:")
st.user_input()
# submit and check
