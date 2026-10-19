// Wix Velo - Dashboard sayfasi (sayfayi Wix'te "Uyeler/Yonetici" ile kisitlayin)
// Bilesen ID'leri: #repeaterLeads (icinde #txtIsim #txtTelefon #txtHayvan #txtMesaj #txtTarih), #txtToplam
// ADMIN_TOKEN tarayiciya konmaz: istek Wix backend'den (leads.web.js) yapilir, anahtar Wix Secrets Manager'da durur.
import { leadleriGetir } from 'backend/leads.web';

$w.onReady(async function () {
    const veri = await leadleriGetir();
    if (!veri.basari) {
        $w('#txtToplam').text = veri.hata;
        return;
    }
    $w('#txtToplam').text = `${veri.toplam} talep`;
    $w('#repeaterLeads').data = veri.leadler.map(l => ({ _id: String(l.id), ...l }));
    $w('#repeaterLeads').onItemReady(($item, satir) => {
        $item('#txtIsim').text = satir.isim;
        $item('#txtTelefon').text = satir.telefon;
        $item('#txtHayvan').text = satir.hayvan_sayisi != null ? `${satir.hayvan_sayisi} baş` : '–';
        $item('#txtMesaj').text = satir.mesaj || '–';
        $item('#txtTarih').text = satir.tarih;
    });
});
