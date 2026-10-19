# run.py - Dijital Coban SmartLead AI
# Giris noktasi. Gelistirme: python run.py  |  Uretim (Render): gunicorn run:app
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
