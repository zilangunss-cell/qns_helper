import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

st.set_page_config(page_title="Varpilatör", page_icon="🧠", layout="wide")

# --- YAN MENÜ: API KEY GİRİŞİ ---
with st.sidebar:
    st.header("🔑 Giriş")
    st.write("Uygulamayı kullanmak için OpenAI API anahtarını girmen gerekir.")
    
    user_api_key = st.text_input("OpenAI API Key:", type="password", placeholder="sk-...")
    
    st.divider()
    st.info("💡 **Not:** Bu anahtar hiçbir yere kaydedilmez. Sayfayı yenilediğinde silinir.")
    st.markdown("[API Key Nereden Alınır?](https://platform.openai.com/api-keys)")

# --- ANA EKRAN ---
st.title("🧠 Varpilatör - Güvenli Mod")
st.write("Senin anahtarın, senin kontrolün. YouTube videosunu yapıştır ve özeti al.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    # Video ID Çıkarma
    video_id = ""
    if "v=" in youtube_url:
        video_id = youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_url:
        video_id = youtube_url.split("/")[-1]
        
    if video_id:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
        with col2:
            st.success("Video algılandı.")

    # Buton
    if st.button("🚀 AI ile Analiz Et"):
        if not user_api_key:
            st.error("⚠️ Lütfen önce sol menüden API Key'inizi girin!")
            st.stop()
        elif not user_api_key.startswith("sk-"):
            st.warning("⚠️ Girdiğiniz API Key hatalı görünüyor. 'sk-' ile başlamalı.")
            st.stop()
        else:
            # --- İŞLEMLER ---
            with st.spinner("⏳ 1. Video metni çekiliyor..."):
                full_text = ""
                try:
                    # BURASI DÜZELTİLDİ: Artık istek hatası vermez.
                    # Önce Türkçe, yoksa İngilizce altyazıyı dener.
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'tr-TR', 'en'])
                    
                    # Parçaları birleştir
                    for t in transcript:
                        full_text += t['text'] + " "
                        
                except Exception as e:
                    # Altyazı kapalıysa veya hata varsa
                    st.error("❌ Hata: Videonun altyazısı çekilemedi. Altyazı kapalı olabilir.")
                    st.error(f"Teknik Hata Detayı: {e}")
                    st.stop()

                if not full_text:
                    st.error("❌ Metin boş geldi.")
                    st.stop()

                # --- GPT İLE ÖZETLEME ---
                with st.spinner("🧠 2. Yapay Zeka özetliyor..."):
                    try:
                        client = OpenAI(api_key=user_api_key)
                        
                        prompt = f"""
                        Aşağıdaki video transkriptini incele.
                        Bana videonun ana konusunu, anlatılan teknikleri ve en önemli noktalarını 
                        TÜRKÇE maddeler halinde özetle.
                        
                        Metin:
                        {full_text[:15000]} 
                        """

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Sen yardımcı bir asistansın."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        
                        ozet = response.choices[0].message.content

                        st.divider()
                        st.subheader("✨ AI Özeti")
                        st.markdown(ozet)
                        
                        with st.expander("📄 Video Metnini Göster"):
                            st.text_area("Transcript", full_text, height=200)
                            
                    except Exception as e:
                        st.error(f"OpenAI hatası: {e}")
