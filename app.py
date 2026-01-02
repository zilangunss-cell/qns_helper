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
        # Video ID'sini linkten ayıklama
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in youtube_url:
            video_id = youtube_url.split("/")[-1]
        else:
            video_id = None

        if video_id:
            # Videoyu göster
            st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
            st.success(f"Video algılandı! ID: {video_id}")
            
            if st.button("Analiz Et / Metni Getir"):
                with st.spinner("Altyazılar çekiliyor..."):
                    try:
                        # YENİ YÖNTEM: list_transcripts kullanımı
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # Türkçe veya İngilizce altyazıyı bulmaya çalış (öncelik sırasına göre)
                        # 'find_transcript' hem manuel hem otomatik oluşturulmuşları arar
                        transcript = transcript_list.find_transcript(['tr', 'en'])
                        
                        # Veriyi çek
                        transcript_data = transcript.fetch()
                        
                        # Metne çevir
                        formatter = TextFormatter()
                        text_formatted = formatter.format_transcript(transcript_data)
                        
                        st.subheader("📝 Video Metni:")
                        st.text_area("Çıktı", text_formatted, height=300)
                        
                    except Exception as trans_error:
                        st.error("Altyazı bulunamadı veya çekilemedi.")
                        st.error(f"Detay: {trans_error}")

        else:
            st.warning("Lütfen geçerli bir YouTube linki yapıştır.")
                
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
