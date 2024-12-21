import streamlit as st

pg = st.navigation([st.Page(page="000_Learn_Kana.py", url_path='Learn_Kana'),
                    st.Page(page="00_Romaji_to_kana.py", url_path='Romaji_to_kana'),
                    st.Page(page="01_Kana_to_romaji.py", url_path='Kana_to_romaji')])
pg.run()
