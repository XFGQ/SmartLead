# SmartLead AI - Dijital Coban Akilli Satis Asistani

Dijital Coban | Akilli Ahir Cozumleri icin ziyaretci sohbeti ve lead toplama sistemi.

## Mimari
- `config.py`: ayarlar (.env)
- `app/database.py`: SQLite (SQL sadece burada)
- `app/services/ai_service.py`: Groq AI cagrilari (sadece burada)
- `app/routes.py`: HTTP rotalari

## Calistirma (Docker)
```
copy .env.example .env   # Linux/Mac: cp
docker compose up --build
```
Tarayici: http://localhost:5000
