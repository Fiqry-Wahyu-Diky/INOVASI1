import streamlit as st
import cv2
import pytesseract
import pandas as pd
import re
import numpy as np

st.title("OCR Extract & Parse Saldo Bank dari Gambar")

# Upload file gambar
uploaded_file = st.file_uploader("Upload gambar (jpg/png/jpeg)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Baca file yang diupload sebagai bytes
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)

    # Decode ke format gambar OpenCV
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    st.image(img, caption=f'Gambar: {uploaded_file.name}', use_column_width=True)

    # OCR dengan pytesseract
    text = pytesseract.image_to_string(gray)

    # Parsing teks hasil OCR
    lines = text.strip().split('\n')
    list_bank = ['JATIM', 'BCA', 'BCA']  # Bisa kamu ganti atau buat dinamis
    data_upi, bank_idx = [], 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.search(r'\d{1,3}(?:\.\d{3})+,\d{2}', line):
            numbers = re.findall(r'\d{1,3}(?:\.\d{3})+,\d{2}', line)
            rekening = re.findall(r'\d{6,}', line)
            nama = line.split(rekening[0])[0].strip().replace('|', '').replace('[', '').replace(']',
                                                                                                '') if rekening else ''
            bank = list_bank[bank_idx] if bank_idx < len(list_bank) else 'BANK LAIN'
            data_upi.append({
                'Bank': bank,
                'Nama Rekening': nama,
                'No. Rekening': rekening[0] if rekening else '',
                'Saldo Bank': numbers[0] if numbers else '',
                'Saldo Acc': numbers[1] if len(numbers) > 1 else ''
            })
            bank_idx += 1

    # Buat DataFrame & bersihkan saldo
    df_upi = pd.DataFrame(data_upi)
    if not df_upi.empty:
        df_upi['Saldo Bank'] = df_upi['Saldo Bank'].str.replace('.', '', regex=False)
        st.subheader("Hasil Parsing Data:")
        st.dataframe(df_upi)
    else:
        st.warning("Tidak ditemukan data yang cocok pada gambar.")

