from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import pandas as pd
import os
import sys
from bson.objectid import ObjectId
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import getpass
from selenium.webdriver.common.action_chains import ActionChains

def save_to_sheet(db, username):
    collections = db['validation_collection']
    user_collection = db['accounts_collection']

    results = user_collection.find_one({"username": username})

    if results:
        # Ambil _id dari hasil query
        user_id = results["_id"]
        print("User ID:", user_id)
    else:
        print("Username tidak ditemukan.")

    # GET DATA FROM MONGO DB
    questions = []
    answers = []

    if username == "user1":
        filename = 'qa_data_henike.xlsx'
        link_gsheet = "https://docs.google.com/spreadsheets/d/1aAF7gj7fVTeYpysT4RIwbsx-VHYJ0hXh2gQqi-6cets/edit?usp=drive_link"
    elif username == "user2":  
        filename = 'qa_data_rino.xlsx'
        link_gsheet = "https://docs.google.com/spreadsheets/d/1GZ4O7MmevdmJoQlMrm-s9hHFhmlTdilOWCL3-M2ZdUQ/edit?usp=drive_link"
    elif username == "user3":
        filename = 'qa_data_tatik.xlsx'
        link_gsheet = "https://docs.google.com/spreadsheets/d/1J_7oyfDkP0j5O0oZA_ItceQ56U1i6FiEdQdaAzp1ZRg/edit?usp=drive_link"

    if os.path.exists(filename):
        df = pd.read_excel(filename)
        print(f"File Excel ditemukan dengan {len(df)} entri yang ada")
    else:
        df = pd.DataFrame(columns=['Question', 'Answer'])
        print("Membuat file Excel baru")

    existing_df = df.copy()

    # ------------- Ambil data baru dari MongoDB berdasarkan user_id -------------
    new_questions = []
    new_answers = []

    for document in collections.find({"user_id": str(user_id)}):
        if 'chat' in document and 'response' in document:
            # Cek apakah Q&A sudah ada di Excel
            if not existing_df[existing_df['Question'] == document['chat']].empty:
                continue  # Lewati jika data sudah ada
            
            new_questions.append(document['chat'])
            new_answers.append(document['response'])

    new_df = pd.DataFrame({
        'Question': new_questions,
        'Answer': new_answers
    })

    if existing_df.empty:
        updated_df = new_df
        print("File Excel kosong. Mengisi dengan data baru.")
    else:
        # Gabungkan dengan data yang sudah ada
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

    updated_df.to_excel(filename, index=False)
    print(f"Data berhasil diperbarui. Total {len(updated_df)} Q&A tersimpan")

    questions = updated_df['Question'].tolist()
    answers = updated_df['Answer'].tolist()

    print("Pertanyaan dan jawaban berhasil diambil dari MongoDB dan disimpan ke Excel.")
    # END GET DATA FROM MONGO DB

    # ------------- SIMPAN KE GOOGLE SHEET -------------
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Navigate directly to the specified Google Sheet
        driver.get(link_gsheet)
        
        # Step 1: Find the name box input with class "jfk-textinput waffle-name-box" as suggested
        print("Looking for the name box...")
        try:
            # Try with ID if classes don't work
            name_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "t-name-box"))
            )
            print("Found name box using ID")
        except Exception as e:
            print(f"Could not find name box: {e}")
            raise

        # Step 2: Click the name box and enter A2
        print("Clicking on name box and entering A2...")
        name_box.click()
        
        # Clear existing text and type A2
        name_box.clear()
        name_box.send_keys("A2")
        name_box.send_keys(Keys.ENTER)
        
        print("Successfully navigated to cell A2 using name box")


        # Memasukkan data untuk setiap pertanyaan dan jawaban
        for i, (q, a) in enumerate(zip(new_questions, new_answers)):
            print(f"Memproses pasangan data {i+1}/{len(new_questions)}")

            def send_keys_with_newlines(element, text):
                """Fungsi untuk mengirim teks dengan dukungan Ctrl+Enter."""
                actions = ActionChains(driver)
                parts = text.split('\n')
                
                for i, part in enumerate(parts):
                    if i > 0:  # Jika bukan bagian pertama, tekan Ctrl+Enter
                        actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL)
                    actions.send_keys(part)
                
                actions.perform()

            def find_empty_row():
                """Fungsi untuk mencari baris kosong di kolom A."""
                while True:
                    # Ambil elemen aktif saat ini (kolom A)
                    active_element = driver.switch_to.active_element
                    # current_value = active_element.get_attribute("value") or ""
                    
                    print("Looking for the name box...")
                    try:
                        # Try with ID if classes don't work
                        isi_shell = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "t-formula-bar-input-container"))
                        )
                        print("Found name box using ID")
                    except Exception as e:
                        print(f"Could not find name box: {e}")
                        raise

                    current_value = str(isi_shell.text)

                    # Jika kolom A kosong, kembalikan baris ini
                    if not current_value.strip():
                        return
                    
                    # Jika tidak kosong, pindah ke baris berikutnya
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    time.sleep(0.5) 

            # Cari baris kosong di kolom A
            find_empty_row()
            
            # Mengetik pertanyaan di kolom A
            send_keys_with_newlines(driver.switch_to.active_element, q)
            time.sleep(0.5)
            
            # Pindah ke kolom B (untuk jawaban)
            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.5)
            
            # Mengetik jawaban dengan dukungan Ctrl+Enter
            send_keys_with_newlines(driver.switch_to.active_element, a)
            time.sleep(0.5)
            
            # Pindah ke baris berikutnya
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(0.5)
            
            print(f"Baris {i+2} ditambahkan: Pertanyaan dan Jawaban")

        print("Data berhasil diekspor ke Google Sheet")

        # Jeda sebelum menutup
        time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    


