import streamlit as st
from groq import Groq  
import pandas as pd
import os
from save_chroma import save_to_chroma, rag

# Gunakan caching untuk memastikan save_to_chroma hanya dijalankan sekali
@st.cache_resource
def load_chroma_collection():
    return save_to_chroma()

# Load Chroma collection hanya sekali
collection = load_chroma_collection()

# Initialize Groq client with your API key
client = Groq(api_key="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")

if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "meta-llama/llama-4-scout-17b-16e-instruct"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Menu navigasi
menu = st.sidebar.selectbox("Menu", ["Chatbot", "Logical Fallacy"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = []

# Clear chat history when switching menus
if "current_menu" not in st.session_state:
    st.session_state.current_menu = menu  # Initialize current menu state

if st.session_state.current_menu != menu:
    clear_chat_history()  # Clear messages when switching menus
    st.session_state.current_menu = menu  # Update current menu state

if menu == "Chatbot":
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Search for relevant tweets based on the user's question
        tweets = rag(collection, prompt)  # Use the RAG function to retrieve relevant data
        
        # Format the tweets into a readable string
        tweets_formatted = "\n".join(tweets) if tweets else "Tidak ada informasi yang relevan ditemukan."
        
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream of response with milliseconds delay
            for response in client.chat.completions.create(
                model=st.session_state["groq_model"],
                messages=[
                    {
                        "role": "user",
                        "content": f"""INPUT
Informasi yang tersedia: {tweets_formatted}
Pertanyaan: {prompt}
OUTPUT Harus Gunakan Bahasa Indonesia.
ANSWER:"""
                    }
                ],
                temperature=0.1,
                stream=True,  # Enable streaming response
            ):
                # Access the 'content' attribute directly from the delta object
                if response.choices[0].delta.content:
                    full_response += response.choices[0].delta.content
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            
            # Finalize the displayed response
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

elif menu == "Logical Fallacy":
    # Handle user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
         
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream of response with milliseconds delay
            for response in client.chat.completions.create(
                model=st.session_state["groq_model"],
                messages=[
                    {
                        "role": "user",
                        "content": f"""Lakukan identifikasi Logical Fallacy terhadap argumen yang akan diberikan. Berikut langkah langkahnya:
    Lingkup identifikasi logical fallacy yaitu antara Ad Hominem, Appeal to Common Belief, Strawman, Hasty Generalization. Sebagai informasi jika termasuk Ad Populum itu sama saja dengan Appeal to Common Belief, jika termasuk Faulty Generalization itu sama saja dengan Hasty Generalization. Jika memang tidak terjadi Logical Fallacy LANSUNG JAWAB "Tidak terjadi Logical Fallacy"!.
Jika sudah menentukan Logical Fallacy yang terjadi, berikan alasan mengapa Logical Fallacy tersebut terjadi dengan mengubah argument ke dalam Logical Form berikut:
1. Ad Hominem:
Person 1 is claiming Y.
Person 1 is a moron.
Therefore, Y is not true.
2. Appeal to Common Belief:
A lot of people believe X.
Therefore, X must be true.
3. Strawman:
Person 1 makes claim Y.
Person 2 restates person 1’s claim (in a distorted way).
Person 2 attacks the distorted version of the claim.
Therefore, claim Y is false
4. Hasty Generalization:
Sample S is taken from population P.
Sample S is a very small part of population P.
Conclusion C is drawn from sample S and applied to population P.

Jika sudah menentukan alasan Logical Fallacy yang terjadi berdasarkan Logical Form, lakukan perubahan pada argumen yang diberikan agar tidak terjadi Logical Fallacy dan berikan perubahan hanya pada kalimat yang mengandung logical fallacynya saja tidak mengubah keseluruhan.

Argumen: Teman saya baru-baru ini mengklaim bahwa seorang montir di bengkel tertentu menarik biaya lebih dari…
Jenis Logical Fallacy: Hasty Generalization
Logical Form:
Sample S adalah seorang montir bengkel yang menarik biaya lebih. 
Sample S adalah sebagian kecil dari populasi montir di bengkel tersebut. 
Kesimpulan C adalah bahwa menyarankan untuk tidak membawa kendaraan Anda ke bengkel tersebut guna mencegah…
Argument sebelum diperbaiki: Teman saya baru-baru ini mengklaim bahwa seorang montir di bengkel tertentu menarik 
biaya lebih dari yang seharusnya, dan bukti pada struknya tampaknya mendukung tuduhan tersebut. Oleh karena itu, 
saya menyarankan untuk tidak membawa kendaraan Anda ke sana guna mencegah Anda sendiri dikenakan biaya berlebih.
Argument yang sudah diperbaiki: Teman saya baru-baru ini mengklaim bahwa seorang montir di bengkel tertentu 
menarik biaya lebih dari yang seharusnya, dan bukti pada struknya tampaknya mendukung tuduhan tersebut. Jika 
Anda berencana untuk menggunakan jasa bengkel tersebut, saya sarankan untuk memastikan bahwa montir yang 
berbeda menangani kendaraan Anda atau meminta rincian biaya secara transparan sebelum pekerjaan dimulai.

Argument: {prompt}
Jenis Logical Fallacy:
Logical Form:
Argument sebelum diperbaiki:
Argument yang sudah diperbaiki:
"""
                    }
                ],
                temperature=0.1,
                stream=True,  # Enable streaming response
            ):
                # Access the 'content' attribute directly from the delta object
                if response.choices[0].delta.content:
                    full_response += response.choices[0].delta.content
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            
            # Finalize the displayed response
            message_placeholder.markdown(full_response)