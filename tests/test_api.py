# tests/test_api.py - Modul F: uctan uca API testleri (demo modunda, dis servise gitmez)
# Calistirma: python -m unittest discover -s tests -v
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.services import ai_service as ai_modul  # noqa: E402


class SmartLeadTest(unittest.TestCase):
    def setUp(self):
        ai_modul.ai_service._son_hata.clear()
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DATABASE_URL"] = os.path.join(self.tmp.name, "test.db")
        import config
        config.TestingConfig.DATABASE_URL = os.environ["DATABASE_URL"]
        config.TestingConfig.ADMIN_TOKEN = ""
        self.app = create_app("testing")
        self.c = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_health(self):
        r = self.c.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["durum"], "ok")
        self.assertEqual(r.get_json()["veritabani"], "sqlite")

    def test_sayfalar(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("adminKey", r.get_data(as_text=True))   # site + canli dashboard
        r = self.c.get("/dashboard")
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/#dashboard"))
        self.assertEqual(self.c.get("/panel").status_code, 200)

    def test_sohbet_bos_mesaj_400(self):
        r = self.c.post("/api/sohbet", json={"mesaj": "  "})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["basari"])

    def test_sohbet_demo_modu(self):
        r = self.c.post("/api/sohbet", json={"mesaj": "Pro paket nedir?"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("demo", r.get_json()["cevap"])

    def test_sohbet_groq_hatasi_503(self):
        self.app.config["GROQ_API_KEY"] = "gsk_test"
        with mock.patch.object(ai_modul.requests, "post", side_effect=ai_modul.requests.ConnectionError("yok")):
            r = self.c.post("/api/sohbet", json={"mesaj": "Merhaba"})
        self.assertEqual(r.status_code, 503)
        self.assertFalse(r.get_json()["basari"])

    def test_sohbet_groq_basarili(self):
        self.app.config["GROQ_API_KEY"] = "gsk_test"
        sahte = mock.Mock()
        sahte.json.return_value = {"choices": [{"message": {"content": " Pro paket panel içerir. "}}]}
        sahte.raise_for_status.return_value = None
        with mock.patch.object(ai_modul.requests, "post", return_value=sahte) as cagri:
            r = self.c.post("/api/sohbet", json={"mesaj": "Pro?", "gecmis": [{"role": "system", "content": "x"}]})
        self.assertEqual(r.get_json()["cevap"], "Pro paket panel içerir.")
        gonderilen = cagri.call_args.kwargs["json"]["messages"]
        self.assertEqual([m["role"] for m in gonderilen], ["system", "user"])  # sahte system mesaji atlandi

    def test_sohbet_yedek_modele_gecer(self):
        self.app.config.update(NVIDIA_API_KEY="nvapi_test", GROQ_API_KEY="gsk_test")
        sahte = mock.Mock()
        sahte.json.return_value = {"choices": [{"message": {"content": "<think>x</think> Groq yanıtı"}}]}
        sahte.raise_for_status.return_value = None

        def cagri(url, **kw):
            if "nvidia" in url:
                raise ai_modul.requests.Timeout("yavas")
            return sahte
        with mock.patch.object(ai_modul.requests, "post", side_effect=cagri) as c:
            r = self.c.post("/api/sohbet", json={"mesaj": "Merhaba"})
        self.assertEqual(r.get_json()["cevap"], "Groq yanıtı")
        denenen = [k.kwargs["json"]["model"] for k in c.call_args_list]
        self.assertEqual(denenen, ["deepseek-ai/deepseek-v4.1-flash", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"])

    def test_lead_kaydet_ve_listele(self):
        r = self.c.post("/api/leads", json={"isim": "Mehmet Aydın", "telefon": "0532 123 45 27",
                                             "hayvan_sayisi": "120", "mesaj": "Pro teklif"})
        self.assertEqual(r.status_code, 201)
        liste = self.c.get("/api/leads").get_json()
        self.assertEqual(liste["toplam"], 1)
        self.assertEqual(liste["leadler"][0]["hayvan_sayisi"], 120)

    def test_lead_dogrulama(self):
        for govde in ({"isim": "", "telefon": "05321234567"},
                      {"isim": "Ali", "telefon": "abc"},
                      {"isim": "Ali", "telefon": "05321234567", "hayvan_sayisi": "çok"},
                      {"isim": "Ali", "telefon": "05321234567", "hayvan_sayisi": -5}):
            self.assertEqual(self.c.post("/api/leads", json=govde).status_code, 400, govde)

    def test_sql_injection_veri_olarak_saklanir(self):
        kotu = "x'); DROP TABLE leads; --"
        self.c.post("/api/leads", json={"isim": kotu, "telefon": "05321234567"})
        liste = self.c.get("/api/leads").get_json()
        self.assertEqual(liste["leadler"][0]["isim"], kotu)

    def test_admin_token(self):
        self.app.config["ADMIN_TOKEN"] = "gizli"
        self.assertEqual(self.c.get("/api/leads").status_code, 401)
        self.assertEqual(self.c.get("/api/leads", headers={"X-Admin-Token": "yanlis"}).status_code, 401)
        self.assertEqual(self.c.get("/api/leads", headers={"X-Admin-Token": "gizli"}).status_code, 200)

    def test_admin_giris(self):
        self.app.config["ADMIN_TOKEN"] = "gizli"
        self.assertEqual(self.c.post("/api/admin/giris", headers={"X-Admin-Token": "yanlis"}).status_code, 401)
        r = self.c.post("/api/admin/giris", headers={"X-Admin-Token": "gizli"})
        self.assertTrue(r.get_json()["basari"])

    def test_uretimde_anahtarsiz_liste_kapali(self):
        self.app.config.update(TESTING=False, DEBUG=False, ADMIN_TOKEN="")
        self.assertEqual(self.c.get("/api/leads").status_code, 503)

    def test_varsayilan_mod_uretim(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FLASK_ENV", None)
            app = create_app()
        self.assertFalse(app.config["DEBUG"])
        self.assertFalse(app.config["TESTING"])

    def test_postgres_sorgu_cevirisi(self):
        from app import database
        with self.app.app_context():
            self.app.config["DATABASE_URL"] = "postgresql://k:s@host/db"
            self.assertEqual(database._sql("VALUES (?, ?)"), "VALUES (%s, %s)")
            self.app.config["DATABASE_URL"] = "data/x.db"
            self.assertEqual(database._sql("VALUES (?, ?)"), "VALUES (?, ?)")

    def test_paket_mesaja_eklenir(self):
        self.c.post("/api/leads", json={"isim": "Ali", "telefon": "05321234567", "paket": "Pro", "mesaj": "Bergama"})
        self.c.post("/api/leads", json={"isim": "Veli", "telefon": "05321234568", "paket": "Henüz karar vermedim"})
        mesajlar = {l["isim"]: l["mesaj"] for l in self.c.get("/api/leads").get_json()["leadler"]}
        self.assertEqual(mesajlar["Ali"], "[Paket: Pro] Bergama")
        self.assertIsNone(mesajlar["Veli"])

    def test_kvkk_onayi_ve_kaynak_kaydedilir(self):
        self.c.post("/api/leads", json={"isim": "Ali", "telefon": "05321234567",
                                        "kvkk": True, "kaynak": "iletisim-formu"})
        self.c.post("/api/leads", json={"isim": "Veli", "telefon": "05321234568"})
        kayitlar = {l["isim"]: l for l in self.c.get("/api/leads").get_json()["leadler"]}
        self.assertIs(kayitlar["Ali"]["kvkk_onay"], True)
        self.assertEqual(kayitlar["Ali"]["kaynak"], "iletisim-formu")
        self.assertIs(kayitlar["Veli"]["kvkk_onay"], False)      # onay gelmezse False kalir
        self.assertEqual(kayitlar["Veli"]["kaynak"], "bilinmiyor")

    def test_eski_tabloya_eksik_kolonlar_eklenir(self):
        """Tablo kvkk_onay/kaynak kolonlari olmadan olusmussa init_db onlari tamamlar."""
        import sqlite3
        yol = os.path.join(self.tmp.name, "eski.db")
        eski = sqlite3.connect(yol)
        eski.executescript("CREATE TABLE leads (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                           " isim TEXT NOT NULL, telefon TEXT NOT NULL, hayvan_sayisi INTEGER,"
                           " mesaj TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        eski.execute("INSERT INTO leads (isim, telefon) VALUES ('Eski', '05321234569')")
        eski.commit()
        eski.close()

        import config
        config.TestingConfig.DATABASE_URL = yol
        c = create_app("testing").test_client()
        self.assertEqual(c.post("/api/leads", json={"isim": "Yeni", "telefon": "05321234567",
                                                    "kvkk": True}).status_code, 201)
        kayitlar = {l["isim"]: l for l in c.get("/api/leads").get_json()["leadler"]}
        self.assertEqual(set(kayitlar), {"Eski", "Yeni"})        # eski kayit korunur
        self.assertIs(kayitlar["Yeni"]["kvkk_onay"], True)
        self.assertIsNone(kayitlar["Eski"]["kaynak"])


if __name__ == "__main__":
    unittest.main()
