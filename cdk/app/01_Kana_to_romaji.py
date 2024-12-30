import streamlit as st
import random
from config import SELECT_KANA_DICT, CHECK_KANA_DICT


def change_character():
    """Change the current character to a random one from the selected mode."""
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
    return


def change_mode(new_mode: str) -> None:
    """Update the mode (Hiragana or Katakana) and change the character accordingly."""
    st.session_state.mode = new_mode
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
    return


# Page configuration
st.set_page_config(
    page_title="Kana to romaji",
    page_icon=":sa:")

# Page title and description
st.title("📝 Welcome to kana app!")
st.subheader("Use this page to practice kana reading!")
st.divider()

# Initialize session state variables
if 'mode' not in st.session_state:
    st.session_state.mode = None

if "character" not in st.session_state:
    st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))

# Select mode
new_mode = st.radio(
    "What type of kana do you want to practice?",
    ["Hiragana", "Katakana"],
    horizontal=True
)

# Change mode if a new mode is selected
if new_mode != st.session_state.mode:
    change_mode(new_mode)

if st.session_state.mode is not None:
    # Display the current character
    st.subheader(st.session_state.character)

    # Button to generate a new character
    st.button("New character?", on_click=change_character)

    # Input and validation
    st.write(f"Please write in the window below romaji reading for {st.session_state.mode} character"
             f" {st.session_state.character}:")

    with st.form("romaji_form"):
        # User input
        user_romaji = st.text_input("Write your romaji here", "")
        user_romaji_lower_case = user_romaji.lower()

        # Submit button
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Check if the user input matches the expected romaji for the character
            if CHECK_KANA_DICT.get(st.session_state.mode).get(user_romaji_lower_case) == st.session_state.character:
                st.success(f'Yes,   {st.session_state.character}   is "{user_romaji_lower_case}"!', icon="✅")
                st.balloons()
            else:
                st.error(f'No,   {st.session_state.character}   is NOT "{user_romaji_lower_case}"!', icon="🚨")
