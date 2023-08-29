import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.title("Rekomendasi Pengadaan Obat")
st.divider()
st.header("Unggah file data")
st.sidebar.markdown("# Unggah Data")
st.sidebar.markdown(
    """
    Pada halaman ini user dapat mengunggah file excel berisi data-data yang dibutuhkan, \
    yaitu data penjualan, data pembelian, dan data obat.
    """
)


def import_file(file_path, file_data: str):
    try:
        # Baca file Excel menjadi DataFrame
        df = pd.read_excel(file_path)

        # cek isi data
        if check_file_content(df, file_data):
            # Tampilkan data di Streamlit
            st.success("Berhasil import data")
            return df
        else:
            st.error("Data tidak valid")
            # return

    except Exception as e:
        st.error("Terjadi kesalahan saat membaca file.")
        st.error(e)


def check_file_content(data: pd.DataFrame, file_data: str):
    if file_data == 'penjualan':
        if len(data.columns) == 14:
            return True
        return False
    elif file_data == 'pembelian':
        if len(data.columns) == 33:
            return True
        return False
    else:
        if len(data.columns) == 31:
            return True
        return False


def main():
    uploaded_file = st.file_uploader(
        "**Data transaksi detail penjualan**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_trs = import_file(uploaded_file, "penjualan")

    uploaded_file = st.file_uploader(
        "**Data transaksi detail pembelian**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_beli = import_file(uploaded_file, "pembelian")

    uploaded_file = st.file_uploader(
        "**Data obat**", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data_obat = import_file(uploaded_file, "obat")

    if uploaded_file is not None:
        st.session_state['data_trs_1'] = data_trs
        st.session_state['data_beli_1'] = data_beli
        st.session_state['data_obat_1'] = data_obat


if __name__ == "__main__":
    main()
