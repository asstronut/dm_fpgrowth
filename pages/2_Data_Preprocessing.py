import numpy as np
import streamlit as st
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder

st.title("Data Preprocessing")
st.divider()
st.sidebar.markdown("# Data Preprocessing")


def prepare_data(df: pd.DataFrame, file_data):
    if file_data == 'penjualan':
        df = df[['faktur', 'kode']]
        df.drop(df[df['kode'] == 'R/ dokter'].index, inplace=True)
    elif file_data == 'pembelian':
        df = df[['tanggal', 'kode', 'nama', 'jumlah']]
    elif file_data == 'obat':
        df = df[['kode', 'nama', 'stok']]
    return df


def format_data(df: pd.DataFrame):
    df_display = df.groupby("faktur")[['kode']].apply(
        lambda x: x.values.tolist()).reset_index(name='kode')
    df = [item[1]['kode'].tolist()
          for item in list(df.groupby('faktur'))]

    # The following instructions transform the dataset into the required format
    trans_encoder = TransactionEncoder()  # Instanciate the encoder
    trans_encoder_matrix = trans_encoder.fit(
        df).transform(df)
    formatted_data = pd.DataFrame(
        trans_encoder_matrix, columns=trans_encoder.columns_)

    return formatted_data, df_display


def main():
    st.session_state['data_trs_2'] = prepare_data(
        st.session_state['data_trs_1'], 'penjualan')
    st.session_state['data_beli_2'] = prepare_data(
        st.session_state['data_beli_1'], 'pembelian')
    st.session_state['data_obat_2'] = prepare_data(
        st.session_state['data_obat_1'], 'obat')

    st.header("Pemilihan Atribut")
    st.caption("Bentuk data setelah tahap pemilihan atribut")

    st.subheader("Data Penjualan")
    st.dataframe(st.session_state['data_trs_2'].head().set_index(np.arange(1, 6)))
    st.subheader("Data Pembelian")
    st.dataframe(st.session_state['data_beli_2'].head().set_index(np.arange(1, 6)))
    st.subheader("Data Obat")
    st.dataframe(st.session_state['data_obat_2'].head().set_index(np.arange(1, 6)))

    st.session_state['data_trs_3'], st.session_state['data_trs_3_display'] = format_data(
        st.session_state['data_trs_2'])

    st.header('Pemformatan Data')
    st.caption("Data penjualan setelah tahap pemformatan")
    st.dataframe(st.session_state['data_trs_3_display'].head().set_index(np.arange(1, 6)))


if 'data_trs_1' and 'data_beli_1' and 'data_obat_1' in st.session_state:
    st.header("Bentuk Data Awal")

    st.subheader("Data Penjualan")
    st.dataframe(st.session_state['data_trs_1'].head().set_index(np.arange(1, 6)))

    st.subheader("Data Pembelian")
    st.dataframe(st.session_state['data_beli_1'].head().set_index(np.arange(1, 6)))

    st.subheader("Data Obat")
    st.dataframe(st.session_state['data_obat_1'].head().set_index(np.arange(1, 6)))

    # main function for preprocessing data
    if st.button("Preprocess Data"):
        main()
        st.write(":green[**Berhasil preprocessing data.**] :white_check_mark:")
else:
    st.error("Data belum diimport.")
