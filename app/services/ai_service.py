# app/services/ai_service.py - Dijital Coban SmartLead AI
# Modul C: yapay zeka cagrilari SADECE burada. Flask rotasi ve veritabani bilmez.
# Modeller sirayla denenir (NVIDIA DeepSeek -> NVIDIA gpt-oss -> Groq qwen -> Groq gpt-oss-20b);
# biri hata verir veya zaman asimina duserse siradakine gecilir.
import re
import time

import requests
from flask import current_app

URLLER = {
    "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}
GECMIS_LIMITI = 10          # modele gonderilen en fazla onceki mesaj
MESAJ_LIMITI = 1000         # tek mesajda en fazla karakter
MAX_TOKENS = 800            # dusunen (reasoning) modellere de yer kalsin
BEKLEME_SURESI = 120        # hata veren model bu kadar saniye zincirin sonuna atilir
DUSUNCE_DESENI = re.compile(r"<think>.*?</think>", re.DOTALL)
DEMO_YANITI = ("Şu an demo modunda çalışıyorum (yapay zekâ anahtarı tanımlı değil). "
               "Paketlerimiz Lite, Pro ve Platinum'dur. Teklif için adınızı, telefonunuzu ve "
               "hayvan sayınızı bırakırsanız ekibimiz size dönüş yapar.")


class AIServiceError(Exception):
    """Hicbir modele ulasilamadiginda firlatilir; rota bunu 503'e cevirir."""


class AIService:
    def __init__(self):
        self._son_hata = {}   # (saglayici, model) -> hatanin zamani

    def yanit_uret(self, mesaj, gecmis=None):
        """Zincirdeki ilk calisan modelin yanitini doner. Hic anahtar yoksa demo yaniti doner."""
        zincir = self._zincir()
        if not zincir:
            return DEMO_YANITI
        mesajlar = self._mesajlari_hazirla(mesaj, gecmis)
        # Yakin zamanda hata veren modeller sona alinir (siralama kararli, oncelik korunur)
        for saglayici, anahtar, model, sure in sorted(zincir, key=self._beklemede_mi):
            try:
                cevap = self._cagir(saglayici, anahtar, model, sure, mesajlar)
            except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as hata:
                current_app.logger.warning("%s/%s hatasi: %s", saglayici, model, hata)
                self._son_hata[(saglayici, model)] = time.monotonic()
                continue
            self._son_hata.pop((saglayici, model), None)
            current_app.logger.info("Yanit veren model: %s/%s", saglayici, model)
            return cevap
        raise AIServiceError("Asistan şu an yanıt veremiyor, lütfen biraz sonra tekrar deneyin.")

    def _zincir(self):
        """Ayarlardan deneme sirasini kurar; anahtari veya modeli bos olanlar atlanir."""
        a = current_app.config
        adaylar = [
            ("nvidia", a.get("NVIDIA_API_KEY"), a.get("NVIDIA_MODEL"), a.get("NVIDIA_TIMEOUT", 12)),
            ("nvidia", a.get("NVIDIA_API_KEY_2") or a.get("NVIDIA_API_KEY"), a.get("NVIDIA_MODEL_2"),
             a.get("NVIDIA_TIMEOUT", 12)),
            ("groq", a.get("GROQ_API_KEY"), a.get("GROQ_MODEL"), a.get("AI_TIMEOUT", 20)),
            ("groq", a.get("GROQ_API_KEY"), a.get("GROQ_MODEL_2"), a.get("AI_TIMEOUT", 20)),
        ]
        return [s for s in adaylar if s[1] and s[2]]

    def _beklemede_mi(self, secenek):
        zaman = self._son_hata.get((secenek[0], secenek[2]))
        return zaman is not None and time.monotonic() - zaman < BEKLEME_SURESI

    def _mesajlari_hazirla(self, mesaj, gecmis):
        """Sistem talimati + son gecmis + yeni mesaj. Gecersiz gecmis ogeleri atlanir."""
        mesajlar = [{"role": "system", "content": current_app.config["BUSINESS_CONTEXT"]}]
        for oge in (gecmis or [])[-GECMIS_LIMITI:]:
            if (isinstance(oge, dict) and oge.get("role") in ("user", "assistant")
                    and isinstance(oge.get("content"), str)):
                mesajlar.append({"role": oge["role"], "content": oge["content"][:MESAJ_LIMITI]})
        mesajlar.append({"role": "user", "content": mesaj[:MESAJ_LIMITI]})
        return mesajlar

    def _cagir(self, saglayici, anahtar, model, sure, mesajlar):
        yanit = requests.post(
            URLLER[saglayici],
            headers={"Authorization": f"Bearer {anahtar}"},
            json={"model": model, "messages": mesajlar, "temperature": 0.4, "max_tokens": MAX_TOKENS},
            timeout=sure,
        )
        yanit.raise_for_status()
        icerik = yanit.json()["choices"][0]["message"]["content"] or ""
        icerik = DUSUNCE_DESENI.sub("", icerik).strip()
        if not icerik:
            raise ValueError("bos yanit")
        return icerik


ai_service = AIService()
