import streamlit as st
import yt_dlp
import requests
from openai import OpenAI

st.set_page_config(page_title="Varpilatör AI", page_icon="🧠", layout="wide")

# --- YAN MENÜ: API KEY GİRİŞİ ---
with st.sidebar:
    st.header("🔑 Giriş")
    st.write("Uygulamayı kullanmak için OpenAI API anahtarını girmen gerekir.")
    
    # Şifre kutusu (type='password' olduğu için yazılanlar nokta nokta görünür)
    user_api_key = st.text_input("OpenAI API Key:", type="password", placeholder="sk-...")
    
    st.divider()
    st.info("💡 **Not:** Bu anahtar hiçbir yere kaydedilmez. Sayfayı yenilediğinde silinir.")
    st.markdown("[API Key Nereden Alınır?](https://platform.openai.com/api-keys)")

# --- ANA EKRAN ---
st.title("🧠 Varpilatör - Güvenli Mod")
st.write("Senin anahtarın, senin kontrolün. YouTube videosunu yapıştır ve özeti al.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    # Video ID ve Kapak Resmi
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
        # ÖNCE KONTROL: Kullanıcı anahtarı girdi mi?
        if not user_api_key:
            st.error("⚠️ Lütfen önce sol menüden API Key'inizi girin!")
            st.stop() # İşlemi burada durdur
            
        elif not user_api_key.startswith("sk-"):
            st.warning("⚠️ Girdiğiniz API Key hatalı görünüyor. 'sk-' ile başlamalı.")
            st.stop()

        else:
            # İşlemleri Başlat
            with st.spinner("⏳ 1. Video metni çekiliyor..."):
                try:
                    # --- 1. ADIM: METNİ ÇEKME (yt-dlp) ---
                    ydl_opts = {
                        'skip_download': True,
                        'writesubtitles': True,
                        'writeautomaticsub': True,
                        'subtitleslangs': ['tr', 'en'],
                        'quiet': True,
                    }

                    full_text = ""
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=False)
                        captions = info.get('automatic_captions') or info.get('subtitles')
                        
                        if captions:
                            target_lang = 'tr' if 'tr' in captions else 'en'
                            if target_lang in captions:
                                subs_list = captions[target_lang]
                                json_url = None
                                for sub in subs_list:
                                    if sub['ext'] == 'json3':
                                        json_url = sub['url']
                                        break
                                if not json_url and subs_list:
                                    json_url = subs_list[0]['url']

                                if json_url:
                                    response = requests.get(json_url)
                                    data = response.json()
                                    if 'events' in data:
                                        for event in data['events']:
                                            if 'segs' in event:
                                                for seg in event['segs']:
                                                    if 'utf8' in seg:
                                                        full_text += seg['utf8'] + " "
                    
                    if not full_text:
                        st.error("❌ Bu videonun altyazısı yok veya çekilemedi.")
                        st.stop()

                    # --- 2. ADIM: GPT İLE ÖZETLEME ---
                    with st.spinner("🧠 2. Yapay Zeka özetliyor..."):
                        
                        # Kullanıcının girdiği anahtarı kullanıyoruz
                        client = OpenAI(api_key=user_api_key)
                        
                        prompt = f"""
                        Aşağıdaki video transkriptini incele.
                        Bana videonun ana konusunu, anlatılan teknikleri ve en önemli noktalarını 
                        TÜRKÇE maddeler halinde özetle. Anlaşılır ve net ol.
                        
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

                        # SONUÇLARI GÖSTER
                        st.divider()
                        st.subheader("✨ AI Özeti")
                        st.markdown(ozet)
                        
                        with st.expander("📄 Video Metnini Göster"):
                            st.text_area("Transcript", full_text, height=200)

                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
