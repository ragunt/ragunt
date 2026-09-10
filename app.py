import streamlit as st

from src.aae_strategist import FACTOR_MAX, rank_products
from src.shopee_analyzer import analyze_shopee_url

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")

st.title("🔥 Arash Affiliate Engine")
st.caption("AAE v8 — memisahkan produk laris, potensi affiliate, dan potensi konten.")

manual_tab, shopee_tab = st.tabs(["📊 Bandingkan Manual", "🔗 Analisa Link Shopee"])


def competition_input(key, default="Tidak diketahui"):
    options = ["Tidak diketahui", "Rendah", "Sedang", "Tinggi"]
    selected = st.selectbox("Persaingan", options, index=options.index(default), key=key)
    return {"Tidak diketahui": -1, "Rendah": 2, "Sedang": 5, "Tinggi": 8}[selected], selected


def show_result(winner):
    decision = winner["decision"]
    if decision == "🔥 AMBIL & TES": st.success(f"🚀 {decision}")
    elif decision == "🟡 KUMPULKAN DATA": st.warning(decision)
    else: st.error(decision)

    st.info(f"**Alasan keputusan:** {winner['decision_reason']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Product Score", f"{winner['score']}/100")
    c2.metric("Affiliate Score", f"{winner['affiliate_score']}/100")
    c3.metric("Content Score", f"{winner['content_score']}/100")
    st.metric("Confidence data", f"{winner['confidence']}%")
    if winner["estimated_commission_per_sale"]:
        st.metric("Estimasi komisi / transaksi", f"Rp{winner['estimated_commission_per_sale']:,.0f}".replace(",", "."))
    else:
        st.warning("Komisi belum tersedia. Affiliate Score belum bisa dianggap final.")

    if winner["missing_critical_fields"]:
        st.warning("Data kritis yang masih kurang: " + ", ".join(winner["missing_critical_fields"]))

    st.write(f"**Faktor terlemah:** {winner['weakest_factor']}")
    st.subheader("🧠 Breakdown AAE v8")
    for factor, value in winner["breakdown"].items():
        st.write(f"**{factor}:** {value}/{FACTOR_MAX[factor]}")

    st.subheader("🎯 Strategi Konten")
    st.write(f"**Prioritas:** {winner['priority']}")
    st.write(f"**Angle:** {winner['angle']}")
    st.write(f"**Hook 1–3 detik:** {winner['hook']}")
    st.write(f"**Script 15–30 detik:** {winner['script_15_30s']}")
    st.write(f"**CTA:** {winner['cta']}")
    st.code(winner["caption"], language="text")
    st.write(f"**Gaya video:** {winner['video_style']}")


def collect_product(prefix, defaults=None):
    defaults = defaults or {}
    name = st.text_input("Nama produk", value=defaults.get("name", ""), key=f"{prefix}_name")
    category = st.text_input("Kategori", value=defaults.get("category", ""), key=f"{prefix}_category")
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Harga (Rp)", min_value=0, value=int(defaults.get("price", 0)), step=1000, key=f"{prefix}_price")
        commission = st.number_input("Komisi (%)", min_value=0.0, value=float(defaults.get("commission_percent", 0)), step=0.5, key=f"{prefix}_commission")
    with col2:
        rating = st.number_input("Rating produk", min_value=0.0, max_value=5.0, value=float(defaults.get("rating", 0)), step=0.1, key=f"{prefix}_rating")
        sales = st.number_input("Terjual", min_value=0, value=int(defaults.get("sales", 0)), step=100, key=f"{prefix}_sales")
    review_count = st.number_input("Jumlah ulasan", min_value=0, value=int(defaults.get("review_count", 0)), step=10, key=f"{prefix}_reviews")
    seller_rating = st.number_input("Rating seller (opsional)", min_value=0.0, max_value=5.0, value=float(defaults.get("seller_rating", 0)), step=0.1, key=f"{prefix}_seller_rating")
    problem = st.text_input("Masalah yang diselesaikan", value=defaults.get("problem", ""), key=f"{prefix}_problem")
    benefit = st.text_input("Manfaat utama", value=defaults.get("benefit", ""), key=f"{prefix}_benefit")
    target = st.text_input("Target pembeli", value=defaults.get("target", ""), key=f"{prefix}_target")
    competition, _ = competition_input(f"{prefix}_competition")
    return {"name": name, "category": category, "price": price, "commission_percent": commission, "rating": rating, "sales": sales, "review_count": review_count, "seller_rating": seller_rating, "problem": problem, "benefit": benefit, "target": target, "competition": competition}


with shopee_tab:
    st.subheader("🔗 Analisa Produk Shopee")
    st.info("Tempel link produk Shopee. AAE membaca data publik secara best-effort; komisi affiliate tetap perlu dikonfirmasi di akun Affiliate.")
    url = st.text_input("Link produk Shopee", placeholder="https://shopee.co.id/...")

    if st.button("🔍 Analisa Produk", type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Tempel link produk Shopee terlebih dahulu.")
        else:
            result = analyze_shopee_url(url)
            if not result["ok"]:
                st.error(result["error"])
                st.warning("Gunakan data manual untuk field yang belum terbaca otomatis.")
            else:
                data = result["data"]
                missing = data.get("missing_fields", [])
                auto_fields = data.get("auto_fields", [])
                if missing: st.warning("Belum terbaca otomatis: " + ", ".join(missing))
                else: st.success("✅ Data dasar produk berhasil dibaca otomatis.")
                st.caption("Otomatis terbaca: " + (", ".join(auto_fields) if auto_fields else "belum ada"))
                if data.get("image"): st.image(data["image"], width=180)
                product = collect_product("shopee", data)
                if st.button("🚀 Nilai Potensi Affiliate", use_container_width=True, key="score_shopee"):
                    if not product["name"]: st.warning("Nama produk wajib diisi.")
                    else: show_result(rank_products([product])[0])

with manual_tab:
    st.subheader("📊 Penilai Produk Affiliate")
    st.info("Masukkan beberapa produk. AAE v8 memilih berdasarkan Affiliate Score, bukan sekadar jumlah terjual.")
    count = st.number_input("Jumlah produk", min_value=1, max_value=10, value=3, step=1)
    products = []
    for i in range(int(count)):
        st.markdown(f"### Produk {i + 1}")
        product = collect_product(f"manual_{i}", {"price": 49000, "commission_percent": 8, "rating": 4.8, "sales": 1000})
        if product["name"]: products.append(product)

    if st.button("🚀 Nilai & Pilih Produk", type="primary", use_container_width=True):
        if not products:
            st.warning("Isi minimal 1 nama produk.")
        else:
            ranked = rank_products(products)
            winner = ranked[0]
            st.success(f"🏆 Produk utama: {winner['product']} — Affiliate Score {winner['affiliate_score']}/100")
            st.subheader("🏆 Ranking Berdasarkan Affiliate Score")
            for idx, item in enumerate(ranked, start=1):
                st.markdown(f"**#{idx} — {item['product']}**")
                st.write(f"Affiliate: **{item['affiliate_score']}/100** | Product: **{item['score']}/100** | Content: **{item['content_score']}/100** | Keputusan: **{item['decision']}**")
                st.progress(min(int(item["affiliate_score"]), 100))
            st.subheader("🔎 Kenapa produk ini dipilih?")
            show_result(winner)

st.divider()
st.caption("AAE v8 — Affiliate Opportunity Engine. Product Score ≠ Affiliate Score ≠ Content Score. Data komisi dan eligibility tetap harus dikonfirmasi pada akun Shopee Affiliate.")
