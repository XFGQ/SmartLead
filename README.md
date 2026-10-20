# SmartLead AI - Dijital Coban Akilli Satis Asistani

Dijital Coban | Akilli Ahir Cozumleri icin ziyaretci sohbeti ve lead toplama sistemi.

## Mimari
- `config.py`: ayarlar (.env) + BUSINESS_CONTEXT
- `app/database.py`: SQLite (SQL sadece burada)
- `app/services/ai_service.py`: AI cagrilari (sadece burada): NVIDIA DeepSeek -> NVIDIA gpt-oss -> Groq qwen -> Groq gpt-oss-20b yedek zinciri, demo modu
- `app/routes.py`: HTTP rotalari (dogrulama + yonlendirme)
- `app/__init__.py`: create_app() fabrikasi + /health
- `wix_velo/`: Wix Studio sayfalarina yapistirilacak Velo kodlari

## Uc noktalar
| Metod | Yol | Aciklama |
|---|---|---|
| GET | `/`, `/dashboard` | Karsilama ve yonetim paneli |
| GET | `/health` | Canlilik kontrolu |
| POST | `/api/sohbet` | `{mesaj, gecmis}` -> `{basari, cevap}` |
| POST | `/api/leads` | `{isim, telefon, hayvan_sayisi, mesaj}` -> 201 |
| GET | `/api/leads` | `ADMIN_TOKEN` doluysa `X-Admin-Token` basligi gerekir |

## Calistirma
```
copy .env.example .env   # Linux/Mac: cp
docker compose up --build
```
veya venv ile: `pip install -r requirements.txt` ve `python run.py`. Tarayici: http://localhost:5000

## Test
```
python -m unittest discover -s tests -v
```

## Site ve yonetim paneli
- `/` : Dijital Coban sitesi (sohbet asistani + teklif formu canli API'ye bagli)
- `/dashboard` : `/#dashboard` bolumune yonlendirir. Yonetici anahtari ile giris yapilir;
  anahtar yalnizca tarayici oturumunda (sessionStorage) tutulur, sayfa koduna yazilmaz.
- `/panel` : sade yedek yonetim paneli

## Render
Build: `pip install -r requirements.txt` · Start: `gunicorn run:app` · Health: `/health`

Environment Variables:
| Anahtar | Deger |
|---|---|
| `FLASK_ENV` | `production` |
| `ADMIN_TOKEN` | uzun rastgele metin (dashboard giris anahtari) |
| `NVIDIA_API_KEY` | 1. NVIDIA anahtari (DeepSeek) |
| `NVIDIA_MODEL` | `deepseek-ai/deepseek-v4.1-flash` |
| `NVIDIA_API_KEY_2` | 2. NVIDIA anahtari (gpt-oss-20b) |
| `NVIDIA_MODEL_2` | `openai/gpt-oss-20b` |
| `GROQ_API_KEY` | Groq anahtari (son yedek) |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` |
| `GROQ_MODEL_2` | `openai/gpt-oss-20b` |
| `SECRET_KEY` | uzun rastgele metin |
| `DATABASE_URL` | Neon/Render PostgreSQL baglanti adresi (`postgresql://...`) — kalici veritabani |
| `CORS_ORIGINS` | `https://furkanduman1925.wixsite.com` |

`FLASK_ENV` verilmezse uygulama uretim modunda calisir. Uretimde `ADMIN_TOKEN` tanimli degilse `GET /api/leads` 503 doner (liste kapali kalir).
Rastgele anahtar uretmek icin: `python -c "import secrets;print(secrets.token_urlsafe(24))"`
