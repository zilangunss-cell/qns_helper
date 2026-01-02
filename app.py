import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Sayfa Ayarları
st.set_page_config(page_title="Varpilatör Web", page_icon="🤖", layout="centered")

# Başlık
st.title("🤖 Varpilatör Web Versiyonu")
st.write("Videodaki konsepti Streamlit ile hayata geçiriyoruz.")

# Kullanıcıdan Link Alma
youtube_url = st.text_input("YouTube Video Linkini Yapıştır:", placeholder="https://www.youtube.com/watch?v=...")

if youtube_url:
    try:
        # Video ID'sini linkten ayıklama basit yöntemi
        video_id = youtube_url.split("v=")[1].split("&")[0]
        
        # Videoyu göster
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
        st.success(f"Video algılandı! ID: {video_id}")
        
        if st.button("Analiz Et / Metni Getir"):
            with st.spinner("Altyazılar çekiliyor..."):
                # Transkript çekme işlemi (Varpilatör mantığı)
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
                formatter = TextFormatter()
                text_formatted = formatter.format_transcript(transcript)
                
                st.subheader("📝 Video Metni:")
                st.text_area("Çıktı", text_formatted, height=300)
                
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
        st.info("Lütfen geçerli bir YouTube linki girdiğinden emin ol.")
