import chromadb
import pandas as pd
import os

STATUS_FILE = "chroma_status.txt"  # File untuk menyimpan status koleksi

def save_to_chroma():
    # Tentukan direktori untuk penyimpanan data ChromaDB
    persist_directory = r"D:\Kuliah\SKRIPSI\Validasi Skripsi\ChromaDB_Storage"

    # Membuat klien Chroma dengan penyimpanan persisten
    client_chroma = chromadb.PersistentClient(path=persist_directory)

    # Nama koleksi
    collection_name = "politik2"

    # Periksa apakah koleksi sudah dibuat sebelumnya
    if os.path.exists(STATUS_FILE):
        print("---- Koleksi sudah dibuat sebelumnya ----")
        return client_chroma.get_collection(name=collection_name)

    # Jika belum, buat koleksi baru
    try:
        collection = client_chroma.create_collection(name=collection_name)
    except Exception as e:
        collection = client_chroma.get_collection(name=collection_name)

    folder_path = r"H:\My Drive\UNIKOM\Skripsi\Code\Validasi Skripsi"

    dataframes = []

    # Loop melalui semua file CSV di folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            # Membaca file CSV ke DataFrame
            df = pd.read_csv(file_path)

            # Mengganti nilai NaN di kolom "tweet" dengan string kosong
            df["tweet"].fillna("", inplace=True)

            dataframes.append(df)

    # Menggabungkan semua DataFrame menjadi satu
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Menghapus duplikat
    combined_df.drop_duplicates(inplace=True)

    # Mengambil kolom "tweet" sebagai list
    documents = combined_df["tweet"].tolist()

    # Menambahkan metadata dengan kolom "keyword"
    metadatas = [{"keyword": "politik"} for _ in range(len(documents))]

    # Menggunakan indeks sebagai ID unik
    ids = [str(i) for i in combined_df.index]

    # Menentukan ukuran batch maksimum yang didukung
    max_batch_size = 5000  # Sesuaikan dengan batasan ChromaDB

    # Fungsi untuk membagi data menjadi batch
    def batch_data(data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    # Menambahkan data ke koleksi dalam batch
    for doc_batch, meta_batch, id_batch in zip(
        batch_data(documents, max_batch_size),
        batch_data(metadatas, max_batch_size),
        batch_data(ids, max_batch_size)
    ):
        collection.add(
            documents=doc_batch,
            metadatas=meta_batch,
            ids=id_batch
        )

    print("---- Data telah berhasil ditambahkan ke Chroma! ----")

    # Tandai bahwa koleksi sudah dibuat
    with open(STATUS_FILE, "w") as f:
        f.write("done")

    return collection

def rag(collection, query_text):
    results = collection.query(
        query_texts=[str(query_text)],
        n_results=1000
    )

    # Mengambil hasil pencarian (dokumen dan skor similarity)
    documents_scores = list(zip(results["documents"][0], results["distances"][0]))

    # Mengurutkan hasil dari skor tertinggi ke terendah
    sorted_results = sorted(documents_scores, key=lambda x: x[1], reverse=False)

    tweets = ""

    for i, (doc, score) in enumerate(sorted_results[:10], start=1):
        tweets += f" \n- Informasi: {doc}"

    return tweets
