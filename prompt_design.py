from groq import Groq  
import json
import re
from google import genai

# client_ubah_prompt = Groq(api_key="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")  # API UPI
# client_buat_pertanyaan = Groq(api_key="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")  # API Aziz
client_ubah_prompt = genai.Client(api_key="AIzaSyC8P5GhFiDfcu-wlyOsFjij9baCvLy1Bxo") # saitamaseenei
client_buat_pertanyaan = genai.Client(api_key="AIzaSyCacjouK67Zxxx9LjCoLmJls7p6OVm2V1s") # aziz.1012

def ubah_prompt(pertanyaan): 
    prompt_1 = f"""Tugas kamu adalah untuk melakkukan transformasi pertanyaan menjadi sebuah bentuk prompt yang optimal. Dimana prompt tersebut memiliki instruksi, context, input data, dan output indicator.

    ------------------------------------------------
    Pertanyaan: {pertanyaan}

    Contoh Transformasi:
    - Pertanyaan: 'Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?'
    - Optimal Prompt: 'Jelaskan apa yang menjadi faktor utama yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum. Berikan analisis terperinci mengenai pembahasan tersebut.
    Berikan jawaban yang detail: '"""

    prompt_2 = """\n Format Keluaran:
    Keluaran harus berupa objek JSON di mana setiap pertanyaan dipasangkan dengan pertanyaan optimal yang sesuai. Untuk setiap topik, cantumkan pertanyaan asli dan pertanyaan optimal yang telah diubah. Keluaran harus dalam bahasa Inggris. Jangan ubah bahasa key dari JSON keluaran.

    Format the outputs in JSON. Example:
    {
        "pertanyaan": "Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?",
        "optimal prompt": "Jelaskan apa yang menjadi faktor utama yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum. Berikan analisis terperinci mengenai pembahasan tersebut.  
        Berikan jawaban yang detail: "
    },
    

    
    }}"""

    full_prompt = prompt_1 + prompt_2

    # chat_completion = client_ubah_prompt.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": full_prompt,
    #         }
    #     ],
    #     temperature=0,
    #     model="meta-llama/llama-4-scout-17b-16e-instruct",
    # )
    # text = str(chat_completion.choices[0].message.content)
    response = client_ubah_prompt.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=full_prompt,
    )

    text = str(response.text)
    # Menentukan posisi awal dan akhir blok JSON
    start = text.find('{')
    end = text.rfind('}') + 1

    # Mengekstrak substring JSON
    json_str = text[start:end]

    # Mengonversi string JSON menjadi objek Python
    data = json.loads(json_str)
    return data['optimal prompt']

def buat_pertanyaan(pertanyaan, answer):
    prompt_1 = f"""Pertanyaan sebelum: {pertanyaan} 
    Jawaban: {answer}
    Buatlah 2-3 pertanyaan yang diajukan berdasarkan informasi yang diberikan dalam bahasa indonesia. Pertanyaan yang dibentuk haruslah relevan dengan informasi yang diberikan. Contoh pertanyaan yang dihasilkan berdasarkan jawaban dipisahkah oleh triple backticks.
    Jika ada jawaban seperti ini: "Sama-sama! Semoga harimu menyenangkan!😊" atau sejenisnya, maka gunakan contoh no 2.

    Lalu, jika ada jawaban seperti "Sama-sama! Semoga harimu menyenangkan!😊" atau sejenisnya, maka output yang dihasilakn adalah string kosong.

    JANGAN MEMBUAT PERTANYAAN YANG SAMA DENGAN PERTANYAAN SEBELUMNYA!

    contoh 1:
    ```
    Jawaban: "Prabowo Subianto menjadi sorotan publik dalam pemilihan umum karena latar belakang militernya yang kuat, posisi sebagai Ketua Umum Partai Gerindra, dan visinya yang nasionalis-populis. Dia dikenal karena keterlibatannya dalam beberapa pemilu sebelumnya, kontroversi seputar tuduhan pelanggaran hak asasi manusia, serta gaya komunikasinya yang lugas dan kadang emosional. Aliansi politik yang dibentuknya dan pesan-pesan yang menekankan kemandirian ekonomi serta perlindungan sumber daya alam Indonesia juga menambah perhatian terhadap kiprahnya dalam politik nasional."

    Maka pertanyaan yang dihasilkan adalah sebagai berikut:
    Pertanyaan: "Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?" 

    maka akan diubah menjadi bentuk yang lebih menjelaskan pertanyaan di atas seperti:
    prompt_pertanyaan: "Jelaskan apa yang menjadi faktor utama yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum. Berikan analisis terperinci mengenai pembahasan tersebut.
    Pertanyaan: Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?
    Berikan jawaban yang detail: "

    ```                                         

    Contoh 2:
    ```
    Jawaban: "Sama-sama! Jika ada pertanyaan lebih lanjut, jangan ragu untuk bertanya. Semoga harimu menyenangkan!😊"

    Maka pertanyaan yang dihasilkan adalah sebagai berikut:
    pertanyaan: Semoga harimu menyenangkan
    prompt: Semoga harimu menyenangkan

    Optional:
    Berikan greeting kepada penggunanya, tetapi dengan format pertanyaan dan prompt.
    ```

    Jika terdapat jawaban seperti "Sama-sama! Semoga harimu menyenangkan!😊" atau sejenisnya, jawab seperti contoh 2. """

    prompt_2 = """\n Format the outputs in JSON. Contoh:
    [
        {{
            "pertanyaan": "Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?",
            "prompt_pertanyaan": "Jelaskan apa yang menjadi faktor utama yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum. Berikan analisis terperinci mengenai pembahasan tersebut.
            <br>Pertanyaan: Apa yang membuat Prabowo menjadi sorotan publik dalam pemilihan umum?<br>
            Berikan jawaban yang detail: "    
        }},
        {{
            "pertanyaan": "Thank you!"
            "prompt_pertanyaan": "Thank you for helping"
        }}
        ...
    ]

    SELALU TAMPILKAN INI PADA OUTPUT JSON YANG DIHASILKAN JIKA CONTOH 1
    {{
        "pertanyaan": "Thank you!"
        "prompt_pertanyaan": "Thank you for helping"
    }}"""

    full_prompt = prompt_1 + prompt_2

    # chat_completion = client_buat_pertanyaan.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": full_prompt,
    #         }
    #     ],
    #     temperature=0,
    #     model="meta-llama/llama-4-scout-17b-16e-instruct",
    # )

    # # Ubah string ke list of dict
    # text = str(chat_completion.choices[0].message.content)
    response = client_buat_pertanyaan.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=full_prompt,
    )

    text = str(response.text)
    # Ambil array JSON dari string menggunakan regex
    match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)

    if match:
        json_array_str = match.group(0)
        data = json.loads(json_array_str)  # Ubah jadi list of dict
        return data  # Menampilkan seluruh array
    else:
        return "Array JSON tidak ditemukan."