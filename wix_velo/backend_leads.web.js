// Wix Velo backend dosyasi: backend/leads.web.js
// Secrets Manager'a "SMARTLEAD_ADMIN_TOKEN" adiyla Render'daki ADMIN_TOKEN degerini ekleyin.
import { Permissions, webMethod } from 'wix-web-module';
import { fetch } from 'wix-fetch';
import { getSecret } from 'wix-secrets-backend';

const API = 'https://smartlead-kc49.onrender.com';

export const leadleriGetir = webMethod(Permissions.Admin, async () => {
    const token = await getSecret('SMARTLEAD_ADMIN_TOKEN');
    const yanit = await fetch(`${API}/api/leads`, { headers: { 'X-Admin-Token': token } });
    return yanit.json();
});
