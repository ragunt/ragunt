import json
import sys


def score_product(product):
    """Simple MVP score; replace with real model/data later."""
    rating_score = min(float(product.get("rating", 0)) / 5 * 25, 25)
    sales_score = min(float(product.get("sales", 0)) / 10000 * 25, 25)
    commission_score = min(float(product.get("commission_percent", 0)) / 10 * 20, 20)
    price_score = 15 if 15000 <= float(product.get("price", 0)) <= 150000 else 8
    problem_score = 15 if product.get("problem") and product.get("benefit") else 5
    return round(rating_score + sales_score + commission_score + price_score + problem_score, 1)


def build_strategy(product):
    score = score_product(product)
    name = product["name"]
    problem = product.get("problem", "ada masalah yang bisa diselesaikan")
    benefit = product.get("benefit", "lebih praktis")
    target = product.get("target", "calon pembeli")

    return {
        "product": name,
        "score": score,
        "angle": f"Solusi praktis untuk {problem}",
        "hook": f"Kalau kamu masih {problem}, coba lihat ini.",
        "script_15_30s": (
            f"Kalau kamu masih {problem}, coba lihat {name}. "
            f"Produk ini bisa bantu {benefit}. "
            f"Cocok buat {target}. "
            "Sebelum beli, cek harga dan ulasan terbaru."
        ),
        "cta": "Cek produknya dan bandingkan dengan kebutuhanmu.",
        "caption": f"Solusi simpel: {benefit}. #shopeeaffiliate #racunshopee #rekomendasiproduk",
        "video_style": "B-roll produk + teks besar + cut cepat setiap 2–3 detik",
    }


def main(path):
    with open(path, "r", encoding="utf-8") as f:
        products = json.load(f)

    strategies = sorted((build_strategy(p) for p in products), key=lambda x: x["score"], reverse=True)
    for item in strategies:
        print(json.dumps(item, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/aae_strategist.py examples/products.json")
        raise SystemExit(1)
    main(sys.argv[1])
