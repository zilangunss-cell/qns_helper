def transcribe_with_local_whisper(video_url):
    """
    Ücretsiz yerel Whisper modeli ile sesi yazıya döker.
    """
    # URL temizleme
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
    else:
        return None, "Geçersiz YouTube linki."

    audio_file = f"{video_id}.mp3"

    # --- KRİTİK AYARLAR (YouTube Engelini Aşmak İçin) ---
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
        'nocheckcertificate': True, # SSL hatalarını yoksay
        'geo_bypass': True,         # Coğrafi engelleri aşmayı dene
        
        # Tarayıcı taklidi yapan başlıklar:
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.youtube.com/',
        }
    }
    
    status_text = st.empty()
    status_text.info("📥 Video sesi indiriliyor (Bot koruması aşılıyor)...")
    
    try:
        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
    except Exception as e:
        # Eğer hala hata veriyorsa temizlik yap ve hatayı dön
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None, f"Ses indirme hatası (YouTube engeli): {e}"

    # 2. Whisper ile Yerel Olarak Çevir
    status_text.info("🤖 Yapay Zeka sesi dinliyor (Bu işlem videonun uzunluğuna göre zaman alır)...")
    
    try:
        model = load_whisper_model()
        result = model.transcribe(audio_file)
        text = result["text"]
        
        # Temizlik
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        status_text.empty()
        return text, None
        
    except Exception as e:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None, f"Whisper işlem hatası: {e}"
