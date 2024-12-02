import streamlit as st
import random
from streamlit_drawable_canvas import st_canvas
from config import SELECT_KANA_DICT

st.set_page_config(
        page_title="Romaji to kana",
        page_icon="::")

st.title("📝 Welcome to kana app!")
st.subheader("Use this page to practice kana writing!")
st.divider()

if 'mode' not in st.session_state:
    st.session_state.mode = None

st.session_state.mode = st.selectbox(
        "What type of kana do you want to practice?",
        ("Hiragana", "Katakana"),
        placeholder="Select your mode"
    )

st.session_state.character = random.choice(SELECT_KANA_DICT.get(st.session_state.mode))
st.write(f"Please write in the window below {st.session_state.mode} for {st.session_state.character}:")

# Create a canvas component
canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0)",  # Fixed fill color with some opacity
            stroke_width=6,
            stroke_color="#000000",
            background_color="#FFFFFF",
            background_image=None,
          #  update_streamlit=realtime_update,
            height=150,
          #  drawing_mode=drawing_mode,
            point_display_radius=0,
            display_toolbar=st.sidebar.checkbox("Display toolbar", True),
            key="full_app",
        )
# check input
