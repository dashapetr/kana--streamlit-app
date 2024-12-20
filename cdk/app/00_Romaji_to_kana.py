import streamlit as st
import random
from PIL import Image
from manga_ocr import MangaOcr
import os
from streamlit_drawable_canvas import st_canvas
from config import ALL_ROMAJI, CHECK_KANA_DICT
from huggingface_hub import snapshot_download


def change_romaji():
    st.session_state.romaji = random.choice(ALL_ROMAJI)
    return


def change_mode(new_mode):
    st.session_state.mode = new_mode
    st.session_state.romaji = random.choice(ALL_ROMAJI)
    return


def download_model():
    model_dir = "/models/manga-ocr"
    if not os.path.exists(model_dir):
        snapshot_download(repo_id="TareHimself/manga-ocr-base", local_dir=model_dir)
    return model_dir


def recognize_character(mocr):
    character_file_path = os.path.join(os.getcwd(), "result.png")
    if not os.path.exists(character_file_path):
        raise FileNotFoundError(f"The file {character_file_path} does not exist.")

    img = Image.open(character_file_path)
    text = mocr(img)
    return text.strip()[0]


st.set_page_config(
        page_title="Romaji to kana",
        page_icon=":sa:")

st.title("📝 Welcome to kana app!")
st.subheader("Use this page to practice kana writing!")
st.divider()

if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'mocr' not in st.session_state:
    st.session_state.mocr = MangaOcr(pretrained_model_name_or_path=download_model())

new_mode = st.radio(
    "What type of kana do you want to practice?",
    ["Hiragana", "Katakana"],
    horizontal=True
)

if new_mode != st.session_state.mode:
    change_mode(new_mode)

if "romaji" not in st.session_state:
    st.session_state.romaji = random.choice(ALL_ROMAJI)

st.subheader(st.session_state.romaji)

st.button("New character?", on_click=change_romaji)

st.write(f"Please write in the window below {st.session_state.mode} for {st.session_state.romaji}:")
with st.form("my_form", clear_on_submit=True):
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0)",
        stroke_width=6,
        stroke_color="#000000",
        background_color="#FFFFFF",
        background_image=None,
        height=300,
        point_display_radius=0,
        key="full_app",
    )

    file_path = f"result.png"

    submitted = st.form_submit_button("Submit")
    if submitted:
        img_data = canvas_result.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")
        im.save(file_path, "PNG")
        user_result = recognize_character(st.session_state.mocr)
        if CHECK_KANA_DICT.get(st.session_state.mode).get(st.session_state.romaji) == user_result:
            st.success(f'Yes,   {st.session_state.romaji}   is "{user_result}"!', icon="✅")
            st.balloons()
        else:
            st.error(f'No,   {st.session_state.romaji}   is NOT "{user_result}"!', icon="🚨")
