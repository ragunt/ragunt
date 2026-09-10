import streamlit as st

from src.aae_strategist import rank_products
from src.shopee_analyzer import analyze_shopee_url

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")

st.title("🔥 Arash Affiliate Engine")
st.caption("Pilih produk yang paling berpotensi sebelum bikin konten affiliate.")

manual_tab, shopee_tab = st.tabs(["📊 Bandingkan Manual", "🔗 Analisa Link Shopee"])

with shopee_tab:
    st.subheader("🔗 Analisa Produk Shopee")
    st.info("Tempel link produk Shopee. AAE mencoba membaca data publik dan akan menunjukkan data mana yang masih perlu dilengkapi.")
    url = st.text_input("Link produk Shopee", placeholder="https://shopee.co.id/...")

    if st.button("🔍 Analisa Produk", type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Tempel link produk Shopee terlebih dahulu.")
        else:
            result = analyze_shopee_url(url)
            if not result["ok"]:
                st.error(result["error"])
                if result.get("fallback"):
                    st.warning("Gunakan data manual untuk field yang belum terbaca otomatis.")
            else:
                data = result["data"]
                missing = data.get("missing_fields", [])
                auto_fields = data.get("auto_fields", [])

                if missing:
                    st.warning("⚠️ Sebagian data belum terbaca otomatis. Lengkapi field yang kosong sebelum penilaian.")
                    st.caption("Belum terbaca: " + ", ".join(missing))
                else:
                    st.success("✅ Data dasar produk berhasil dibaca otomatis.")

                st.caption("Otomatis terbaca: " + (", ".join(auto_fields) if auto_fields else "belum ada"))
                if data.get("image"):
                    st.image(data["image"], width=180)

                name = st.text_input("Nama produk", value=data.get("name", ""), key="shopee_name")
                category = st.text_input("Kategori", value=data.get("category", ""), key="shopee_category")
                col1, col2 = st.columns(2)
                with col1:
                    price = st.number_input("Harga (Rp)", min_value=0, value=int(data.get("price", 0)), step=1000, key="shopee_price")
                    commission = st.number_input("Komisi (%)", min_value=0.0, value=float(data.get("commission_percent", 0)), step=0.5, key="shopee_commission")
                with col2:
                    rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=float(data.get("rating", 0)), step=0.1, key="shopee_rating")
                    sales = st.number_input("Terjual", min_value=0, value=int(data.get("sales", 0)), step=100, key="shopee_sales")

                review_count = st.number_input("Jumlah ulasan", min_value=0, value=int(data.get("review_count", 0)), step=10, key="shopee_reviews")
                problem = st.text_input("Masalah yang diselesaikan", value=data.get("problem", ""), key="shopee_problem")
                benefit = st.text_input("Manfaat utama", value=data.get("benefit", ""), key="shopee_benefit")
                target = st.text_input("Target pembeli", value=data.get("target", ""), key="shopee_target")

                st.divider()
                st.subheader("🧾 Checklist sebelum skor final")
                checks = {
                    "Nama": bool(name),
                    "Harga": price > 0,
                    "Rating": rating > 0,
                    "Terjual": sales > 0,
                    "Ulasan": review_count > 0,
                    "Komisi": commission > 0,
                    "Masalah": bool(problem),
                    "Manfaat": bool(benefit),
                    "Target": bool(target),
                }
                for label, done in checks.items():
                    st.write(f"{'✅' if done else '⬜'} {label}")

                if st.button("🚀 Nilai Potensi Affiliate", use_container_width=True, key="score_shopee"):
                    incomplete = [label for label, done in checks.items() if not done]
                    if incomplete:
                        st.warning("Lengkapi dulu: " + ", ".join(incomplete) + ". AAE tetap bisa menghitung skor, tetapi hasilnya belum final.")

                    if not name:
                        st.warning("Nama produk wajib diisi.")
                    else:
                        product = {
                            "name": name,
                            "category": category,
                            "price": price,
                            "commission_percent": commission,
                            "rating": rating,
                            "sales": sales,
                            "review_count": review_count,
                            "problem": problem,
                            "benefit": benefit,
                            "target": target,
                        }
                        winner = rank_products([product])[0]
                        st.success(f"🏆 Skor: {winner['score']}/100 — {winner['label']}")
                        st.subheader("🔎 Breakdown")
                        for factor, value in winner["breakdown"].items():
                            st.write(f"**{factor}:** {value}")
                        st.subheader("🎯 Strategi Konten")
                        st.write(f"**Angle:** {winner['angle']}")
                        st.write(f"**Hook 1–3 detik:** {winner['hook']}")
                        st.write(f"**Script 15–30 detik:** {winner['script_15_30s']}")
                        st.write(f"**CTA:** {winner['cta']}")
                        st.code(winner["caption"], language="text")
                        st.write(f"**Gaya video:** {winner['video_style']}")

with manual_tab:
    st.subheader("📊 Penilai Produk Affiliate")
    st.info("Masukkan data beberapa produk. AAE akan memberi skor 0–100, mengurutkan produk, dan menunjukkan alasan kenapa produk tersebut layak diuji.")

    count = st.number_input("Jumlah produk yang mau dibandingkan", min_value=1, max_value=10, value=3, step=1)
    products = []

    for i in range(int(count)):
        st.markdown(f"### Produk {i + 1}")
        name = st.text_input("Nama produk", key=f"name_{i}")
        category = st.text_input("Kategori", key=f"category_{i}")
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Harga (Rp)", min_value=0, value=49000, step=1000, key=f"price_{i}")
            commission = st.number_input("Komisi (%)", min_value=0.0, value=8.0, step=0.5, key=f"commission_{i}")
        with col2:
            rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=4.8, step=0.1, key=f"rating_{i}")
            sales = st.number_input("Terjual", min_value=0, value=1000, step=100, key=f"sales_{i}")
        problem = st.text_input("Masalah yang diselesaikan", key=f"problem_{i}")
        benefit = st.text_input("Manfaat utama", key=f"benefit_{i}")
        target = st.text_input("Target pembeli", key=f"target_{i}")

        if name:
            products.append({"name": name, "category": category, "price": price, "commission_percent": commission, "rating": rating, "sales": sales, "problem": problem, "benefit": benefit, "target": target})

    if st.button("🚀 Nilai & Pilih Produk", type="primary", use_container_width=True):
        if not products:
            st.warning("Isi minimal 1 nama produk.")
        else:
            ranked = rank_products(products)
            winner = ranked[0]
            st.success(f"🏆 Produk utama: {winner['product']} — {winner['score']}/100 ({winner['label']})")
            st.subheader("🏆 Ranking Produk")
            for idx, item in enumerate(ranked, start=1):
                st.markdown(f"**#{idx} — {item['product']}**")
                st.write(f"Skor: **{item['score']}/100** — {item['label']}")
                st.progress(min(int(item["score"]), 100))
            st.subheader("🔎 Kenapa produk ini dipilih?")
            for factor, value in winner["breakdown"].items():
                st.write(f"**{factor}:** {value}")
            st.subheader("🎯 Strategi Konten Produk Terpilih")
            st.write(f"**Angle:** {winner['angle']}")
            st.write(f"**Hook 1–3 detik:** {winner['hook']}")
            st.write(f"**Script 15–30 detik:** {winner['script_15_30s']}")
            st.write(f"**CTA:** {winner['cta']}")
            st.code(winner["caption"], language="text")
            st.write(f"**Gaya video:** {winner['video_style']}")

st.divider()
st.caption("AAE MVP v5 — analisa link Shopee bersifat best-effort; halaman dinamis atau pembatasan akses dapat membuat sebagian data tidak terbaca.")
