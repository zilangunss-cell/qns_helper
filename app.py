import streamlit as st
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
import os

st.title("🕵️ Hata Dedektifi")

# 1. Kütüphane Nereden Yükleniyor?
st.write("### 1. Dosya Konumu")
try:
    st.code(f"Kütüphane şuradan çalışıyor:\n{youtube_transcript_api.__file__}")
except Exception as e:
    st.error(f"Dosya yolu bulunamadı: {e}")

# 2. İçinde Hangi Komutlar Var?
st.write("### 2. Kütüphane İçeriği")
try:
    # YouTubeTranscriptApi sınıfının içindeki özellikleri listele
    attributes = dir(YouTubeTranscriptApi)
    # Sadece bizim aradıklarımız var mı kontrol et
    methods = [m for m in attributes if "transcript" in m]
    st.write("Bulunan Metodlar:", methods)
    
    if 'list_transcripts' in attributes:
        st.success("✅ list_transcripts MEVCUT!")
    else:
        st.error("❌ list_transcripts MEVCUT DEĞİL!")
        
except Exception as e:
    st.error(f"Okunamadı: {e}")

# 3. Klasörde Çakışan Dosya Var mı?
st.write("### 3. Klasör Kontrolü")
st.write(os.listdir('.'))
