import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

MENU = {
    '1': {"ad": "Fıstıklı Baklava (1 Kg)", "fiyat": 650},
    '2': {"ad": "Çikolatalı Yaş Pasta", "fiyat": 450},
    '3': {"ad": "Su Böreği", "fiyat": 300},
    '4': {"ad": "Karışık Kuru Pasta", "fiyat": 250}
}

user_sessions = {} 
siparisler = []

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender_phone = request.values.get('From')
    
    resp = MessagingResponse()
    msg = resp.message()

    if sender_phone not in user_sessions:
        user_sessions[sender_phone] = {'state': 'BASLANGIC', 'sepet': None}

    user_state = user_sessions[sender_phone]['state']

    
    if user_state == 'BASLANGIC' or incoming_msg in ['selam', 'merhaba', 'menu', 'iptal']:
        user_sessions[sender_phone] = {'state': 'SECIM_YAPIYOR', 'sepet': None}
        cevap = "*Zeytinli Pastanesi'ne Hoş Geldiniz!* \n\nLütfen ürün numarasını yazın:\n\n"
        for kod, urun in MENU.items():
            cevap += f"*{kod}* - {urun['ad']} : {urun['fiyat']} TL\n"
        msg.body(cevap)

    elif user_state == 'SECIM_YAPIYOR':
        if incoming_msg in MENU:
            secilen_urun = MENU[incoming_msg]
            user_sessions[sender_phone]['sepet'] = secilen_urun
            user_sessions[sender_phone]['state'] = 'ADRES_BEKLEME'
            msg.body(f" *{secilen_urun['ad']}* seçildi.\n\nLütfen *açık adresinizi* yazın:")
        else:
            msg.body(" Hatalı seçim. Lütfen menüdeki numaralardan birini yazın.")

    elif user_state == 'ADRES_BEKLEME':
        if len(incoming_msg) > 5:
            siparis_detayi = {
                "tarih": datetime.now().strftime("%H:%M"),
                "telefon": sender_phone,
                "urun": user_sessions[sender_phone]['sepet']['ad'],
                "fiyat": user_sessions[sender_phone]['sepet']['fiyat'],
                "adres": incoming_msg
            }
            siparisler.append(siparis_detayi)
            print(f"YENİ SİPARİŞ: {siparis_detayi}")
            msg.body(" Siparişiniz alındı! Teşekkürler.")
            user_sessions[sender_phone] = {'state': 'BASLANGIC', 'sepet': None}
        else:
            msg.body("Lütfen geçerli bir adres girin.")

    return str(resp)

@app.route("/panel")
def panel():
    html = "<h1>Gelen Siparişler</h1><hr>"
    for s in reversed(siparisler):
        html += f"<p><b>{s['tarih']}</b> - {s['urun']} - {s['adres']} ({s['telefon']})</p>"
    return html

if __name__ == "__main__":
    app.run(port=5000, debug=True)