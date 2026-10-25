# app/routes.py - Dijital Coban SmartLead AI
# Modul D: istegi dogrular ve dogru katmana yonlendirir. SQL ve AI kodu yazmaz.
import hmac
import re

from flask import Blueprint, current_app, jsonify, redirect, render_template, request

from app import database
from app.services.ai_service import MESAJ_LIMITI, AIServiceError, ai_service

sayfa_bp = Blueprint("sayfa", __name__)
api_bp = Blueprint("api", __name__)

TELEFON_DESENI = re.compile(r"^\+?[0-9 ()-]{10,20}$")


def _hata(mesaj, kod):
    return jsonify({"basari": False, "hata": mesaj}), kod


@sayfa_bp.get("/")
def karsilama():
    return render_template("index.html")


@sayfa_bp.get("/dashboard")
def dashboard():
    # Asıl panel sitenin içindeki #dashboard bölümüdür
    return redirect("/#dashboard")


@sayfa_bp.get("/panel")
def yedek_panel():
    # Sade yedek yönetim paneli
    return render_template("dashboard.html")


@sayfa_bp.get("/form")
def iletisim_formu():
    # Wix'e iFrame ile gömülen "Bize Ulaşın" formu
    return render_template("form.html")


@api_bp.post("/sohbet")
def sohbet():
    veri = request.get_json(silent=True) or {}
    mesaj = str(veri.get("mesaj", "")).strip()
    gecmis = veri.get("gecmis", [])
    if not mesaj:
        return _hata("Mesaj boş olamaz.", 400)
    if len(mesaj) > MESAJ_LIMITI:
        return _hata(f"Mesaj en fazla {MESAJ_LIMITI} karakter olabilir.", 400)
    if not isinstance(gecmis, list):
        gecmis = []
    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)
    except AIServiceError as e:
        return _hata(str(e), 503)
    return jsonify({"basari": True, "cevap": cevap})


@api_bp.post("/leads")
def lead_kaydet():
    veri = request.get_json(silent=True) or {}
    isim = str(veri.get("isim", "")).strip()
    telefon = str(veri.get("telefon", "")).strip()
    mesaj = str(veri.get("mesaj", "") or "").strip()
    paket = str(veri.get("paket", "") or "").strip()
    if paket in ("Lite", "Pro", "Platinum"):
        mesaj = f"[Paket: {paket}] {mesaj}".strip()
    mesaj = mesaj[:MESAJ_LIMITI] or None
    hayvan = veri.get("hayvan_sayisi")
    kvkk_onay = bool(veri.get("kvkk"))
    kaynak = str(veri.get("kaynak", "") or "").strip()[:40] or "bilinmiyor"

    if not isim or not telefon:
        return _hata("İsim ve telefon zorunludur.", 400)
    if len(isim) > 100:
        return _hata("İsim en fazla 100 karakter olabilir.", 400)
    if not TELEFON_DESENI.match(telefon):
        return _hata("Telefon numarası geçerli değil.", 400)
    if hayvan in ("", None):
        hayvan = None
    else:
        try:
            hayvan = int(hayvan)
        except (TypeError, ValueError):
            return _hata("Hayvan sayısı sayı olmalıdır.", 400)
        if not 0 <= hayvan <= 100000:
            return _hata("Hayvan sayısı 0 ile 100000 arasında olmalıdır.", 400)

    lead_id = database.lead_ekle(isim, telefon, hayvan, mesaj, kvkk_onay, kaynak)
    return jsonify({"basari": True, "id": lead_id, "mesaj": "Talebiniz alındı, ekibimiz size dönüş yapacak."}), 201


def _admin_dogrula():
    """Yönetici anahtarını kontrol eder; sorun yoksa None, varsa hata yanıtı döner.
    Üretimde ADMIN_TOKEN tanımlı değilse liste tamamen kapalıdır (fail-closed)."""
    beklenen = current_app.config.get("ADMIN_TOKEN", "")
    if not beklenen:
        if current_app.config.get("DEBUG") or current_app.config.get("TESTING"):
            return None
        return _hata("Yönetici anahtarı sunucuda tanımlı değil (ADMIN_TOKEN).", 503)
    gelen = request.headers.get("X-Admin-Token", "")
    if not hmac.compare_digest(gelen.encode(), beklenen.encode()):
        return _hata("Yetkisiz erişim.", 401)
    return None


@api_bp.post("/admin/giris")
def admin_giris():
    """Dashboard giriş ekranı anahtarı burada doğrular."""
    hata = _admin_dogrula()
    return hata or jsonify({"basari": True})


@api_bp.get("/leads")
def lead_listele():
    hata = _admin_dogrula()
    if hata:
        return hata
    leadler = database.tum_leadler()
    return jsonify({"basari": True, "toplam": len(leadler), "leadler": leadler})
