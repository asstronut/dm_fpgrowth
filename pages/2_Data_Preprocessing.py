import numpy as np
import streamlit as st
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder

st.markdown("# Data Preprocessing")
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
    if 'data_trs_1' and 'data_beli_1' and 'data_obat_1' in st.session_state:
        st.write("## Bentuk Data Awal")

        st.write("### Data Penjualan")
        st.dataframe(st.session_state['data_trs_1'].head().set_index(np.arange(1, 6)))

        st.write("### Data Pembelian")
        st.dataframe(st.session_state['data_beli_1'].head().set_index(np.arange(1, 6)))

        st.write("### Data Obat")
        st.dataframe(st.session_state['data_obat_1'].head().set_index(np.arange(1, 6)))

        if st.button("Preprocess Data"):
            st.session_state['data_trs_2'] = prepare_data(
                st.session_state['data_trs_1'], 'penjualan')
            st.session_state['data_beli_2'] = prepare_data(
                st.session_state['data_beli_1'], 'pembelian')
            st.session_state['data_obat_2'] = prepare_data(
                st.session_state['data_obat_1'], 'obat')

            st.write("## Pemilihan Atribut")
            st.dataframe(st.session_state['data_trs_2'].head().set_index(np.arange(1, 6)))
            st.dataframe(st.session_state['data_beli_2'].head().set_index(np.arange(1, 6)))
            st.dataframe(st.session_state['data_obat_2'].head().set_index(np.arange(1, 6)))

            st.session_state['data_trs_3'], df_display_trs = format_data(
                st.session_state['data_trs_2'])

            st.write('## Pemformatan Data')
            st.dataframe(df_display_trs.head().set_index(np.arange(1, 6)))
    else:
        st.error("Data belum diimport.")


main()
