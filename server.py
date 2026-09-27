from flask import Flask, request, jsonify

app = Flask(__name__)

# Güvenlik şifremiz
GIZLI_SIFRE = "EnesGizliKonum2026!."

# Son konumu saklamak için geçici hafıza
son_konum = {
    "lat": None,
    "lon": None,
    "zaman": "Henüz konum gelmedi"
}

@app.route('/')
def ana_sayfa():
    return "GPS Takip Sunucusu Aktif ve Çalışıyor! 🚀"

# Telefonun konum gönderdiği yer
@app.route('/guncelle', methods=['POST'])
def konum_guncelle():
    veri = request.json
    
    # Şifre kontrolü
    if not veri or veri.get("sifre") != GIZLI_SIFRE:
        return jsonify({"hata": "Yetkisiz erişim!"}), 403
    
    son_konum["lat"] = veri.get("lat")
    son_konum["lon"] = veri.get("lon")
    son_konum["zaman"] = veri.get("zaman", "Bilinmeyen zaman")
    
    return jsonify({"durum": "Basarili", "mesaj": "Konum kaydedildi!"})

# Senin haritada göreceğin yer
@app.route('/konumlar', methods=['GET'])
def konumlari_gor():
    sifre = request.args.get("sifre")
    
    # Şifre kontrolü
    if sifre != GIZLI_SIFRE:
        return "<h3>Hata: Yetkisiz erişim veya yanlış şifre!</h3>", 403
    
    if son_konum["lat"] is None or son_konum["lon"] is None:
        return "<h3>Henüz telefondan bir konum gelmedi. Lütfen telefon uygulamasını çalıştırın.</h3>"
    
    lat = son_konum["lat"]
    lon = son_konum["lon"]
    zaman = son_konum["zaman"]
    
    # Google Maps linkini otomatik oluşturuyoruz
    harita_linki = f"https://www.google.com/maps?q={lat},{lon}"
    
    # Ekrana şık ve tıklanabilir bir tasarım basıyoruz
    html_ciktisi = f"""
    <html>
        <head>
            <title>Canlı Konum Takibi</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="15"> <!-- Sayfa her 15 saniyede bir otomatik yenilenir -->
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
                .kutu {{ background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }}
                .buton {{ background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; font-size: 20px; border-radius: 5px; display: inline-block; margin-top: 20px; }}
                .buton:hover {{ background-color: #45a049; }}
            </style>
        </head>
        <body>
            <div class="kutu">
                <h2>📍 Telefonun Anlık Konumu</h2>
                <p><b>Son Güncelleme Zamanı:</b> {zaman}</p>
                <p><b>Enlem (Lat):</b> {lat}</p>
                <p><b>Boylam (Lon):</b> {lon}</p>
                <br>
                <a class="buton" href="{harita_linki}" target="_blank">🗺️ Haritada Aç / Göster</a>
                <p style="font-size: 12px; color: gray; margin-top: 20px;">Bu sayfa yeni konumları görmek için her 15 saniyede bir otomatik yenilenir.</p>
            </div>
        </body>
    </html>
    """
    return html_ciktisi

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
