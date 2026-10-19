# GetlocRams — Bantuan Lokasi Jemaah Umroh

Aplikasi Flask yang memungkinkan jemaah **secara sadar dan sukarela** membagikan koordinat GPS aktual satu kali kepada petugas melalui Telegram.

## Menjalankan

1. `pip install -r requirements.txt`
2. Salin `.env.example` menjadi `.env`, lalu isi token Telegram Bot dan Chat ID petugas.
3. Jalankan `python app.py`.
4. Buka `http://localhost:5001` untuk pengujian di komputer yang sama.
5. Untuk digunakan pada HP jemaah, deploy melalui **HTTPS** dengan server produksi (misalnya Gunicorn di belakang reverse proxy HTTPS). Browser memerlukan secure context untuk Geolocation API.

## Catatan

- Hanya lokasi yang disetujui pengguna yang dikirim; tidak ada pelacakan diam-diam atau berkala.
- Telegram bot harus memiliki izin mengirim pesan ke chat/grup tujuan.
- Simpan `.env` secara rahasia dan jangan commit ke repositori.
- Jangan gunakan Flask development server untuk produksi. Tambahkan CSRF/origin controls, rate limiting terpusat, pengamanan akses, monitoring dan kebijakan retensi data sebelum peluncuran publik.
- Endpoint menerima koordinat dari browser; server tidak bisa membuktikan bahwa koordinat tersebut asli atau tidak dimanipulasi.
- Pastikan nomor kontak darurat rombongan tersedia sebagai alternatif.
