FROM python:3.11-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
# Smoke test icin hello.py; proje hazir olunca: CMD ["python", "run.py"]
CMD ["python", "hello.py"]
