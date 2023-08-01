import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.title("Rekomendasi Pengadaan Obat")
st.divider()
st.header("Unggah file data")
st.sidebar.markdown("# Home")


def import_file(file_path):
    try:
        # Baca file Excel menjadi DataFrame
        df = pd.read_excel(file_path)

        # Tampilkan data di Streamlit
        st.write(":green[**Berhasil import data.**] :white_check_mark:")

        return df

    except Exception as e:
        st.error("Terjadi kesalahan saat membaca file.")
        st.error(e)


def main():
    uploaded_file = st.file_uploader(
        "**Data transaksi detail penjualan**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_trs = import_file(uploaded_file)

    uploaded_file = st.file_uploader(
        "**Data transaksi detail pembelian**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_beli = import_file(uploaded_file)

    uploaded_file = st.file_uploader(
        "**Data obat**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_obat = import_file(uploaded_file)

    if uploaded_file is not None:
        st.session_state['data_trs_1'] = data_trs
        st.session_state['data_beli_1'] = data_beli
        st.session_state['data_obat_1'] = data_obat


if __name__ == "__main__":
    main()
