// Wix Velo - Ana sayfa: sohbet + teklif formu
// Bilesen ID'leri: #inputMesaj #btnSor #txtCevap #inputIsim #inputTelefon #inputHayvan #inputNot #btnKaydet #txtSonuc
import { fetch } from 'wix-fetch';

const API = 'https://smartlead-kc49.onrender.com';
let gecmis = [];

$w.onReady(function () {
    $w('#btnSor').onClick(sohbetGonder);
    $w('#btnKaydet').onClick(leadKaydet);
});

async function sohbetGonder() {
    const mesaj = $w('#inputMesaj').value.trim();
    if (!mesaj) return;
    $w('#btnSor').disable();
    $w('#txtCevap').text = 'Yanıt hazırlanıyor…';
    try {
        const yanit = await fetch(`${API}/api/sohbet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mesaj, gecmis })
        });
        const veri = await yanit.json();
        $w('#txtCevap').text = veri.basari ? veri.cevap : veri.hata;
        if (veri.basari) {
            gecmis.push({ role: 'user', content: mesaj }, { role: 'assistant', content: veri.cevap });
            gecmis = gecmis.slice(-10);
        }
        $w('#inputMesaj').value = '';
    } catch (e) {
        $w('#txtCevap').text = 'Sunucuya ulaşılamadı. Lütfen birkaç saniye sonra tekrar deneyin.';
    }
    $w('#btnSor').enable();
}

async function leadKaydet() {
    const govde = {
        isim: $w('#inputIsim').value,
        telefon: $w('#inputTelefon').value,
        hayvan_sayisi: $w('#inputHayvan').value,
        mesaj: $w('#inputNot').value
    };
    try {
        const yanit = await fetch(`${API}/api/leads`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(govde)
        });
        const veri = await yanit.json();
        $w('#txtSonuc').text = veri.basari ? veri.mesaj : veri.hata;
    } catch (e) {
        $w('#txtSonuc').text = 'Sunucuya ulaşılamadı.';
    }
}
