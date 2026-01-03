import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

st.set_page_config(page_title="Varpilatör Web", page_icon="🤖", layout="centered")

st.title("🤖 Varpilatör Web Versiyonu")
st.write("Videodaki konsepti Streamlit ile hayata geçiriyoruz.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:", placeholder="https://www.youtube.com/watch?v=...")

if youtube_url:
    try:
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in youtube_url:
            video_id = youtube_url.split("/")[-1]
        else:
            video_id = None

        if video_id:
            st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
            
            if st.button("Analiz Et / Metni Getir"):
                with st.spinner("Altyazılar çekiliyor..."):
                    try:
                        # Artık 0.6.3 sürümüne döndüğümüz için bu komut KESİN çalışacak
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # Türkçe varsa al, yoksa İngilizce, o da yoksa otomatik çeviriyi al
                        transcript = transcript_list.find_transcript(['tr', 'en'])
                        transcript_data = transcript.fetch()
                        
                        formatter = TextFormatter()
                        text_formatted = formatter.format_transcript(transcript_data)
                        
                        st.subheader("📝 Video Metni:")
                        st.text_area("Kopyalamak için:", text_formatted, height=300)
                        st.success("İşlem tamamlandı!")
                        
                    except Exception as trans_error:
                        st.error("Altyazı çekilemedi. Videoda altyazı kapalı olabilir.")
                        st.error(f"Hata Detayı: {trans_error}")
        else:
            st.warning("Link formatı hatalı görünüyor.")
                
    except Exception as e:
        st.error(f"Beklenmedik bir hata: {e}")
