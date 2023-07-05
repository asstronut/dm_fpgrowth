from mining import perform_rule_calculation, compute_association_rule
from mlxtend.preprocessing import TransactionEncoder
import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def import_data(file_path):
    try:
        # Baca file Excel menjadi DataFrame
        df = pd.read_excel(file_path)

        # Tampilkan data di Streamlit
        st.write("Berhasil import data.")

    except Exception as e:
        st.error("Terjadi kesalahan saat membaca file.")
        st.error(e)
    return df


def prepare_data(df: pd.DataFrame):
    # select data
    df = df[['Unnamed: 5', 'Unnamed: 1']]

    # rename column data
    df.columns = ['faktur', 'nama_obat']

    # data cleaning
    df.drop(df.iloc[[0]].index, inplace=True)
    df.drop(
        df[df['nama_obat'] == 'Laporan Penjualan per Barang'].index, inplace=True)
    df.drop(df[df['nama_obat'] == 'Cetak :'].index, inplace=True)
    df.drop(df[df['faktur'] == 'faktur'].index, inplace=True)
    df.dropna(how='all', inplace=True)
    df = df.reset_index(drop=True)

    # normalize data
    df['nama_obat'] = df['nama_obat'].fillna(method='ffill')
    df = df.dropna().sort_values('faktur').reset_index(drop=True)

    # rename column data, only for display
    # df.columns = ['Faktur', 'Nama Obat']
    return df


def format_data(df: pd.DataFrame):
    df = [item[1]['nama_obat'].tolist()
          for item in list(df.groupby('faktur'))]

    # The following instructions transform the dataset into the required format
    trans_encoder = TransactionEncoder()  # Instanciate the encoder
    trans_encoder_matrix = trans_encoder.fit(
        df).transform(df)
    formatted_data = pd.DataFrame(
        trans_encoder_matrix, columns=trans_encoder.columns_)

    return formatted_data


def mining_fpgrowth(data: pd.DataFrame, cleaned_data: pd.DataFrame):
    min_sup = cleaned_data.groupby('nama_obat').count().faktur.mean()
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


def display_recommendation(return_rules: pd.DataFrame):
    for i, j in return_rules.iterrows():
        st.write(f"Rule {i}:")
        st.write(
            f"Jika membeli **{j['antecedents']}**, maka akan membeli **{j['consequents']}** dengan confidence {j['confidence']} dan lift {j['lift']}")
        st.write("")


def main():
    st.title("Rekomendasi Pengadaan Obat")

    # Tambahkan komponen untuk mengunggah file Excel
    uploaded_file = st.file_uploader(
        "Unggah file excel data transaksi", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Panggil fungsi import_data() untuk mengimpor data
        data = import_data(uploaded_file)

        if st.button("Mining Data"):
            cleaned_data = prepare_data(data)
            formatted_data = format_data(cleaned_data)
            # fpgrowth_matrix, min_sup, perc_min_sup = mining_fpgrowth(
            #     formatted_data, cleaned_data)
            fpgrowth_matrix = mining_fpgrowth(
                formatted_data, cleaned_data)
            # st.dataframe(fpgrowth_matrix, width=1000, height=500)
            return_rules = eval_fpgrowth(fpgrowth_matrix)
            st.dataframe(return_rules)
            # st.write(min_sup)
            # st.write(perc_min_sup)
            # display recommendation
            display_recommendation(return_rules)


if __name__ == '__main__':
    main()
