# Arash Affiliate Engine (AAE) v8.2

MVP sistem untuk membantu Shopee Affiliate memilih produk, memeriksa kualitas data, menentukan angle, hook, script Shorts 15–30 detik, caption, dan skor peluang affiliate.

## Prinsip v8.2
- Modal awal Rp0 dan tetap praktis dijalankan dari HP.
- Tidak menyamakan **produk laris** dengan **peluang affiliate terbaik**.
- Data yang tidak diketahui tidak boleh diam-diam dianggap fakta.
- Angka `10RB+` diperlakukan sebagai lower bound, bukan tepat 10.000.
- Rating produk dan rating seller dipisahkan.
- Field problem/benefit/target dapat diinferensikan dari nama, kategori, dan deskripsi, tetapi sumber inference tetap ditandai.
- Estimasi komisi adalah gross estimate, bukan jaminan payout.

## Fitur v8.2
1. **Penilai Produk Manual** — bandingkan sampai 10 produk berdasarkan demand, ekonomi affiliate, kualitas, potensi konten, persaingan, dan risiko.
2. **Analisa Link Shopee** — tempel URL produk Shopee Indonesia dan AAE mencoba membaca metadata publik.
3. **Data Intelligence** — inferensi problem, benefit, target dan estimasi persaingan ketika data manual belum tersedia.
4. **Data Quality & Suspicious Data** — memberi peringatan untuk lower-bound sales, ketidakkonsistenan rating/ulasan, harga varian, dan data yang perlu diverifikasi.
5. **Safe defaults** — mode manual tidak lagi mengisi angka contoh yang berpotensi dianggap sebagai data produk nyata.
6. **Regression tests** — pengujian strategist, intelligence, dan parser Shopee.

## Struktur
```text
src/
  __init__.py
  aae_strategist.py       # scoring + decision + strategy
  data_intelligence.py    # inference + data quality + suspicious-data checks
  shopee_analyzer.py      # pembaca metadata publik Shopee
examples/
  products.json
  app.py
  tests/
```

## Jalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```

Atau:
```bash
python src/aae_strategist.py examples/products.json
python -m unittest discover -s tests -v
```

## Batasan yang sengaja dipertahankan
Analisa link menggunakan HTTP request ke halaman publik dan parser metadata. Shopee dapat menggunakan halaman dinamis atau membatasi akses sehingga tidak semua link pasti bisa dibaca otomatis. AAE tidak mencoba bypass anti-bot atau kontrol akses.

Komisi affiliate tidak diasumsikan tersedia dari halaman produk. User perlu memasukkan tarif komisi yang benar untuk kanal/program affiliate yang digunakan.

AAE belum menggunakan Shopee API resmi atau model AI eksternal. Tahap berikutnya dapat menambahkan data kanal komisi, eligibility seller/product, cache, dan market evidence bertimestamp.
