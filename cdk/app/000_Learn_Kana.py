import streamlit as st

st.set_page_config(
    page_title="Kana Learning App",
    page_icon="📝",
    layout="centered",
)

st.title("📝 Welcome to the Kana Learning App!")
st.subheader("Use this page to learn kana!")
st.divider()

if 'study_mode' not in st.session_state:
    st.session_state.study_mode = None

st.session_state.study_mode = st.radio(
    "What type of kana do you want to learn?",
    ["Hiragana", "Katakana"],
    horizontal=True
)

# Display the Kana Chart
image_path = f"img/{st.session_state.study_mode}.jpg"
try:
    st.image(image_path,
             caption=f"{st.session_state.study_mode} Chart. "
                     f"Source: https://www.japanistry.com/hiragana-katakana/")
except FileNotFoundError:
    st.error(
        f"Could not load the image for {st.session_state.study_mode}. "
        f"Please check the file path: {image_path}")

# Footer
st.divider()
st.markdown(
    """
    🎯 **Practice Makes Perfect!**  
    👉 Visit the **Romaji to kana** and **Kana to romaji** pages to test your knowledge.  
    🔁 Switch between *Hiragana* and *Katakana* modes to sharpen your skills.  
    🌟 Keep practicing and track your progress regularly!
    """,
)
