# Arash Affiliate Engine (AAE)

MVP sistem untuk membantu Shopee Affiliate memilih produk, menentukan angle, hook, script Shorts 15–30 detik, caption, hashtag, dan skor peluang konten.

## Target
- Modal awal Rp0
- Bisa dikembangkan dari HP
- Fokus konten pendek 15–30 detik
- Tidak bergantung pada ajakan subscribe/follow
- Output siap dipakai untuk proses produksi konten

## Fitur saat ini
1. **Penilai Produk Manual** — bandingkan sampai 10 produk berdasarkan rating, penjualan, komisi, harga, kejelasan masalah, dan manfaat.
2. **Analisa Link Shopee** — tempel URL produk Shopee Indonesia dan AAE mencoba membaca metadata publik produk.
3. **Strategi Konten** — setelah data cukup, AAE menghasilkan skor 0–100, ranking, angle, hook, script 15–30 detik, CTA, caption, dan gaya video.

## Struktur
```text
src/
  __init__.py
  aae_strategist.py   # mesin skor + strategi konten
  shopee_analyzer.py  # pembaca metadata halaman Shopee
examples/
  products.json       # contoh data produk
app.py                # antarmuka Streamlit
```

## Jalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```

Atau jalankan mesin skor dari terminal:
```bash
python src/aae_strategist.py examples/products.json
```

## Catatan penting tentang link Shopee
Analisa link menggunakan HTTP request ke halaman publik dan parser metadata. Shopee dapat menggunakan halaman dinamis, login, anti-bot, atau pembatasan akses sehingga **tidak semua link pasti bisa dibaca otomatis**. Jika akses otomatis gagal, data tetap bisa dimasukkan melalui mode manual.

Komisi affiliate juga tidak diasumsikan tersedia dari halaman produk, sehingga kolom komisi tetap dapat dikoreksi/dilengkapi secara manual.

AAE belum menggunakan Shopee API resmi atau model AI eksternal. Integrasi resmi/API dan analisis performa dapat ditambahkan pada tahap berikutnya.
