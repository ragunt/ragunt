# Arash Affiliate Engine (AAE)

MVP awal sistem AI untuk membantu Shopee Affiliate: memilih produk, menentukan angle, hook, script Shorts 15–30 detik, caption, hashtag, dan skor peluang konten.

## Target
- Modal awal Rp0
- Bisa dikembangkan dari HP
- Fokus konten pendek 15–30 detik
- Tidak bergantung pada ajakan subscribe/follow
- Output siap dipakai untuk proses produksi konten

## Struktur
```text
src/
  aae_strategist.py   # mesin strategi konten MVP
examples/
  products.json       # contoh data produk
```

## Jalankan
```bash
python src/aae_strategist.py examples/products.json
```

MVP ini belum terhubung ke Shopee API atau model AI eksternal. Tahap berikutnya dapat menambahkan sumber data produk, model AI, penyimpanan performa, dan scheduler.
