import streamlit as st
import pandas as pd
import warnings
import re
import numpy as np
warnings.filterwarnings('ignore')
from mining import perform_rule_calculation, compute_association_rule

st.markdown("# Rekomendasi Pengadaan Obat")
# st.sidebar.markdown("# Main page 🎈")


def import_file(file_path):
    try:
        # Baca file Excel menjadi DataFrame
        df = pd.read_excel(file_path)

        # Tampilkan data di Streamlit
        st.write("**Berhasil import data.**")

        return df

    except Exception as e:
        st.error("Terjadi kesalahan saat membaca file.")
        st.error(e)


def main():
    uploaded_file = st.file_uploader(
        "**Unggah file excel data transaksi detail penjualan**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_trs = import_file(uploaded_file)

    uploaded_file = st.file_uploader(
        "**Unggah file excel data transaksi detail pembelian**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_beli = import_file(uploaded_file)

    uploaded_file = st.file_uploader(
        "**Unggah file excel data obat**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_obat = import_file(uploaded_file)

    if uploaded_file is not None:
        st.session_state['data_trs_1'] = data_trs
        st.session_state['data_beli_1'] = data_beli
        st.session_state['data_obat_1'] = data_obat


if __name__ == "__main__":
    main()
