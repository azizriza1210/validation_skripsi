from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from save_chroma import save_to_chroma, rag
from prompt_design import ubah_prompt, buat_pertanyaan
from openpyxl import Workbook, load_workbook
import os

# Inisialisasi collection di luar fungsi app factory
# Ini memastikan fungsi save_to_chroma() hanya dipanggil sekali
collection = save_to_chroma()

def create_app():
    # Inisialisasi Flask
    app = Flask(__name__)
    CORS(app)  # Agar bisa diakses dari frontend berbeda (seperteyi localhost:5173)

    # Inisialisasi Groq client
    client_rag = Groq(api_key="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")  # Ganti "key" dengan API key Anda

    # Model default GROQ
    GROQ_MODEL = "llama3-70b-8192"

    # Path file Excel
    EXCEL_FILE = "chat_log.xlsx"

    # Fungsi untuk menyimpan ke Excel
    def save_to_excel(prompt, response):
        if os.path.exists(EXCEL_FILE):
            wb = load_workbook(EXCEL_FILE)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Prompt", "Response"])  # Header
        
        ws.append([prompt, response])
        wb.save(EXCEL_FILE)

    @app.route("/chatbot/chat", methods=["POST"])
    def chatbot_chat():
        try:
            data = request.get_json(force=True)
            prompt = data.get("query")
            
            if not prompt:
                return jsonify({"error": "No query provided"}), 400
            
            # Ubah prompt menggunakan Groq
            optimal_prompt = ubah_prompt(prompt)
            print(f"Optimal Prompt: {optimal_prompt}")
            
            # Ambil data relevan dari RAG
            tweets = rag(collection, optimal_prompt)
            tweets_formatted = "\n".join(tweets) if tweets else "Tidak ada informasi yang relevan ditemukan."
            
            # Buat prompt untuk LLM
            input_prompt = f"""INPUT Informasi yang tersedia: {tweets_formatted} Pertanyaan: {prompt} OUTPUT Harus Gunakan Bahasa Indonesia. ANSWER:"""
            
            # Stream response dan gabung jadi satu string
            full_response = ""
            for response in client_rag.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": input_prompt}],
                temperature=0.1,
                stream=True,
            ):
                delta = response.choices[0].delta
                if delta.content:
                    full_response += delta.content
            
            # Buat pertanyaan baru berdasarkan jawaban
            new_questions = buat_pertanyaan(optimal_prompt, full_response)
            
            # Simpan log ke Excel
            save_to_excel(prompt, full_response)
            
            return jsonify({"answer": full_response, "questions": new_questions})
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

# Jalankan Flask
if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)