#import streamlit as st
from Discovery import run as run_discovery
from Test_Result import run as run_test_result
import pandas as pd
from data_processing import finalize_data

# Fungsi untuk navigasi antar halaman
def navigate_to(page):
    st.session_state.page = page

# Menentukan state halaman
if "page" not in st.session_state:
    st.session_state.page = "main"

# Mengatur navigasi berdasarkan state
if st.session_state.page == "main":
    run_discovery(navigate_to)
elif st.session_state.page == "results":
    run_test_result(navigate_to)
