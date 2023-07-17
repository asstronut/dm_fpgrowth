from mining import perform_rule_calculation, compute_association_rule
from mlxtend.preprocessing import TransactionEncoder
import streamlit as st
import pandas as pd
import warnings
import re
import numpy as np
warnings.filterwarnings('ignore')


def import_file(file_path):
    try:
        # Baca file Excel menjadi DataFrame
        df = pd.read_excel(file_path)

        # Tampilkan data di Streamlit
        st.write("Berhasil import data.")

    except Exception as e:
        st.error("Terjadi kesalahan saat membaca file.")
        st.error(e)
    return df


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
    df = [item[1]['kode'].tolist()
          for item in list(df.groupby('faktur'))]

    # The following instructions transform the dataset into the required format
    trans_encoder = TransactionEncoder()  # Instanciate the encoder
    trans_encoder_matrix = trans_encoder.fit(
        df).transform(df)
    formatted_data = pd.DataFrame(
        trans_encoder_matrix, columns=trans_encoder.columns_)

    return formatted_data


def mining_fpgrowth(data: pd.DataFrame, cleaned_data: pd.DataFrame):
    min_sup = cleaned_data.groupby('kode').count().faktur.mean()
    perc_min_sup = min_sup / len(cleaned_data['faktur'].unique())
    # FP-Growth
    fpgrowth_matrix = perform_rule_calculation(data, min_support=perc_min_sup)

    # return fpgrowth_matrix, min_sup, perc_min_sup
    return fpgrowth_matrix


def eval_fpgrowth(fpgrowth_matrix: pd.DataFrame):
    association_rules = compute_association_rule(
        fpgrowth_matrix, metric="confidence", min_thresh=0.7)
    association_rules = association_rules[[
        'antecedents', 'consequents', 'confidence', 'lift']]
    # return max lift value
    return_rules = association_rules.sort_values(
        'lift', ascending=False).head(5).reset_index(drop=True)
    return_rules.index = return_rules.index + 1

    return_rules['antecedents'] = return_rules['antecedents'].apply(lambda x: list(
        x)).astype("unicode")
    return_rules['consequents'] = return_rules['consequents'].apply(lambda x: list(
        x)).astype("unicode")

    return return_rules


def display_recommendation(return_rules: pd.DataFrame, data_obat: pd.DataFrame, data_beli: pd.DataFrame):
    jml_restock = data_beli.groupby('kode')['jumlah'].sum().reset_index()

    antecedents_restock = []
    consequent_restock = []

    for i, j in return_rules.iterrows():
        antecedents = re.sub(r'[\[\]\']', '', j['antecedents'])
        if jml_restock[jml_restock['kode'] == antecedents]['jumlah'].empty:
            antecedents_restock.append(0)
        else:
            jml_restock_obat = int(jml_restock[jml_restock['kode'] == antecedents]['jumlah'].values[0]) // 4
            antecedents_restock.append(jml_restock_obat)
        consquents = re.sub(r'[\[\]\']', '', j['consequents'])
        if jml_restock[jml_restock['kode'] == consquents]['jumlah'].empty:
            consequent_restock.append(0)
        else:
            jml_restock_obat = int(jml_restock[jml_restock['kode'] == consquents]['jumlah'].values[0]) // 4
            consequent_restock.append(jml_restock_obat)

    return_rules['antecedent_prev_restock'] = antecedents_restock
    return_rules['consequent_prev_restock'] = consequent_restock
    return_rules['associate_restock'] = np.max(return_rules[['antecedent_prev_restock', 'consequent_prev_restock']],
                                               axis=1)
    # return_rules['antecedents'] = return_rules['antecedents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    antecedents_cl = return_rules['antecedents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    consequents_cl = return_rules['consequents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    # st.write(antecedents_cl)
    # return_rules['antecedent_current_stock'] = data_obat[data_obat['kode'].isin(antecedents_cl)]['stok'].values
    # return_rules['consequent_current_stock'] = data_obat[data_obat['kode'].isin(consequents_cl)]['stok'].values
    # return_rules['antecedent_current_stock'] = [2, 1]
    # return_rules['consequent_current_stock'] = [2, 2]
    # antecedents_name = data_obat[data_obat['kode'] == antecedents]['nama'].values
    # consequents = j['consequents'][2:-2]
    # consequents_name = data_obat[data_obat['kode'] == consequents]['nama'].values
    #
    # lift_rnd = j['lift']
    # confidence_rnd = j['confidence']
    # st.write(
    #     f"Jika membeli **{antecedents_name}**, maka akan membeli **{consequents_name}** dengan confidence {confidence_rnd} dan lift {lift_rnd}")
    # st.write("")
    st.dataframe(return_rules.drop(['confidence', 'lift'], axis=1))


def main():
    st.title("Rekomendasi Pengadaan Obat")

    # Tambahkan komponen untuk mengunggah file Excel
    uploaded_file_trs = st.file_uploader(
        "Unggah file excel data transaksi detail penjualan", type=["xlsx", "xls"])
    if uploaded_file_trs is not None:
        data_trs = import_file(uploaded_file_trs)
        data_trs = prepare_data(data_trs, 'penjualan')
    
    uploaded_file_beli = st.file_uploader(
        "Unggah file excel data transaksi detail pembelian", type=["xlsx", "xls"])
    if uploaded_file_beli is not None:
        data_beli = import_file(uploaded_file_beli)
        data_beli = prepare_data(data_beli, 'pembelian')
    
    uploaded_file_obat = st.file_uploader(
        "Unggah file excel data obat", type=["xlsx", "xls"])
    if uploaded_file_obat is not None:
        data_obat = import_file(uploaded_file_obat)
        data_obat = prepare_data(data_obat, 'obat')

    if uploaded_file_trs and uploaded_file_beli and uploaded_file_obat is not None:
        if st.button("Mining Data"):
            formatted_data = format_data(data_trs)
            fpgrowth_matrix = mining_fpgrowth(
                formatted_data, data_trs)
            return_rules = eval_fpgrowth(fpgrowth_matrix)
            # st.dataframe(return_rules)
            display_recommendation(return_rules, data_obat, data_beli)


if __name__ == '__main__':
    main()
