import os
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Bikin judul
st.title("💰 Chatbot AI Pengelola Keuangan Rumah Tangga")
st.markdown("Saya adalah asisten AI Anda untuk membantu mengelola, menganalisis, dan memberikan saran tentang anggaran bulanan rumah tangga Anda.")

# --- Bagian API Key ---
# Cek apakah API key sudah ada
if "GOOGLE_API_KEY" not in os.environ:
    # Jika belum, minta user buat masukin API key
    google_api_key = st.text_input("Google API Key", type="password")
    # User harus klik Start untuk save API key
    start_button = st.button("Mulai Chatbot")
    if start_button and google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.rerun()
    # Jangan tampilkan chat dulu kalau belum pencet start atau key kosong
    st.stop()

# Inisiasi client LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash") # Model yang lebih baru dan cepat

# --- System Message Awal (Context Keuangan) ---

# Tentukan instruksi spesifik untuk AI Pengelola Keuangan
FINANCE_SYSTEM_INSTRUCTION = (
    "Anda adalah Asisten AI Pengelola Keuangan Rumah Tangga yang profesional dan analitis. "
    "Tugas Anda adalah: "
    "1. Menganalisis data keuangan (pendapatan, pengeluaran, tabungan) yang diberikan oleh pengguna. "
    "2. Memberikan saran dan tips yang realistis untuk penghematan atau investasi. "
    "3. Membantu pengguna melacak anggaran dan mengidentifikasi area masalah. "
    "4. Bersikap suportif, lugas, dan berikan jawaban yang terstruktur (misalnya, dalam bentuk poin atau tabel). "
    "Contoh interaksi: Jika pengguna menyebutkan 'Pendapatan Rp 10.000.000 dan pengeluaran makan Rp 3.000.000', "
    "Anda harus menghitung persentase pengeluaran makan dan memberikan saran spesifik."
)

# Cek apakah data sebelumnya ttg message history sudah ada
if "messages_history" not in st.session_state:
    # Jika belum, bikin datanya, isinya hanya system message dulu, dengan instruksi keuangan sebagai context
    st.session_state["messages_history"] = [
        SystemMessage(content=FINANCE_SYSTEM_INSTRUCTION)
    ]

# Jika messages_history sudah ada, tinggal di load aja
messages_history = st.session_state["messages_history"]

# --- Tampilkan Chat History ---
for message in messages_history:
    # Tdk perlu tampilkan system message
    if type(message) is SystemMessage:
        continue
    # Pilih role, apakah user/AI
    role = "User" if type(message) is HumanMessage else "AI"
    # Tampikan chatnya!
    with st.chat_message(role):
        st.markdown(message.content)

# --- Proses Input dan Respon Chat ---

# Baca prompt terbaru dari user
prompt = st.chat_input("Contoh: Gaji bulan ini Rp 12.000.000. Pengeluaran wajib Rp 5.000.000, cicilan Rp 3.000.000, tabungan Rp 1.000.000. Berapa sisa dana untuk kebutuhan lain?")
if not prompt:
    st.stop()

# 1. Tampilkan prompt user
with st.chat_message("User"):
    st.markdown(prompt)

# 2. Masukin prompt ke message history, dan kirim ke LLM
messages_history.append(HumanMessage(content=prompt))

# Panggil LLM
with st.spinner("AI sedang menganalisis keuangan Anda..."):
    response = llm.invoke(messages_history)

# 3. Simpan jawaban LLM ke message history
messages_history.append(response)

# 4. Tampilkan langsung jawaban LLM
with st.chat_message("AI"):
    st.markdown(response.content)

# Simpan history ke session state setelah update
st.session_state["messages_history"] = messages_history