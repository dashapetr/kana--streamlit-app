import streamlit as st
import random
from config import SELECT_KANA_DICT, CHECK_KANA_DICT


def change_character():
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
    return


def change_mode(new_mode):
    st.session_state.mode = new_mode
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
    return


st.set_page_config(
    page_title="Kana to romaji",
    page_icon=":sa:")

st.title("📝 Welcome to kana app!")
st.subheader("Use this page to practice kana reading!")
st.divider()

if 'mode' not in st.session_state:
    st.session_state.mode = None

new_mode = st.radio(
    "What type of kana do you want to practice?",
    ["Hiragana", "Katakana"],
    horizontal=True
)

if new_mode != st.session_state.mode:
    change_mode(new_mode)

if "character" not in st.session_state:
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))

if st.session_state.mode is not None:

    st.subheader(st.session_state.character)

    st.button("New character?", on_click=change_character)

    st.write(f"Please write in the window below romaji reading for {st.session_state.mode} character"
             f" {st.session_state.character}:")

    with st.form("my_form"):
        user_romaji = st.text_input("Write your romaji here", "")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if CHECK_KANA_DICT.get(st.session_state.mode).get(user_romaji) == st.session_state.character:
                st.success(f'Yes,   {st.session_state.character}   is "{user_romaji}"!', icon="✅")
                st.balloons()
            else:
                st.error(f'No,   {st.session_state.character}   is NOT "{user_romaji}"!', icon="🚨")
