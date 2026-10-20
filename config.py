# config.py - Dijital Coban SmartLead AI
# Modul A: tum ayarlar .env dosyasindan okunur; is mantigi icermez.
import os

from dotenv import load_dotenv

load_dotenv()

# Yapay zekanin kisiligi. Ise ozel olan tek metin budur; diger katmanlar her is icin aynidir.
VARSAYILAN_BUSINESS_CONTEXT = """Sen Dijital Çoban – Akıllı Ahır Çözümleri'nin satış asistanısın.
Bergama/İzmir merkezli firmamız koyun yetiştiricilerine taşınabilir, modüler ve otomatik akıllı ahır kurar.

Paketler (her pakette taşınabilir modüler ahır, yerinde kurulum ve 1 yıl garanti vardır):
- Lite: otomatik yemleme, otomatik su ve otomatik gübre temizleme sistemi.
- Pro: Lite'taki her şey + yapay zekâ destekli TV/tablet izleme paneli (yem, su, gübre sistemlerinin
  anlık takibi, olağan dışı tüketim ve arıza uyarıları, ahırı uzaktan izleme).
- Platinum: Pro'daki her şey + sabitleme ve ilaçlama bölmesi + veteriner raporlu 50 baş başlangıç sürüsü.
  Çip tabanlı sağlık izleme "yakında" gelecektir; şu an satışta olduğunu söyleme.
Ahır modülerdir: modül eklenerek büyütülür, çıkarılarak küçültülür, arazi değişirse taşınır.
Bir modül yaklaşık 35 baş içindir; kesin modül sayısını keşif görüşmesinde ekip belirler.
Bakım paketi ayrıca satılır (3 ayda bir saha ziyareti, öncelikli servis). Ödeme taksitle veya altınla yapılabilir.
Ahır müşterilerine saman ve yoncada %5 indirim vardır.

Kurallar:
- Kibar, sade ve kısa Türkçe konuş. Çiftçiyle çiftçi gibi konuş, teknik terimleri açıkla.
- Fiyat sorulursa kesin rakam verme; teklif için ad, telefon ve hayvan sayısını iste.
- Hibe ve destekler hakkında yalnızca genel bilgi ver; onay garantisi verme, sonucun ilgili kuruma bağlı olduğunu söyle.
- Hayvan hastalığı, teşhis veya ilaç dozu hakkında tavsiye verme; veterinere yönlendir.
- Kimlik numarası, kart veya banka bilgisi isteme; kullanıcı paylaşırsa paylaşmamasını rica et.
- Bilmediğin bir konuda tahmin yürütme; ekibimizin dönüş yapacağını söyle.
- İletişim: +90 536 523 7959, dijitalcoban@rinnesoft.com"""


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gelistirme-anahtari-degistir")
    DATABASE_URL = os.environ.get("DATABASE_URL", "data/smartlead.db")
    # Yapay zeka zinciri: sirayla denenir, calismayan atlanir (bkz. app/services/ai_service.py)
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
    NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "deepseek-ai/deepseek-v4.1-flash")
    NVIDIA_API_KEY_2 = os.environ.get("NVIDIA_API_KEY_2", "")   # bossa NVIDIA_API_KEY kullanilir
    NVIDIA_MODEL_2 = os.environ.get("NVIDIA_MODEL_2", "openai/gpt-oss-20b")
    NVIDIA_TIMEOUT = int(os.environ.get("NVIDIA_TIMEOUT", "12"))
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_MODEL_2 = os.environ.get("GROQ_MODEL_2", "openai/gpt-oss-20b")
    AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "20"))
    # Wix site adresi; virgulle birden fazla adres yazilabilir
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]
    # Doluysa GET /api/leads icin X-Admin-Token basligi zorunlu olur
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
    BUSINESS_CONTEXT = os.environ.get("BUSINESS_CONTEXT", VARSAYILAN_BUSINESS_CONTEXT)
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    # testler demo modunda calisir, dis servise gitmez
    NVIDIA_API_KEY = ""
    NVIDIA_API_KEY_2 = ""
    GROQ_API_KEY = ""


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
