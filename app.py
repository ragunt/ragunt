import streamlit as st

from src.aae_strategist import build_strategy, rank_products

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")

st.title("🔥 Arash Affiliate Engine")
st.caption("Pilih produk yang paling berpotensi sebelum bikin konten affiliate.")

st.subheader("📊 Penilai Produk Affiliate")
st.info(
    "Masukkan data beberapa produk. AAE akan memberi skor 0–100, "
    "mengurutkan produk, dan menunjukkan alasan kenapa produk tersebut layak diuji."
)

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
        products.append({
            "name": name,
            "category": category,
            "price": price,
            "commission_percent": commission,
            "rating": rating,
            "sales": sales,
            "problem": problem,
            "benefit": benefit,
            "target": target,
        })

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
        breakdown = winner["breakdown"]
        for factor, value in breakdown.items():
            st.write(f"**{factor}:** {value}")

        st.subheader("🎯 Strategi Konten Produk Terpilih")
        st.write(f"**Angle:** {winner['angle']}")
        st.write(f"**Hook 1–3 detik:** {winner['hook']}")
        st.write(f"**Script 15–30 detik:** {winner['script_15_30s']}")
        st.write(f"**CTA:** {winner['cta']}")
        st.code(winner["caption"], language="text")
        st.write(f"**Gaya video:** {winner['video_style']}")

st.divider()
st.caption("AAE MVP v3 — saat ini penilaian memakai data yang dimasukkan pengguna. Integrasi sumber data produk otomatis dapat ditambahkan berikutnya.")
