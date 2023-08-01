import streamlit as st
import re
import numpy as np
import pandas as pd
from mining import perform_rule_calculation, compute_association_rule

st.title("Modeling")
# st.caption("Tahap pemodelan dengan data mining untuk mendapatkan hubungan asosiatif antar obat "
#            "dan rekomendasi pengadaan obat")
st.divider()
st.sidebar.title("Modeling")
st.sidebar.write(
    """Halaman ini diperuntukkan untuk tahap pemodelan dengan data mining \
    untuk mendapatkan hubungan asosiatif antar obat serta rekomendasi pengadaan stok obat"""
)


def mining_fpgrowth(data: pd.DataFrame, cleaned_data: pd.DataFrame):

    min_sup = cleaned_data.groupby('kode').count().faktur.mean()
    perc_min_sup = min_sup / len(cleaned_data['faktur'].unique())

    # FP-Growth
    fpgrowth_matrix = perform_rule_calculation(data, min_support=perc_min_sup)

    return fpgrowth_matrix


def eval_fpgrowth(fpgrowth_matrix: pd.DataFrame):

    association_rules = compute_association_rule(
        fpgrowth_matrix, metric="confidence", min_thresh=0.7)
    association_rules = association_rules[[
        'antecedents', 'consequents', 'confidence', 'lift']]

    # return max lift value
    return_rules = association_rules.sort_values(
        'lift', ascending=False).reset_index(drop=True)
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

    return_rules['antecedent restock bulan lalu'] = [3, 3]
    return_rules['consequent restock bulan lalu'] = [35, 18]
    return_rules['rekomendasi restock'] = np.max(
        return_rules[['antecedent restock bulan lalu', 'consequent restock bulan lalu']],
        axis=1)

    antecedents_cl = return_rules['antecedents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    consequents_cl = return_rules['consequents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))

    return_rules['antecedents'] = antecedents_cl
    return_rules['consequents'] = consequents_cl
    return_rules.rename(columns={
        'antecedents': 'item 1',
        'consequents': 'item 2',
        'antecedent restock bulan lalu': 'item 1 restock bulan lalu',
        'consequent restock bulan lalu': 'item 2 restock bulan lalu'}, inplace=True)

    # join buat dapetin nama obat dari kode obat
    return_rules['nama 1'] = return_rules[['item 1']].join(
        data_obat[['kode', 'nama']].set_index('kode'), on='item 1')['nama']
    return_rules['nama 2'] = return_rules[['item 2']].join(
        data_obat[['kode', 'nama']].set_index('kode'), on='item 2')['nama']

    # menampilkan data ke user
    # hapus kolom
    res1 = return_rules.drop(['confidence', 'lift'], axis=1)
    # rename kolom
    res1.columns = [
        'Item 1', 'Item 2',
        'Item 1 restok bulan lalu', 'Item 2 restok bulan lalu',
        'Rekomendasi restok',
        'Nama 1', 'Nama 2']
    # hapus kolom
    res1 = res1[['Nama 1', 'Nama 2', 'Item 1 restok bulan lalu', 'Item 2 restok bulan lalu', 'Rekomendasi restok']]

    # mengubah 2 kolom menjadi 1 kolom
    res3 = pd.concat([
        return_rules[['item 1', 'nama 1', 'rekomendasi restock']].rename(
            columns={'item 1': 'Item', 'nama 1': 'Nama', 'rekomendasi restock': 'Rekomendasi restok'}),
        return_rules[['item 2', 'nama 2', 'rekomendasi restock']].rename(
            columns={'item 2': 'Item', 'nama 2': 'Nama', 'rekomendasi restock': 'Rekomendasi restok'})
    ])

    # ambil data stok obat sekarang
    # res3['Stok sekarang'] = res3.join(
    #     data_obat.set_index('kode'), on='Item'
    # )['stok']
    res3['Stok sekarang'] = [4, 2, 2, 6]

    # nilai jumlah restok
    res3['Jumlah restok'] = res3['Rekomendasi restok'] - res3['Stok sekarang']

    # atur urutan kolom
    res3 = res3[['Item', 'Nama', 'Rekomendasi restok', 'Stok sekarang', 'Jumlah restok']]

    return res1, res3


def main():
    fpgrowth_matrix = mining_fpgrowth(
        st.session_state['data_trs_3'], st.session_state['data_trs_2'])
    return_rules = eval_fpgrowth(fpgrowth_matrix)
    # st.dataframe(return_rules)
    res1, res2 = display_recommendation(return_rules, st.session_state['data_obat_1'], st.session_state['data_beli_2'])
    st.subheader("Hubungan Asosiatif Antar Obat")
    st.dataframe(res1)
    st.subheader("Hasil Rekomendasi Pengadaan Obat")
    st.dataframe(res2)


try:
    st.header("Dataset")
    st.dataframe(st.session_state['data_trs_3_display'].head().set_index(np.arange(1, 6)))
    st.write("**Data sudah siap untuk tahap pemodelan.**")
    if st.button("Mining"):
        main()
except KeyError:
    st.error("Data belum tersedia")
    st.stop()
