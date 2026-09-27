from flask import Flask, request, jsonify

app = Flask(__name__)

GIZLI_SIFRE = "EnesGizliKonum2026!."

son_konum = {
    "lat": None,
    "lon": None,
    "zaman": "Henüz konum gelmedi"
}

@app.route('/')
def telefon_gonderici():
    return f"""
    <html>
        <head>
            <title>Konum Paylaşımı</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #1e1e2f; color: white; }}
                .kutu {{ background: #2d2d44; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 15px rgba(0,0,0,0.3); }}
                #durum {{ margin-top: 20px; font-size: 18px; color: #ffeb3b; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="kutu">
                <h2>📡 Konum Paylaşımı Aktif</h2>
                <p>Bu pencere açık kaldığı sürece konumunuz gönderiliyor...</p>
                <p id="durum">Konum alınıyor...</p>
            </div>

            <script>
                const SIFRE = "{GIZLI_SIFRE}";
                const SUNUCU_URL = "/guncelle";

                window.onload = function() {{
                    if (navigator.geolocation) {{
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
                                    document.getElementById("durum").innerText = "✅ Konum başarıyla gönderiliyor (Canlı)";
                                }})
                                .catch(error => {{
                                    document.getElementById("durum").innerText = "❌ Hata: " + error;
                                }});
                            }},
                            function(error) {{
                                document.getElementById("durum").innerText = "⚠️ Konum izni gerekli! (" + error.message + ")";
                            }},
                            {{ enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }}
                        );
                    }}
                }};
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

# JSON tabanlı konum okuma API'si (Sayfayı yeniletmeden arkadan veri çeker)
@app.route('/api/konum', methods=['GET'])
def api_konum():
    sifre = request.args.get("sifre")
    if sifre != GIZLI_SIFRE:
        return jsonify({"hata": "Yetkisiz"}), 403
    return jsonify(son_konum)

@app.route('/konumlar', methods=['GET'])
def konumlari_gor():
    sifre = request.args.get("sifre")
    if sifre != GIZLI_SIFRE:
        return "<h3>Hata: Yetkisiz erişim!</h3>", 403
    
    # Sayfa artık kendiliğinden yenilenmeyecek, arkadan AJAX ile saniyede bir güncellenecek!
    return f"""
    <html>
        <head>
            <title>Canlı Harita Takibi</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
                .kutu {{ background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }}
                .buton {{ background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; font-size: 20px; border-radius: 5px; display: inline-block; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="kutu">
                <h2>📍 Anlık Konum Takibi</h2>
                <p id="zaman"><b>Son Güncelleme:</b> Yükleniyor...</p>
                <br>
                <div id="haritaAlani">
                    <p style="color: gray;">Konum bekleniyor...</p>
                </div>
            </div>

            <script>
                const sifre = "{sifre}";
                
                function konumuGuncelle() {{
                    fetch('/api/konum?sifre=' + sifre)
                    .then(res => res.json())
                    .then(data => {{
                        if (data.lat && data.lon) {{
                            document.getElementById("zaman").innerHTML = "<b>Son Güncelleme:</b> " + data.zaman;
                            const haritaLinki = "https://www.google.com/maps?q=" + data.lat + "," + data.lon;
                            document.getElementById("haritaAlani").innerHTML = '<a class="buton" href="' + haritaLinki + '" target="_blank">🗺️ Haritada Aç / Göster</a>';
                        }} else {{
                            document.getElementById("zaman").innerText = "Henüz konum gelmedi.";
                        }}
                    }});
                }}

                // Sayfayı hiç yenilemeden her 3 saniyede bir arkadan veriyi tazecekle
                setInterval(konumuGuncelle, 3000);
                konumuGuncelle();
            </script>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
