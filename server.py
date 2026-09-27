from flask import Flask, request, jsonify

app = Flask(__name__)

GIZLI_SIFRE = "EnesGizliKonum2026!."

son_konum = {
    "lat": None,
    "lon": None,
    "zaman": "Henüz konum gelmedi"
}

# Telefonun tarayıcısından tek tıkla konum göndereceği sihirli sayfa
@app.route('/')
def telefon_gonderici():
    return f"""
    <html>
        <head>
            <title>Konum Gönderici</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #1e1e2f; color: white; }}
                .kutu {{ background: #2d2d44; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 15px rgba(0,0,0,0.3); }}
                button {{ background-color: #4CAF50; color: white; padding: 15px 25px; font-size: 18px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }}
                button:hover {{ background-color: #45a049; }}
                #durum {{ margin-top: 20px; font-size: 16px; color: #ffeb3b; }}
            </style>
        </head>
        <body>
            <div class="kutu">
                <h2>📱 Konum Paylaşım Paneli</h2>
                <p>Konumunuzun sunucuya iletilmesi için aşağıdaki butona dokunun.</p>
                <button onclick="konumuPaylas()">Konumu Paylaşmaya Başla</button>
                <p id="durum">Bekleniyor...</p>
            </div>

            <script>
                const SIFRE = "{GIZLI_SIFRE}";
                const SUNUCU_URL = "/guncelle";

                function konumuPaylas() {{
                    if (navigator.geolocation) {{
                        document.getElementById("durum").innerText = "Konum alınıyor...";
                        navigator.geolocation.watchPosition(
                            function(position) {{
                                const lat = position.coords.latitude;
                                const lon = position.coords.longitude;
                                
                                fetch(SUNUCU_URL, {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{ sifre: SIFRE, lat: lat, lon: lon, zaman: new Date().toLocaleString() }})
                                }})
                                .then(response => response.json())
                                .then(data => {{
                                    document.getElementById("durum").innerText = "✅ Konum başarıyla gönderildi! (Canlı güncelleniyor)";
                                }})
                                .catch(error => {{
                                    document.getElementById("durum").innerText = "❌ Gönderim hatası: " + error;
                                }});
                            }},
                            function(error) {{
                                document.getElementById("durum").innerText = "Hata: Konum izni verilmedi veya GPS kapalı! (" + error.message + ")";
                            }},
                            {{ enableHighAccuracy: true, maximumAge: 10000, timeout: 5000 }}
                        );
                    }} else {{
                        document.getElementById("durum").innerText = "Tarayıcınız konum özelliğini desteklemiyor.";
                    }}
                }}
            </script>
        </body>
    </html>
    """

@app.route('/guncelle', methods=['POST'])
def konum_guncelle():
    veri = request.json
    if not veri or veri.get("sifre") != GIZLI_SIFRE:
        return jsonify({"hata": "Yetkisiz erişim!"}), 403
    
    son_konum["lat"] = veri.get("lat")
    son_konum["lon"] = veri.get("lon")
    son_konum["zaman"] = veri.get("zaman", "Bilinmeyen zaman")
    return jsonify({"durum": "Basarili"})

@app.route('/konumlar', methods=['GET'])
def konumlari_gor():
    sifre = request.args.get("sifre")
    if sifre != GIZLI_SIFRE:
        return "<h3>Hata: Yetkisiz erişim!</h3>", 403
    
    if son_konum["lat"] is None or son_konum["lon"] is None:
        return "<h3>Henüz konum gelmedi. Telefonunuzdan ana sayfayı açıp konumu paylaşın.</h3>"
    
    lat = son_konum["lat"]
    lon = son_konum["lon"]
    zaman = son_konum["zaman"]
    harita_linki = f"https://www.google.com/maps?q={lat},{lon}"
    
    return f"""
    <html>
        <head>
            <title>Canlı Harita Takibi</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
                .kutu {{ background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }}
                .buton {{ background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; font-size: 20px; border-radius: 5px; display: inline-block; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="kutu">
                <h2>📍 Telefonun Anlık Konumu</h2>
                <p><b>Son Güncelleme:</b> {zaman}</p>
                <br>
                <a class="buton" href="{harita_linki}" target="_blank">🗺️ Haritada Aç / Göster</a>
                <p style="font-size: 12px; color: gray; margin-top: 20px;">Sayfa her 10 saniyede bir otomatik yenilenir.</p>
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
