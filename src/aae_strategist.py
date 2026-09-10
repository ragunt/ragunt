import json
import re
import sys


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _has(value):
    return bool(str(value or "").strip())


def _sales_score(sales):
    # Diminishing returns: 10k+ sold is strong, but sales alone must not dominate.
    sales = max(sales, 0)
    if sales >= 10000:
        return 25.0
    return round(min(sales / 10000 * 25, 25), 1)


def _commission_score(commission):
    commission = max(commission, 0)
    if commission >= 10:
        return 20.0
    return round(min(commission / 10 * 20, 20), 1)


def _price_score(price):
    if 20000 <= price <= 150000:
        return 15.0
    if 10000 <= price < 20000 or 150000 < price <= 300000:
        return 10.0
    if price > 0:
        return 5.0
    return 0.0


def _content_score(product):
    score = 0
    problem = str(product.get("problem", "")).lower()
    benefit = str(product.get("benefit", "")).lower()
    category = str(product.get("category", "")).lower()

    if _has(problem):
        score += 5
    if _has(benefit):
        score += 5

    # Extra points for products that are easy to demonstrate visually.
    visual_terms = [
        "baju", "kemeja", "blouse", "fashion", "sepatu", "tas", "aksesoris",
        "dapur", "rumah", "organizer", "kabel", "lampu", "beauty", "skincare",
        "alat", "gadget", "hp", "elektronik", "kebersihan",
    ]
    if any(term in category or term in problem or term in benefit for term in visual_terms):
        score += 5

    # A visible before/after or simple demo is valuable for short-form content.
    demo_terms = ["rapi", "hemat", "cepat", "praktis", "sebelum", "sesudah", "solusi", "mudah"]
    if any(term in problem or term in benefit for term in demo_terms):
        score += 5

    return min(score, 20)


def _competition_score(product):
    # Prefer an explicitly supplied competition estimate. Lower competition is better.
    competition = _num(product.get("competition", -1), -1)
    if competition >= 0:
        return round(max(0, min(10, 10 - competition)), 1)

    # Without market-wide competitor data, use a conservative neutral score.
    return 5.0


def _risk_score(product):
    score = 10.0
    rating = _num(product.get("rating"))
    seller_rating = _num(product.get("seller_rating"))
    category = str(product.get("category", "")).lower()
    price = _num(product.get("price"))

    if rating and rating < 4.5:
        score -= 3
    if seller_rating and seller_rating < 4.5:
        score -= 2
    if any(term in category for term in ["fashion", "pakaian", "kemeja", "sepatu"]):
        score -= 2  # size/fit/return risk
    if 0 < price < 10000:
        score -= 1  # quality expectation risk for ultra-low price

    return max(0.0, min(10.0, score))


def _confidence(product):
    fields = [
        ("name", 1),
        ("price", 1),
        ("rating", 1),
        ("sales", 1),
        ("review_count", 1),
        ("commission_percent", 1),
        ("problem", 1),
        ("benefit", 1),
        ("target", 1),
    ]
    complete = sum(1 for field, _ in fields if _has(product.get(field)) or _num(product.get(field)) > 0)
    return round(complete / len(fields) * 100, 1)


def _priority(score, confidence):
    if score >= 85 and confidence >= 80:
        return "🔥 PRIORITAS TINGGI"
    if score >= 70:
        return "🟢 LAYAK DIUJI"
    if score >= 55:
        return "🟡 PERLU DATA"
    return "🔴 SKIP"


def score_breakdown(product):
    rating = _num(product.get("rating"))
    sales = _num(product.get("sales"))
    commission = _num(product.get("commission_percent"))
    price = _num(product.get("price"))

    demand = round(min(rating / 5 * 10, 10) + _sales_score(sales) * 0.6, 1)
    demand = min(demand, 25)
    economics = round(_commission_score(commission), 1)
    product_quality = round(min(rating / 5 * 15, 15), 1)
    content = float(_content_score(product))
    competition = _competition_score(product)
    risk = _risk_score(product)

    return {
        "Demand": demand,
        "Affiliate Economics": economics,
        "Product Quality": product_quality,
        "Content Potential": content,
        "Competition": competition,
        "Risk": risk,
    }


def score_product(product):
    """Score affiliate opportunity from 0-100, not just product popularity."""
    breakdown = score_breakdown(product)
    return round(sum(breakdown.values()), 1)


def score_label(score):
    if score >= 85:
        return "🔥 PRIORITAS TINGGI"
    if score >= 70:
        return "🟢 LAYAK DIUJI"
    if score >= 55:
        return "🟡 PERLU DATA"
    return "🔴 SKIP"


def build_strategy(product):
    score = score_product(product)
    name = product.get("name", "Produk")
    problem = product.get("problem", "ada masalah yang bisa diselesaikan")
    benefit = product.get("benefit", "lebih praktis")
    target = product.get("target", "calon pembeli")
    price = _num(product.get("price"))
    commission = _num(product.get("commission_percent"))
    estimated_commission = round(price * commission / 100, 0) if price and commission else 0
    confidence = _confidence(product)

    return {
        "product": name,
        "score": score,
        "label": score_label(score),
        "priority": _priority(score, confidence),
        "confidence": confidence,
        "estimated_commission_per_sale": estimated_commission,
        "breakdown": score_breakdown(product),
        "angle": f"Solusi praktis untuk {problem}",
        "hook": f"Kalau kamu masih {problem}, coba lihat ini.",
        "script_15_30s": (
            f"Kalau kamu masih {problem}, coba lihat {name}. "
            f"Produk ini bisa bantu {benefit}. "
            f"Cocok buat {target}. "
            "Sebelum beli, cek harga, ulasan, dan variasinya."
        ),
        "cta": "Cek produknya dan bandingkan dengan kebutuhanmu.",
        "caption": f"Solusi simpel: {benefit}. #shopeeaffiliate #racunshopee #rekomendasiproduk",
        "video_style": "B-roll/demo produk + teks besar + cut cepat setiap 2–3 detik",
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
