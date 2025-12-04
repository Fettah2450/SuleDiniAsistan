import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai.errors import APIError 

# Telegram Token ve Gemini Key'i doğrudan koda gömüyoruz (eğer config.py kullanmıyorsak)
# Kendi doğru anahtarlarınızı buraya yapıştırın:
TELEGRAM_BOT_TOKEN = "8044876827:AAHGWWTEqaVL79HLXnf_W-nJLwmtSYslaPs"
GEMINI_API_KEY = "AIzaSyAmidYtGrfHh5k1qxlZkAoQM0a-x59F0Ng" 

# Railway, port numarasını bir Environment Variable (Ortam Değişkeni) olarak verir
# Eğer Railway'de çalışıyorsak PORT ve WEBHOOK_URL'i alacağız.
PORT = int(os.environ.get('PORT', '8080')) 
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'YOUR_RAILWAY_APP_URL') # Bu Railway tarafından otomatik ayarlanır

# Logging ayarları
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Eğer token veya API anahtarı yoksa programı durdur
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    print("HATA: TOKEN VE API KEY ALANLARI BOŞ BIRAKILMIŞ!")
    exit()

# Gemini API İstemcisini Başlat
try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    model = 'gemini-2.5-flash'
    system_instruction = "Sen, dini konularda kullanıcılara yardımcı olan bir yapay zekasın..." # (Kısaltıldı)
except Exception as e:
    logging.error(f"HATA: Yapay zeka servisi başlatılamadı. {e}")
    exit()

# ----------- KOMUT İŞLEYİCİLERİ -----------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Selamun aleyküm! Ben **Şule Yapay Zekayım**. Nasıl yardımcı olabilirim?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # ... (Kimlik kontrol kodu burada)
    
    # 2. Yapay Zeka ile cevap verme
    try:
        response = gemini_client.models.generate_content(
            model=model,
            contents=user_message,
            config={"system_instruction": system_instruction}
        )
        await update.message.reply_text(response.text)
        
    except APIError as e:
        logging.error(f"Gemini API Hatası: {e}")
        await update.message.reply_text("Üzgünüm, şu anda yapay zeka servisimizden cevap alamıyorum.")
    except Exception as e:
        logging.error(f"Genel Hata: {e}")
        await update.message.reply_text("Bir hata oluştu.")


# ----------- ANA FONKSİYON -----------

def main():
    """Botu webhook ile çalıştıran ana işlev"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook'u Ayarlama
    # Railway, WEBHOOK_URL'i otomatik olarak tanımlar.
    
    # 1. Telegram'a webhook adresimizi bildir
    application.bot.set_webhook(url=WEBHOOK_URL)
    
    # 2. Web sunucusunu başlat
    print("--------------------------------------------------")
    print(f"BAŞARIYLA BAŞLATILDI: Şule Yapay Zeka botu {PORT} portunda çalışıyor!")
    print("--------------------------------------------------")
    
    # Uygulamayı başlat
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="", # Webhook endpoint'i boş bıraktık
        webhook_url=WEBHOOK_URL
    )


if __name__ == '__main__':
    main()
