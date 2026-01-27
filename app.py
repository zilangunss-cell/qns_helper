import streamlit as st
import yt_dlp
import os
import whisper  # Ücretsiz yerel Whisper kütüphanesi
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

st.set_page_config(page_title="Varpilatör", page_icon="🧠", layout="wide")

# --- YAN MENÜ ---
with st.sidebar:
    st.header("🔑 Giriş")
    st.write("Özetleme (GPT) için OpenAI API anahtarını girmen gerekir.")
    st.caption("Not: Sesi yazıya dökme işlemi artık ÜCRETSİZ modelle yapılıyor!")
    user_api_key = st.text_input("OpenAI API Key:", type="password", placeholder="sk-...")

# --- FONKSİYONLAR ---

@st.cache_resource
def transcribe_with_local_whisper(video_url):
    """
    Ücretsiz yerel Whisper modeli ile sesi yazıya döker.
    """
    # URL'den ID çıkarma
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
    else:
        return None, "Geçersiz YouTube linki."

    audio_file = f"{video_id}.mp3"

    # --- YOUTUBE ENGELİNİ AŞAN YENİ AYARLAR ---
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_id, 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        
        # SİHİRLİ KISIM BURASI: Android istemci taklidi yapıyoruz
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # Android gibi davran
            }
        },
        
        # Ek başlıklar
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        }
    }
    
    status_text = st.empty()
    status_text.info("📥 Video sesi indiriliyor (Android modunda)...")
    
    try:
        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
    except Exception as e:
        # Temizlik
        if os.path.exists(audio_file):
            os.remove(audio_file)
        # Hata mesajını daha okunaklı döndür
        return None, f"YouTube Engeli (403): Sunucu IP'si bloklanmış olabilir. {e}"

    # 2. Whisper ile Çeviri
    status_text.info("🤖 Yapay Zeka sesi dinliyor...")
    
    try:
        model = load_whisper_model()
        result = model.transcribe(audio_file)
        text = result["text"]
        
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        status_text.empty()
        return text, None
        
    except Exception as e:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None, f"Whisper hatası: {e}"

# --- ANA EKRAN ---
st.title("🧠 Varpilatör - Tamamen Ücretsiz Transkript Modu")
st.write("Altyazısı olmayan videoları sunucu tabanlı yapay zeka ile çözer.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    video_id = ""
    if "v=" in youtube_url:
        video_id = youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_url:
        video_id = youtube_url.split("/")[-1]
        
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", width=300)

    if st.button("🚀 Analiz Et"):
        if not user_api_key or not user_api_key.startswith("sk-"):
            st.error("⚠️ Lütfen özetleme için API Key girin.")
            st.stop()

        full_text = ""
        
        # --- AŞAMA 1: YouTube Altyazısını Dene (En Hızlısı) ---
        with st.spinner("🔍 Altyazı kontrol ediliyor..."):
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'tr-TR', 'en'])
                for t in transcript_list:
                    full_text += t['text'] + " "
                st.success("✅ YouTube altyazısı bulundu!")
            except Exception:
                # Altyazı yoksa sessizce devam et
                pass
        
        # --- AŞAMA 2: Altyazı Yoksa Yerel Whisper Kullan (ÜCRETSİZ) ---
        if not full_text:
            st.warning("⚠️ Hazır altyazı yok. Ücretsiz AI motoru devreye giriyor...")
            
            # Bu işlem sunucuda yapılır, API parası gitmez.
            transcribed_text, error = transcribe_with_local_whisper(youtube_url)
            
            if error:
                st.error(error)
                st.stop()
            else:
                full_text = transcribed_text
                st.success("✅ Ses başarıyla metne çevrildi!")

        # --- AŞAMA 3: GPT ile Özetle (Sadece Burası API Harcar) ---
        if full_text:
            with st.spinner("🧠 Metin özetleniyor..."):
                try:
                    client = OpenAI(api_key=user_api_key)
                    prompt = f"""
                    Aşağıdaki metni incele.
                    Videonun ana konusunu, teknik detaylarını ve önemli noktalarını 
                    TÜRKÇE maddeler halinde özetle.
                    
                    Metin:
                    {full_text[:15000]}
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Sen uzman bir asistansın."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    st.divider()
                    st.subheader("✨ AI Özeti")
                    st.markdown(response.choices[0].message.content)
                    
                    with st.expander("📝 Metni Göster"):
                        st.text_area("Transkript", full_text, height=200)

                except Exception as e:
                    st.error(f"Özetleme hatası: {e}")
