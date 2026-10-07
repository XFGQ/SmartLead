# Duman testi - sadece ortam kontrolu (proje dosyasi DEGIL)
from flask import Flask
app = Flask(__name__)

@app.route('/')
def merhaba():
    return 'Ortam calisiyor!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
