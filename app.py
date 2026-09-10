import streamlit as st

from src.aae_strategist import FACTOR_MAX, rank_products
from src.shopee_analyzer import analyze_shopee_url

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")

st.title("🔥 Arash Affiliate Engine")
st.caption("Bukan cuma cari produk laris — AAE menilai peluang affiliate-nya.")

manual_tab, shopee_tab = st.tabs(["📊 Bandingkan Manual", "🔗 Analisa Link Shopee"])


def competition_input(key, default="Tidak diketahui"):
    label = "Persaingan"
    options = ["Tidak diketahui", "Rendah", "Sedang", "Tinggi"]
    selected = st.selectbox(label, options, index=options.index(default), key=key)
    return {"Tidak diketahui": -1, "Rendah": 2, "Sedang": 5, "Tinggi": 8}[selected], selected


def show_result(winner):
    decision = winner["decision"]
    if decision == "🔥 AMBIL & TES":
        st.success(decision)
    elif decision == "🟢 LAYAK DIUJI":
        st.success(decision)
    elif decision == "🟡 KUMPULKAN DATA":
        st.warning(decision)
    else:
        st.error(decision)

    st.info(f"**Alasan keputusan:** {winner['decision_reason']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Product Score", f"{winner['score']}/100")
    with col2:
        st.metric("Affiliate Score", f"{winner['affiliate_score']}/100")
    with col3:
        st.metric("Content Score", f"{winner['content_score']}/100")

    st.metric("Confidence data", f"{winner['confidence']}%")
    if winner["estimated_commission_per_sale"]:
        st.metric("Estimasi komisi / transaksi", f"Rp{winner['estimated_commission_per_sale']:,.0f}".replace(",", "."))
        st.caption("Estimasi kotor berdasarkan harga × tarif komisi; payout aktual dapat berbeda karena skema dan nilai pembelian bersih.")
    else:
        st.warning("Komisi belum tersedia. Estimasi komisi per transaksi belum bisa dihitung.")

    if winner["missing_critical_fields"]:
        st.warning("Data kritis yang masih kurang: " + ", ".join(winner["missing_critical_fields"]))

    st.write(f"**Prioritas:** {winner['priority']}")
    st.write(f"**Faktor terlemah (relatif):** {winner['weakest_factor']}")

    st.subheader("🧠 Penilaian AAE")
    for factor, value in winner["breakdown"].items():
        st.write(f"**{factor}:** {value}/{FACTOR_MAX[factor]}")

    st.subheader("🎯 Strategi Konten")
    st.write(f"**Angle:** {winner['angle']}")
    st.write(f"**Hook 1–3 detik:** {winner['hook']}")
    st.write(f"**Script 15–30 detik:** {winner['script_15_30s']}")
    st.write(f"**CTA:** {winner['cta']}")
    st.code(winner["caption"], language="text")
    st.write(f"**Gaya video:** {winner['video_style']}")


with shopee_tab:
    st.subheader("🔗 Analisa Produk Shopee")
    st.info("Tempel link produk Shopee. AAE mencoba membaca data publik; data affiliate seperti komisi bisa tetap perlu diisi manual.")
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
                st.session_state["shopee_data"] = result["data"]

    if "shopee_data" in st.session_state:
        data = st.session_state["shopee_data"]
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
            rating = st.number_input("Rating produk", min_value=0.0, max_value=5.0, value=float(data.get("rating", 0)), step=0.1, key="shopee_rating")
            sales = st.number_input("Terjual", min_value=0, value=int(data.get("sales", 0)), step=100, key="shopee_sales")

        review_count = st.number_input("Jumlah ulasan", min_value=0, value=int(data.get("review_count", 0)), step=10, key="shopee_reviews")
        seller_rating = st.number_input("Rating seller (opsional)", min_value=0.0, max_value=5.0, value=float(data.get("seller_rating", 0)), step=0.1, key="shopee_seller_rating")
        problem = st.text_input("Masalah yang diselesaikan", value=data.get("problem", ""), key="shopee_problem")
        benefit = st.text_input("Manfaat utama", value=data.get("benefit", ""), key="shopee_benefit")
        target = st.text_input("Target pembeli", value=data.get("target", ""), key="shopee_target")
        competition, competition_label = competition_input("shopee_competition")

        st.divider()
        st.subheader("🧾 Kualitas Data")
        checks = {
            "Nama": bool(name), "Harga": price > 0, "Rating produk": rating > 0,
            "Terjual": sales > 0, "Ulasan": review_count > 0, "Komisi": commission > 0,
            "Masalah": bool(problem), "Manfaat": bool(benefit), "Target": bool(target),
            "Persaingan": competition >= 0,
        }
        for label, done in checks.items():
            st.write(f"{'✅' if done else '⬜'} {label}")
        if competition < 0:
            st.caption("Persaingan belum diketahui tidak dihitung sebagai data pasti; AAE memakai skor netral.")

        if st.button("🚀 Nilai Potensi Affiliate", use_container_width=True, key="score_shopee"):
            if not name:
                st.warning("Nama produk wajib diisi.")
            else:
                product = {
                    "name": name, "category": category, "price": price,
                    "commission_percent": commission, "rating": rating, "sales": sales,
                    "review_count": review_count, "seller_rating": seller_rating,
                    "problem": problem, "benefit": benefit, "target": target,
                    "competition": competition,
                }
                st.session_state["shopee_score_result"] = rank_products([product])[0]

        if "shopee_score_result" in st.session_state:
            show_result(st.session_state["shopee_score_result"])

with manual_tab:
    st.subheader("📊 Penilai Produk Affiliate")
    st.info("Masukkan data beberapa produk. AAE akan membandingkan demand, ekonomi affiliate, kualitas, potensi konten, persaingan, dan risiko.")

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
            rating = st.number_input("Rating produk", min_value=0.0, max_value=5.0, value=4.8, step=0.1, key=f"rating_{i}")
            sales = st.number_input("Terjual", min_value=0, value=1000, step=100, key=f"sales_{i}")
        review_count = st.number_input("Jumlah ulasan", min_value=0, value=0, step=10, key=f"reviews_{i}")
        seller_rating = st.number_input("Rating seller (opsional)", min_value=0.0, max_value=5.0, value=0.0, step=0.1, key=f"seller_{i}")
        competition, competition_label = competition_input(f"competition_{i}")
        problem = st.text_input("Masalah yang diselesaikan", key=f"problem_{i}")
        benefit = st.text_input("Manfaat utama", key=f"benefit_{i}")
        target = st.text_input("Target pembeli", key=f"target_{i}")

        if name:
            products.append({
                "name": name, "category": category, "price": price,
                "commission_percent": commission, "rating": rating, "sales": sales,
                "review_count": review_count, "seller_rating": seller_rating,
                "competition": competition, "problem": problem, "benefit": benefit,
                "target": target,
            })

    if st.button("🚀 Nilai & Pilih Produk", type="primary", use_container_width=True):
        if not products:
            st.warning("Isi minimal 1 nama produk.")
        else:
            st.session_state["manual_ranked"] = rank_products(products)

    if "manual_ranked" in st.session_state:
        ranked = st.session_state["manual_ranked"]
        winner = ranked[0]
        st.success(f"🏆 Produk utama: {winner['product']} — Affiliate Score {winner['affiliate_score']}/100")
        st.subheader("🏆 Ranking Produk")
        for idx, item in enumerate(ranked, start=1):
            st.markdown(f"**#{idx} — {item['product']}**")
            st.write(f"Affiliate: **{item['affiliate_score']}/100** | Product: **{item['score']}/100** | Content: **{item['content_score']}/100** | Confidence: **{item['confidence']}%** | Keputusan: **{item['decision']}**")
            st.progress(min(int(item["affiliate_score"]), 100))
        st.subheader("🔎 Kenapa produk ini dipilih?")
        show_result(winner)

st.divider()
st.caption("AAE v8.1 — Affiliate Score, Content Score, Decision Engine, state persistence, dan regression tests. Analisa Shopee tetap best-effort karena halaman dapat dinamis atau membatasi akses.")
