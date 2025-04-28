from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

# URI MongoDB
uri = "mongodb+srv://validasi:sociachat123@validasi.57paaa9.mongodb.net/?appName=Validasi"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("--- Pinged your deployment. You successfully connected to MongoDB!  ---")
except Exception as e:
    print(e)

# Pilih database dan koleksi
db = client['validation_database']
collections = db['validation_collection']
accounts_collection = db['accounts_collection']

def show_data():
    # Inisialisasi list kosong untuk pertanyaan dan jawaban
    questions = []
    answers = []

    # Ambil semua dokumen dari koleksi
    for document in collections.find():
        # Tambahkan pertanyaan dan jawaban ke dalam list
        if 'chat' in document and 'response' in document:
            questions.append(document['chat'])
            answers.append(document['response'])

    # Format data ke dalam struktur JSON yang diinginkan
    result = {
        "questions": questions,
        "answers": answers
    }
    return result

def delete_data():
    # Hapus semua data dari koleksi
    collections.delete_many({})
    return "Data deleted successfully"

from bson import ObjectId  # Digunakan untuk menangani ObjectId dari MongoDB

def login(username, password,nama):
    # Mencari dokumen dengan username dan password yang cocok
    user = accounts_collection.find_one({"username": username, "password": password})
    
    if user:
        # Mengembalikan status sukses beserta ID pengguna
        return json.dumps({
            "status": "success",
            "message": "Login berhasil",
            "user_id": str(ObjectId(user["_id"])),
            "username": username,
            "nama" : str(nama) # Konversi ObjectId ke string
        })
    else:
        # Mengembalikan status error jika username atau password salah
        return json.dumps({
            "status": "error",
            "message": "Username atau password salah"
        })


def simpan_data_user(data_user):
    data_user_collection = db['results_collection']

    insert_result = data_user_collection.insert_one(data_user)

    # Tampilkan ID dari dokumen yang baru saja dimasukkan
    return print("Data berhasil dimasukkan dengan ID:", insert_result.inserted_id)

# # Tes fungsi show_data()
# tes = show_data()

# # Cetak tipe data hasil dan hasilnya dalam format JSON
# print(tes)  # Harusnya <class 'dict