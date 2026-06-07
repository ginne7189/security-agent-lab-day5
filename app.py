import streamlit as st
import dashboard_lib as L

st.set_page_config(page_title="Day 5 · 통합 · 현업 적용", page_icon="5\ufe0f\u20e3", layout="wide")
st.title("\U0001f6e1\ufe0f Day 5 · 통합 · 현업 적용")
st.caption("\ud0a4\u00b7\ud1a0\ud070 \uc5c6\uc774 \ub3d9\uc791 \u00b7 \uc678\ubd80 API \ud638\ucd9c \uc5c6\uc74c")

L.render_overview()
L.render_day5()
