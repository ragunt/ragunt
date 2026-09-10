import streamlit as st

from src.aae_strategist import FACTOR_MAX, rank_products
from src.shopee_analyzer import analyze_shopee_url

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")
st.title("🔥 Arash Affiliate Engine")
st.caption("AAE v8.2 — Data Intelligence: bukan cuma cari produk laris, tapi cek kualitas datanya juga.")

manual_tab, shopee_tab = st.tabs(["📊 Bandingkan Manual", "🔗 Analisa Link Shopee"])


def competition_input(key, default="Tidak diketahui"):
    options = ["Tidak diketahui", "Rendah", "Sedang", "Tinggi"]
    selected = st.selectbox("Persaingan", options, index=options.index(default), key=key)
    return {"Tidak diketahui": -1, "Rendah": 2, "Sedang": 5, "Tinggi": 8}[selected], selected


def show_result(winner):
    decision = winner["decision"]
    if decision in {"🔥 AMBIL & TES", "🟢 LAYAK DIUJI"}:
        st.success(decision)
    elif decision == "🟡 KUMPULKAN DATA":
        st.warning(decision)
    else:
        st.error(decision)
    st.info(f"**Alasan:** {winner['decision_reason']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Product Score", f"{winner['score']}/100")
    c2.metric("Affiliate Score", f"{winner['affiliate_score']}/100")
    c3.metric("Content Score", f"{winner['content_score']}/100")
    st.metric("Confidence data", f"{winner['confidence']}%")
    st.metric("Data Quality", f"{winner['data_quality']}%")
    if winner["estimated_commission_per_sale"]:
        st.metric("Estimasi kotor / transaksi", f"Rp{winner['estimated_commission_per_sale']:,.0f}".replace(",", "."))
        st.caption("Ini hanya gross estimate = harga × tarif komisi. Payout aktual mengikuti skema affiliate dan nilai pembelian bersih.")
    else:
        st.warning("Komisi belum tersedia; estimasi komisi tidak dihitung.")
    if winner["missing_critical_fields"]:
        st.warning("Data kritis kurang: " + ", ".join(winner["missing_critical_fields"]))
    if winner.get("suspicious_flags"):
        st.warning("⚠️ Data perlu verifikasi:")
        for flag in winner["suspicious_flags"]:
            st.write("• " + flag)
    st.write(f"**Prioritas:** {winner['priority']} | **Faktor terlemah:** {winner['weakest_factor']}")
    st.subheader("🧠 Penilaian AAE")
    for factor, value in winner["breakdown"].items():
        st.write(f"**{factor}:** {value}/{FACTOR_MAX[factor]}")
    st.subheader("🎯 Strategi Konten")
    st.write(f"**Angle:** {winner['angle']}")
    st.write(f"**Hook 1–3 detik:** {winner['hook']}")
    st.write(f"**Script:** {winner['script_15_30s']}")
    st.write(f"**CTA:** {winner['cta']}")
    st.code(winner["caption"], language="text")
    st.write(f"**Gaya video:** {winner['video_style']}")


with shopee_tab:
    st.subheader("🔗 Analisa Produk Shopee")
    url = st.text_input("Link produk Shopee", placeholder="https://shopee.co.id/...")
    if st.button("🔍 Analisa Produk", type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Tempel link produk Shopee terlebih dahulu.")
        else:
            result = analyze_shopee_url(url)
            st.session_state.pop("shopee_score_result", None)
            if not result["ok"]:
                st.error(result["error"])
                if result.get("fallback"):
                    st.warning("Gunakan data manual untuk field yang belum terbaca otomatis.")
                if result.get("data"):
                    st.session_state["shopee_data"] = result["data"]
            else:
                st.session_state["shopee_data"] = result["data"]

    if "shopee_data" in st.session_state:
        data = st.session_state["shopee_data"]
        if data.get("missing_fields"):
            st.warning("Sebagian data belum terbaca otomatis. Lengkapi field yang kosong.")
        st.caption("Otomatis: " + (", ".join(data.get("auto_fields", [])) or "belum ada"))
        for warning in data.get("data_warnings", []):
            st.warning(warning)
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
        competition, _ = competition_input("shopee_competition")
        if st.button("🚀 Nilai Potensi Affiliate", use_container_width=True, key="score_shopee"):
            product = {"name": name, "category": category, "description": data.get("description", ""), "price": price, "commission_percent": commission, "rating": rating, "sales": sales, "review_count": review_count, "seller_rating": seller_rating, "problem": problem, "benefit": benefit, "target": target, "competition": competition, "sales_is_lower_bound": data.get("sales_is_lower_bound", False)}
            if not name:
                st.warning("Nama produk wajib diisi.")
            else:
                st.session_state["shopee_score_result"] = rank_products([product])[0]
        if "shopee_score_result" in st.session_state:
            show_result(st.session_state["shopee_score_result"])

with manual_tab:
    st.subheader("📊 Penilai Produk Affiliate")
    st.info("Masukkan data produk. Field ekonomi yang kosong sengaja tidak diberi angka contoh agar AAE tidak menciptakan data palsu.")
    count = st.number_input("Jumlah produk", min_value=1, max_value=10, value=3, step=1)
    products = []
    for i in range(int(count)):
        st.markdown(f"### Produk {i + 1}")
        name = st.text_input("Nama produk", key=f"name_{i}")
        category = st.text_input("Kategori", key=f"category_{i}")
        description = st.text_input("Deskripsi singkat", key=f"description_{i}")
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Harga (Rp)", min_value=0, value=0, step=1000, key=f"price_{i}")
            commission = st.number_input("Komisi (%)", min_value=0.0, value=0.0, step=0.5, key=f"commission_{i}")
        with col2:
            rating = st.number_input("Rating produk", min_value=0.0, max_value=5.0, value=0.0, step=0.1, key=f"rating_{i}")
            sales = st.number_input("Terjual", min_value=0, value=0, step=100, key=f"sales_{i}")
        review_count = st.number_input("Jumlah ulasan", min_value=0, value=0, step=10, key=f"reviews_{i}")
        seller_rating = st.number_input("Rating seller (opsional)", min_value=0.0, max_value=5.0, value=0.0, step=0.1, key=f"seller_{i}")
        competition, _ = competition_input(f"competition_{i}")
        problem = st.text_input("Masalah yang diselesaikan", key=f"problem_{i}")
        benefit = st.text_input("Manfaat utama", key=f"benefit_{i}")
        target = st.text_input("Target pembeli", key=f"target_{i}")
        if name:
            products.append({"name": name, "category": category, "description": description, "price": price, "commission_percent": commission, "rating": rating, "sales": sales, "review_count": review_count, "seller_rating": seller_rating, "competition": competition, "problem": problem, "benefit": benefit, "target": target})
    if st.button("🚀 Nilai & Pilih Produk", type="primary", use_container_width=True):
        st.session_state.pop("manual_ranked", None)
        if products:
            st.session_state["manual_ranked"] = rank_products(products)
        else:
            st.warning("Isi minimal 1 nama produk.")
    if "manual_ranked" in st.session_state:
        ranked = st.session_state["manual_ranked"]
        winner = ranked[0]
        st.success(f"🏆 Produk utama: {winner['product']} — Affiliate Score {winner['affiliate_score']}/100")
        st.subheader("🏆 Ranking Produk")
        for idx, item in enumerate(ranked, start=1):
            st.markdown(f"**#{idx} — {item['product']}**")
            st.write(f"Affiliate: **{item['affiliate_score']}/100** | Product: **{item['score']}/100** | Confidence: **{item['confidence']}%** | Keputusan: **{item['decision']}**")
            st.progress(min(int(item["affiliate_score"]), 100))
        show_result(winner)

st.divider()
st.caption("AAE v8.2 — Data Intelligence, suspicious-data detection, inferred content fields, heuristic competition, safer defaults, and expanded regression tests.")
