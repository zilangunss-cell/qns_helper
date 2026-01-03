import streamlit as st
import yt_dlp
import json

st.set_page_config(page_title="Varpilatör Web", page_icon="🤖", layout="centered")

st.title("🤖 Varpilatör - Güçlendirilmiş Mod")
st.write("Daha güçlü bir altyapı ile video metni çekiliyor.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    # Video ID'sini göstermelik alıyoruz (resim için)
    video_id = ""
    if "v=" in youtube_url:
        video_id = youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_url:
        video_id = youtube_url.split("/")[-1]
        
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

    if st.button("Metni Getir"):
        with st.spinner("YouTube engelleri aşılıyor ve metin çekiliyor..."):
            try:
                # yt-dlp ayarları (Sadece veri çeker, video indirmez)
                ydl_opts = {
                    'skip_download': True,      # Videoyu indirme
                    'writesubtitles': True,     # Altyazı bak
                    'writeautomaticsub': True,  # Otomatik altyazı bak
                    'subtitleslangs': ['tr', 'en'], # Türkçe veya İngilizce
                    'quiet': True,              # Gereksiz log verme
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    
                    # Altyazıları bulma mantığı
                    captions = info.get('automatic_captions') or info.get('subtitles')
                    
                    if captions:
                        # Önce Türkçe var mı bak, yoksa İngilizce
                        target_lang = 'tr' if 'tr' in captions else 'en'
                        
                        if target_lang in captions:
                            # En iyi formatı seç (genelde json3 formatı en temizidir)
                            subs_list = captions[target_lang]
                            json_url = None
                            for sub in subs_list:
                                if sub['ext'] == 'json3':
                                    json_url = sub['url']
                                    break
                            
                            # Eğer json3 bulamazsa ilkini al
                            if not json_url and subs_list:
                                json_url = subs_list[0]['url']

                            # Veriyi indirip metne çevirelim
                            if json_url:
                                import requests
                                response = requests.get(json_url)
                                data = response.json()
                                
                                full_text = ""
                                if 'events' in data:
                                    for event in data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    full_text += seg['utf8']
                                    
                                    st.subheader("📝 Video Metni:")
                                    st.text_area("Sonuç", full_text, height=300)
                                    st.success("Başarıyla çekildi!")
                                else:
                                    st.warning("Altyazı formatı beklendiği gibi değil.")
                        else:
                            st.warning("Bu videoda Türkçe veya İngilizce altyazı bulunamadı.")
                    else:
                        st.error("Bu videonun altyazısı kapalı veya erişilemiyor.")

            except Exception as e:
                st.error("Bir hata oluştu.")
                st.info(f"Hata detayı: {e}")
