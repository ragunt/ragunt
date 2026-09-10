import json
from pathlib import Path

import streamlit as st

from src.aae_strategist import build_strategy

st.set_page_config(page_title="Arash Affiliate Engine", page_icon="🔥", layout="centered")

st.title("🔥 Arash Affiliate Engine")
st.caption("AAE-Strategist MVP — ubah data produk menjadi strategi konten affiliate.")

st.subheader("Input Produk")
name = st.text_input("Nama produk", "")
category = st.text_input("Kategori", "")
price = st.number_input("Harga (Rp)", min_value=0, value=49000, step=1000)
commission = st.number_input("Komisi (%)", min_value=0.0, value=8.0, step=0.5)
rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=4.8, step=0.1)
sales = st.number_input("Jumlah terjual", min_value=0, value=1000, step=100)
problem = st.text_input("Masalah yang diselesaikan", "")
benefit = st.text_input("Manfaat utama", "")
target = st.text_input("Target pembeli", "")

if st.button("🚀 Buat Strategi", type="primary"):
    if not name:
        st.warning("Isi nama produk dulu.")
    else:
        product = {
            "name": name,
            "category": category,
            "price": price,
            "commission_percent": commission,
            "rating": rating,
            "sales": sales,
            "problem": problem,
            "benefit": benefit,
            "target": target,
        }
        result = build_strategy(product)

        st.success(f"Skor peluang: {result['score']}/100")
        st.markdown("### 🎯 Angle")
        st.write(result["angle"])
        st.markdown("### ⚡ Hook 1–3 detik")
        st.write(result["hook"])
        st.markdown("### 🎬 Script 15–30 detik")
        st.write(result["script_15_30s"])
        st.markdown("### 🛒 CTA")
        st.write(result["cta"])
        st.markdown("### ✍️ Caption")
        st.code(result["caption"], language="text")
        st.markdown("### 🎥 Gaya Video")
        st.write(result["video_style"])

st.divider()
st.caption("MVP tahap 2. Belum mengambil data produk Shopee secara otomatis.")
