# app/services/ai_service.py - Dijital Coban SmartLead AI
# Modul C: yapay zeka cagrilari SADECE burada. Flask rotasi ve veritabani bilmez.
import requests
from flask import current_app

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GECMIS_LIMITI = 10          # modele gonderilen en fazla onceki mesaj
MESAJ_LIMITI = 1000         # tek mesajda en fazla karakter
DEMO_YANITI = ("Şu an demo modunda çalışıyorum (yapay zekâ anahtarı tanımlı değil). "
               "Paketlerimiz Lite, Pro ve Platinum'dur. Teklif için adınızı, telefonunuzu ve "
               "hayvan sayınızı bırakırsanız ekibimiz size dönüş yapar.")


class AIServiceError(Exception):
    """Yapay zeka servisine ulasilamadiginda firlatilir; rota bunu 503'e cevirir."""


class AIService:
    def yanit_uret(self, mesaj, gecmis=None):
        """Saglayiciya gore yaniti uretir. Anahtar yoksa demo yaniti doner."""
        ayar = current_app.config
        if not ayar.get("GROQ_API_KEY"):
            return DEMO_YANITI
        saglayici = ayar.get("AI_PROVIDER", "groq").lower()
        if saglayici != "groq":
            raise AIServiceError(f"Desteklenmeyen yapay zekâ sağlayıcısı: {saglayici}")
        return self._groq_cagir(self._mesajlari_hazirla(mesaj, gecmis))

    def _mesajlari_hazirla(self, mesaj, gecmis):
        """Sistem talimati + son gecmis + yeni mesaj. Gecersiz gecmis ogeleri atlanir."""
        mesajlar = [{"role": "system", "content": current_app.config["BUSINESS_CONTEXT"]}]
        for oge in (gecmis or [])[-GECMIS_LIMITI:]:
            if (isinstance(oge, dict) and oge.get("role") in ("user", "assistant")
                    and isinstance(oge.get("content"), str)):
                mesajlar.append({"role": oge["role"], "content": oge["content"][:MESAJ_LIMITI]})
        mesajlar.append({"role": "user", "content": mesaj[:MESAJ_LIMITI]})
        return mesajlar

    def _groq_cagir(self, mesajlar):
        ayar = current_app.config
        try:
            yanit = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {ayar['GROQ_API_KEY']}"},
                json={"model": ayar["GROQ_MODEL"], "messages": mesajlar,
                      "temperature": 0.4, "max_tokens": 400},
                timeout=ayar.get("AI_TIMEOUT", 20),
            )
            yanit.raise_for_status()
            return yanit.json()["choices"][0]["message"]["content"].strip()
        except (requests.RequestException, KeyError, IndexError, ValueError) as hata:
            current_app.logger.warning("Groq hatasi: %s", hata)
            raise AIServiceError("Asistan şu an yanıt veremiyor, lütfen biraz sonra tekrar deneyin.") from hata


ai_service = AIService()
