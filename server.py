import os
from flask import Flask, jsonify, request

app = Flask(__name__)

konumlar = {}
GIZLI_SIFRE = "EnesGizliKonum2026!."


@app.route("/guncelle", methods=["POST"])
def konum_guncelle():
  veri = request.json
  if veri.get("sifre") != GIZLI_SIFRE:
    return jsonify({"hata": "Yetkisiz erişim!"}), 403

  cihaz_adi = veri.get("cihaz")
  enlem = veri.get("lat")
  boylam = veri.get("lon")

  konumlar[cihaz_adi] = {"lat": enlem, "lon": boylam}
  return jsonify({"durum": "Basarili"})


@app.route("/konumlar", methods=["GET"])
def konum_getir():
  sifre = request.args.get("sifre")
  if sifre != GIZLI_SIFRE:
    return jsonify({"hata": "Yetkisiz erişim!"}), 403
  return jsonify(konumlar)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)