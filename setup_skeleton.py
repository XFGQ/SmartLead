"""SmartLead AI iskelet kurulumu (kod YAZMAZ, sadece klasor/dosya iskeletini ve Docker dosyalarini olusturur).
Kullanim: SmartLead reposunun kok klasorunde:  python setup_skeleton.py
"""
from pathlib import Path

HEADER = "# {name} - Dijital Coban SmartLead AI\n# TODO: Modul {mod} yonergeye gore buraya yazilacak.\n"

FILES = {
    "run.py": HEADER.format(name="run.py", mod="E"),
    "config.py": HEADER.format(name="config.py", mod="A"),
    "app/__init__.py": HEADER.format(name="app/__init__.py", mod="E"),
    "app/database.py": HEADER.format(name="app/database.py", mod="B"),
    "app/routes.py": HEADER.format(name="app/routes.py", mod="D"),
    "app/services/__init__.py": "",
    "app/services/ai_service.py": HEADER.format(name="ai_service.py", mod="C"),
    "app/templates/index.html": "<!-- Karsilama sayfasi (Modul G) -->\n",
    "app/templates/dashboard.html": "<!-- Yonetim paneli (Modul G) -->\n",
    "data/.gitkeep": "",
    "hello.py": (
        "# Duman testi - sadece ortam kontrolu (proje dosyasi DEGIL)\n"
        "from flask import Flask\n"
        "app = Flask(__name__)\n\n"
        "@app.route('/')\n"
        "def merhaba():\n"
        "    return 'Ortam calisiyor!'\n\n"
        "if __name__ == '__main__':\n"
        "    app.run(host='0.0.0.0', port=5000)\n"
    ),
    "requirements.txt": "flask\nflask-cors\npython-dotenv\nrequests\ngunicorn\n",
    ".env.example": (
        "SECRET_KEY=degistir-beni\n"
        "DATABASE_URL=data/smartlead.db\n"
        "GROQ_API_KEY=gsk_BURAYA_KENDI_ANAHTARIN\n"
        "AI_PROVIDER=groq\n"
        "CORS_ORIGINS=*\n"
        "FLASK_ENV=development\n"
    ),
    ".gitignore": ".env\nvenv/\n.venv/\n__pycache__/\n*.pyc\ndata/*.db\n.vscode/\n",
    ".dockerignore": ".env\nvenv/\n.venv/\n__pycache__/\n*.pyc\n.git/\ndata/*.db\n",
    "Dockerfile": (
        "FROM python:3.11-slim\n"
        "WORKDIR /srv\n"
        "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "EXPOSE 5000\n"
        "# Smoke test icin hello.py; proje hazir olunca: CMD [\"python\", \"run.py\"]\n"
        "CMD [\"python\", \"hello.py\"]\n"
    ),
    "docker-compose.yml": (
        "services:\n"
        "  smartlead:\n"
        "    build: .\n"
        "    ports:\n"
        "      - \"5000:5000\"\n"
        "    env_file:\n"
        "      - .env\n"
        "    volumes:\n"
        "      - ./data:/srv/data   # SQLite dosyasi konteyner silinse de kalir\n"
        "    restart: unless-stopped\n"
    ),
    "README.md": (
        "# SmartLead AI - Dijital Coban Akilli Satis Asistani\n\n"
        "Dijital Coban | Akilli Ahir Cozumleri icin ziyaretci sohbeti ve lead toplama sistemi.\n\n"
        "## Mimari\n- `config.py`: ayarlar (.env)\n- `app/database.py`: SQLite (SQL sadece burada)\n"
        "- `app/services/ai_service.py`: Groq AI cagrilari (sadece burada)\n- `app/routes.py`: HTTP rotalari\n\n"
        "## Calistirma (Docker)\n```\ncopy .env.example .env   # Linux/Mac: cp\ndocker compose up --build\n```\n"
        "Tarayici: http://localhost:5000\n"
    ),
}

for rel, content in FILES.items():
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        print("atlandi (var):", rel)
        continue
    p.write_text(content, encoding="utf-8")
    print("olusturuldu:", rel)
print("\nTamam. Siradaki: git add . && git commit -m \"Iskelet\" && git push")