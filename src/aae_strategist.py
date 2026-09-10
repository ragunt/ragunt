import json
import sys


def score_product(product):
    """Score affiliate potential from 0-100 using product market signals."""
    rating = float(product.get("rating", 0))
    sales = float(product.get("sales", 0))
    commission = float(product.get("commission_percent", 0))
    price = float(product.get("price", 0))
    problem = bool(product.get("problem"))
    benefit = bool(product.get("benefit"))

    rating_score = min(max(rating / 5 * 20, 0), 20)
    sales_score = min(max(sales / 10000 * 25, 0), 25)
    commission_score = min(max(commission / 10 * 20, 0), 20)

    # Affordable impulse-buy range gets the highest score.
    if 20000 <= price <= 150000:
        price_score = 15
    elif 10000 <= price < 20000 or 150000 < price <= 300000:
        price_score = 10
    else:
        price_score = 5

    problem_score = 10 if problem else 0
    benefit_score = 10 if benefit else 0

    return round(
        rating_score + sales_score + commission_score + price_score
        + problem_score + benefit_score,
        1,
    )


def score_label(score):
    if score >= 80:
        return "🔥 Sangat layak"
    if score >= 65:
        return "🟢 Layak diuji"
    if score >= 50:
        return "🟡 Perlu seleksi"
    return "🔴 Kurang menarik"


def score_breakdown(product):
    rating = float(product.get("rating", 0))
    sales = float(product.get("sales", 0))
    commission = float(product.get("commission_percent", 0))
    price = float(product.get("price", 0))
    return {
        "Rating": round(min(rating / 5 * 20, 20), 1),
        "Penjualan": round(min(sales / 10000 * 25, 25), 1),
        "Komisi": round(min(commission / 10 * 20, 20), 1),
        "Harga": 15 if 20000 <= price <= 150000 else (10 if 10000 <= price <= 300000 else 5),
        "Masalah jelas": 10 if product.get("problem") else 0,
        "Manfaat jelas": 10 if product.get("benefit") else 0,
    }


def build_strategy(product):
    score = score_product(product)
    name = product["name"]
    problem = product.get("problem", "ada masalah yang bisa diselesaikan")
    benefit = product.get("benefit", "lebih praktis")
    target = product.get("target", "calon pembeli")

    return {
        "product": name,
        "score": score,
        "label": score_label(score),
        "breakdown": score_breakdown(product),
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


def rank_products(products):
    """Return products ranked from strongest to weakest affiliate opportunity."""
    return sorted(
        (build_strategy(product) for product in products),
        key=lambda item: item["score"],
        reverse=True,
    )


def main(path):
    with open(path, "r", encoding="utf-8") as f:
        products = json.load(f)

    for item in rank_products(products):
        print(json.dumps(item, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/aae_strategist.py examples/products.json")
        raise SystemExit(1)
    main(sys.argv[1])
