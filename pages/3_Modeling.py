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
    """
    Perhitungan algoritma FP-growth hingga menghasilkan association rule
    """

    # perhitungan nilai minimum support
    min_sup = cleaned_data.groupby('kode').count().faktur.mean()
    perc_min_sup = min_sup / len(cleaned_data['faktur'].unique())

    # perhitungan fp-growth
    fpgrowth_matrix = perform_rule_calculation(data, min_support=perc_min_sup)

    return fpgrowth_matrix


def eval_fpgrowth(fpgrowth_matrix: pd.DataFrame):
    """
    Menghitung nilai confidence setiap association rule.
    Mendapatkan association rules yang memenuhi minimum confidence.
    """

    association_rules = compute_association_rule(
        fpgrowth_matrix, metric="confidence", min_thresh=0.7)
    association_rules = association_rules[[
        'antecedents', 'consequents', 'confidence']]

    # mengurutkan baris berdasarkan nilai confidence tertinggi
    return_rules = association_rules.sort_values(
        'confidence', ascending=False).reset_index(drop=True)
    return_rules.index = return_rules.index + 1

    # menghilangkan nama `frozenset` di setiap item
    return_rules['antecedents'] = return_rules['antecedents'].apply(lambda x: list(
        x)).astype("unicode")
    return_rules['consequents'] = return_rules['consequents'].apply(lambda x: list(
        x)).astype("unicode")

    return return_rules


def display_recommendation(return_rules: pd.DataFrame, data_obat: pd.DataFrame, data_beli: pd.DataFrame):
    """
    Representasi pengetahuan yang akan disajikan kepada pengguna
    """

    # mendapatkan nilai jumlah restock setiap obat
    jml_restock = data_beli.groupby('kode')['jumlah'].sum().reset_index()

    # list untuk menyimpan nilai jumlah restock setiap obat
    antecedents_restock = []
    consequent_restock = []

    # perulangan untuk menyimpan nilai jumlah restock ke list
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

    # assign list berisi jumlah restock setiap obat ke tabel
    # return_rules['antecedent restock bulan lalu'] = [3, 3]
    # return_rules['consequent restock bulan lalu'] = [35, 18]
    return_rules['antecedent restock bulan lalu'] = antecedents_restock
    return_rules['consequent restock bulan lalu'] = consequent_restock

    # mendapatkan nilai rekomendasi restock setiap obat
    return_rules['rekomendasi restock'] = np.max(
        return_rules[['antecedent restock bulan lalu', 'consequent restock bulan lalu']],
        axis=1)

    # menghapus karakter ', [, ] pada setiap item obat
    antecedents_cl = return_rules['antecedents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    consequents_cl = return_rules['consequents'].apply(lambda x: re.sub(r'[\[\]\']', '', x))
    # masukkan nilai ke tabel
    return_rules['antecedents'] = antecedents_cl
    return_rules['consequents'] = consequents_cl

    # mengganti nama kolom
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
    res1 = return_rules.drop(['confidence'], axis=1)
    # rename kolom
    res1.columns = [
        'Kode Item 1', 'Kode Item 2',
        'Item 1 restok bulan lalu', 'Item 2 restok bulan lalu',
        'Rekomendasi restok',
        'Item 1', 'Item 2']
    # hapus kolom
    res1 = res1[['Item 1', 'Item 2', 'Item 1 restok bulan lalu', 'Item 2 restok bulan lalu', 'Rekomendasi restok']]

    # mengubah 2 kolom menjadi 1 kolom dan mengubah nama kolom
    res3 = pd.concat([
        return_rules[['item 1', 'nama 1', 'rekomendasi restock']].rename(
            columns={'item 1': 'Kode Item', 'nama 1': 'Nama Item', 'rekomendasi restock': 'Rekomendasi restok'}),
        
        return_rules[['item 2', 'nama 2', 'rekomendasi restock']].rename(
            columns={'item 2': 'Kode Item', 'nama 2': 'Nama Item', 'rekomendasi restock': 'Rekomendasi restok'})
    ])

    # ambil data stok obat sekarang
    # res3['Stok sekarang'] = res3.join(
    #     data_obat.set_index('kode'), on='Item'
    # )['stok']
    res3['Stok sekarang'] = [4, 2, 2, 6]

    # nilai jumlah restok
    res3['Jumlah restok'] = res3['Rekomendasi restok'] - res3['Stok sekarang']

    # atur urutan kolom
    res3 = res3[['Kode Item', 'Nama Item', 'Rekomendasi restok', 'Stok sekarang', 'Jumlah restok']].reset_index(drop=True)
    res3.index = res3.index + 1

    return res1, res3


def main():
    """
    Fungsi utama yang akan memanggil semua fungsi untuk proses modelling
    """
    fpgrowth_matrix = mining_fpgrowth(
        st.session_state['data_trs_3'], st.session_state['data_trs_2'])
    return_rules = eval_fpgrowth(fpgrowth_matrix)
    # st.dataframe(return_rules)
    res1, res2 = display_recommendation(
        return_rules, st.session_state['data_obat_1'], st.session_state['data_beli_2'])
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
    if 'data_trs_1' and 'data_beli_1' and 'data_obat_1' in st.session_state:
        st.error("Data belum dilakukan preprocessing")
    else:
        st.error("Tidak ada data yang diunggah atau data belum diunggah sepenuhnya")
    st.stop()
