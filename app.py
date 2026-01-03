import streamlit as st
import yt_dlp
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# NLTK için gerekli paketleri indir (Özetleme için şart)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

st.set_page_config(page_title="Varpilatör Web", page_icon="🤖", layout="centered")

st.title("🤖 Varpilatör - Özetleyici Modu")
st.write("Video metnini çeker ve sizin için özetler.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    # Video ID'sini göstermelik alıyoruz
    video_id = ""
    if "v=" in youtube_url:
        video_id = youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_url:
        video_id = youtube_url.split("/")[-1]
        
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

    if st.button("Analiz Et ve Özetle"):
        with st.spinner("Video inceleniyor ve özet çıkarılıyor..."):
            try:
                # 1. ADIM: METNİ ÇEKME (yt-dlp)
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
                            # En temiz formatı (json3) bulmaya çalış
                            for sub in subs_list:
                                if sub['ext'] == 'json3':
                                    json_url = sub['url']
                                    break
                            if not json_url and subs_list:
                                json_url = subs_list[0]['url']

                            if json_url:
                                import requests
                                response = requests.get(json_url)
                                data = response.json()
                                
                                if 'events' in data:
                                    for event in data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    full_text += seg['utf8'] + " "
                
                # 2. ADIM: ÖZETLEME VE GÖSTERME
                if full_text:
                    # A) ÖZET KISMI
                    st.success("✅ İşlem Başarılı!")
                    st.subheader("📌 Video Özeti")
                    
                    # Sumy kütüphanesi ile özetleme
                    try:
                        parser = PlaintextParser.from_string(full_text, Tokenizer("turkish"))
                        summarizer = LsaSummarizer()
                        # En önemli 3 cümleyi seç
                        summary = summarizer(parser.document, 3) 
                        
                        ozet_metni = ""
                        for sentence in summary:
                            ozet_metni += f"- {str(sentence)}\n"
                        
                        st.info(ozet_metni)
                        
                    except Exception as sum_err:
                        st.warning("Özet çıkarılamadı, sadece tam metin gösteriliyor.")
                    
                    # B) TAM METİN KISMI
                    with st.expander("📄 Tam Video Metnini Görmek İçin Tıkla"):
                        st.text_area("Tüm Metin", full_text, height=400)
                        
                else:
                    st.error("Metin çekilemedi veya video dili desteklenmiyor.")

            except Exception as e:
                st.error("Bir hata oluştu.")
                st.write(f"Hata detayı: {e}")
