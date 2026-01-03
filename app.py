import streamlit as st
import yt_dlp
import nltk
from nltk.corpus import stopwords
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# --- GEREKLİ NLTK VERİLERİNİ İNDİR ---
# Streamlit her başladığında bunları kontrol etsin
nltk_packages = ['punkt', 'punkt_tab', 'stopwords']
for package in nltk_packages:
    try:
        nltk.data.find(f'tokenizers/{package}' if 'punkt' in package else f'corpora/{package}')
    except LookupError:
        nltk.download(package)

st.set_page_config(page_title="Varpilatör Web", page_icon="🤖", layout="wide")

# --- YAN MENÜ (AYARLAR) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    st.write("Özetin ne kadar kısa olacağını buradan seç:")
    ozet_cumle_sayisi = st.slider("Özet Cümle Sayısı", min_value=1, max_value=10, value=2)
    st.info(f"Seçilen: En önemli **{ozet_cumle_sayisi}** cümleyi getir.")

# --- ANA EKRAN ---
st.title("🤖 Varpilatör - Akıllı Özet")
st.write("Videoyu analiz eder, anahtar kelimeleri ve en vurucu cümleleri çıkarır.")

youtube_url = st.text_input("YouTube Video Linkini Yapıştır:")

if youtube_url:
    # Video ID'sini bulma
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
            st.success("Video bulundu! Analize hazır.")

    if st.button("Analiz Et"):
        with st.spinner("Video inceleniyor... (Bu işlem videonun uzunluğuna göre sürebilir)"):
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
                            # JSON3 formatı en iyisidir
                            json_url = None
                            for sub in subs_list:
                                if sub['ext'] == 'json3':
                                    json_url = sub['url']
                                    break
                            # Yoksa ilkini al
                            if not json_url and subs_list:
                                json_url = subs_list[0]['url']

                            if json_url:
                                import requests
                                response = requests.get(json_url)
                                data = response.json()
                                
                                # Metni birleştir
                                if 'events' in data:
                                    for event in data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    full_text += seg['utf8'] + " "
                
                # 2. ADIM: İŞLEME VE SUNMA
                if full_text:
                    # Dil tespiti ve Stop Words Yükleme
                    dil_nltk = "turkish" if target_lang == 'tr' else "english"
                    
                    parser = PlaintextParser.from_string(full_text, Tokenizer(dil_nltk))
                    summarizer = LsaSummarizer()
                    
                    # HATA ÇÖZÜMÜ BURADA:
                    # Stop words'leri sumy'den değil, nltk'den alıyoruz
                    try:
                        stop_words_list = stopwords.words(dil_nltk)
                        summarizer.stop_words = stop_words_list
                    except Exception as sw_error:
                        st.warning(f"Stop-words yüklenemedi, özet kalitesi düşebilir. Hata: {sw_error}")

                    # B) ÖZET
                    st.divider()
                    st.subheader(f"📌 Video Özeti ({ozet_cumle_sayisi} Cümle)")
                    
                    try:
                        summary = summarizer(parser.document, ozet_cumle_sayisi)
                        if len(summary) > 0:
                            for i, sentence in enumerate(summary, 1):
                                st.info(f"**{i}.** {str(sentence)}")
                        else:
                            st.warning("Metin özetlenemeyecek kadar kısa veya anlamsız.")
                    except Exception as sum_err:
                        st.error(f"Özetleme sırasında hata: {sum_err}")
                        
                    # C) TAM METİN
                    with st.expander("📄 Tam Metni İncele"):
                        st.text_area("Tüm Döküm", full_text, height=300)
                        
                else:
                    st.error("Metin çekilemedi. Altyazı kapalı olabilir.")

            except Exception as e:
                st.error("Bir hata oluştu.")
                st.write(f"Hata detayı: {e}")
