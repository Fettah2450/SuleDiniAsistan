import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai.errors import APIError 

# ----------------------------------------------------------------------
# 1. API ANAHTARLARI VE AYARLAR
# ----------------------------------------------------------------------

# Lütfen bu alanları kendi doğru anahtarlarınızla doldurun.
TELEGRAM_BOT_TOKEN = "8044876827:AAHGWWTEqaVL79HLXnf_W-nJLwmtSYslaPs"
GEMINI_API_KEY = "AIzaSyAmidYtGrfHh5k1qxlZkAoQM0a-x59F0Ng" 

# Loglama ayarları (Railway'de hata takibi için)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Yapay Zeka Ayarları
try:
    # Key'in doğru çalıştığını daha önce görmüştük.
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    model = 'gemini-2.5-flash'
    # Sistem talimatı (Botun kimliği)
    system_instruction = (
        "Sen, insanlara İslam dini ve genel dini konularda yardımcı olan, "
        "bilgili ve nazik bir yapay zekasın. Cevapların kısa, öz ve saygılı olmalı. "
        "Dini olmayan veya tartışmalı konulara cevap verme."
    )
except Exception as e:
    logger.error(f"HATA: Yapay zeka servisi başlatılamadı. {e}")
    # Eğer key hatalıysa programı durdur
    exit()

# ----------- KOMUT İŞLEYİCİLERİ -----------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot /start komutunu aldığında çalışır."""
    await update.message.reply_text('Selamun aleyküm! Ben **Şule Yapay Zekayım**. Nasıl yardımcı olabilirim?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kullanıcıdan gelen tüm metin mesajlarını işler."""
    if not update.message.text:
        return

    user_message = update.message.text.lower()
    
    # Basit Kimlik Sorgusu Kontrolü (Gemini'ye gitmeden cevap verir)
    identity_keywords = ["kimsin", "nesin", "adın ne", "bot musun"]
    if any(keyword in user_message for keyword in identity_keywords):
        await update.message.reply_text('Ben **Şule Yapay Zekayım**. Amacım, dini konularda size yardımcı olmaktır.')
        return

    # Yapay Zeka ile cevap verme
    try:
        response = gemini_client.models.generate_content(
            model=model,
            contents=update.message.text, # Orijinal mesajı kullanıyoruz
            config={"system_instruction": system_instruction}
        )
        
        # Cevabı Telegram'a gönder
        await update.message.reply_text(response.text)
        
    except APIError as e:
        logger.error(f"Gemini API Hatası: {e}")
        await update.message.reply_text("Üzgünüm, şu anda yapay zeka servisimizden (Gemini) cevap alamıyorum. Lütfen daha sonra tekrar deneyin.")
    except Exception as e:
        logger.error(f"Genel Hata: {e}")
        await update.message.reply_text("Bir hata oluştu. Lütfen mesaj içeriğini veya komutları kontrol edin.")


# ----------- ANA FONKSİYON -----------

def main():
    """Botu çalıştıran ana işlev"""
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'ları kaydet
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("--------------------------------------------------")
    print("BAŞARIYLA BAŞLATILDI: Şule Yapay Zeka botu çalışıyor!")
    print("--------------------------------------------------")

    # Botu, Railway'e uygun basit Polling ile başlat
    # Bu metot, çökme hatası veren Webhook'un yerine kullanılır.
    application.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()
