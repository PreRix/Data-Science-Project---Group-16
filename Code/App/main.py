# ====================================
# Imports

import streamlit as st
from utils.navigation import setup

# ====================================
# Website design

st.set_page_config(
    page_title="DSP - Group 16",
    page_icon="📊",
    layout="wide",
    menu_items={
        "About": "[Check out our GitHub Repository](https://github.com/PreRix/Data-Science-Project---Group-16)"
    }
)

setup()