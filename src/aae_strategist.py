import json
import sys

from src.data_intelligence import data_quality, detect_suspicious_data, enrich_product, estimate_competition

FACTOR_MAX = {
    "Demand": 20,
    "Affiliate Economics": 25,
    "Product Quality": 15,
    "Content Potential": 20,
    "Competition": 10,
    "Risk": 10,
}


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _has(value):
    return bool(str(value or "").strip())


def _sales_score(sales):
    sales = max(_num(sales), 0)
    if sales >= 10000:
        return 20.0
    return round(sales / 10000 * 20, 1)


def _economics_score(product):
    commission = max(_num(product.get("commission_percent")), 0)
    price = max(_num(product.get("price")), 0)
    payout = price * commission / 100
    rate_points = min(commission / 10 * 15, 15)
    payout_points = min(payout / 5000 * 10, 10)
    return round(rate_points + payout_points, 1)


def _content_score(product):
    score = 0
    problem = str(product.get("problem", "")).lower()
    benefit = str(product.get("benefit", "")).lower()
    category = str(product.get("category", "")).lower()
    if _has(problem):
        score += 5
    if _has(benefit):
        score += 5
    visual_terms = ["baju", "gamis", "kemeja", "blouse", "fashion", "sepatu", "tas", "beauty", "skincare", "dapur", "rumah", "organizer", "kabel", "lampu", "gadget", "hp", "elektronik", "kebersihan"]
    if any(term in category or term in problem or term in benefit for term in visual_terms):
        score += 5
    demo_terms = ["rapi", "hemat", "cepat", "praktis", "sebelum", "sesudah", "solusi", "mudah", "nyaman"]
    if any(term in problem or term in benefit for term in demo_terms):
        score += 5
    return min(score, 20)


def _competition_score(product):
    competition = _num(product.get("competition", -1), -1)
    return round(max(0, min(10, 10 - competition)), 1) if competition >= 0 else 5.0


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
        score -= 2
    if 0 < price < 10000:
        score -= 1
    if detect_suspicious_data(product):
        score -= min(2.0, len(detect_suspicious_data(product)) * 0.5)
    return max(0.0, min(10.0, score))


def _confidence(product):
    quality, flags = data_quality(product)
    return round(max(0.0, quality - min(len(flags) * 2, 10)), 1)


def score_breakdown(product):
    product = enrich_product(product)
    rating = _num(product.get("rating"))
    sales = _num(product.get("sales"))
    demand = min(round(rating / 5 * 6 + _sales_score(sales) * 0.7, 1), 20)
    return {
        "Demand": demand,
        "Affiliate Economics": _economics_score(product),
        "Product Quality": round(min(rating / 5 * 15, 15), 1),
        "Content Potential": float(_content_score(product)),
        "Competition": _competition_score(product),
        "Risk": _risk_score(product),
    }


def score_product(product):
    return round(sum(score_breakdown(product).values()), 1)


def affiliate_score(product):
    """Return a normalized 0-100 score for affiliate earning potential."""
    breakdown = score_breakdown(product)
    weights = {
        "Affiliate Economics": 0.40,
        "Demand": 0.20,
        "Content Potential": 0.20,
        "Competition": 0.10,
        "Product Quality": 0.05,
        "Risk": 0.05,
    }
    score = sum((breakdown[factor] / FACTOR_MAX[factor]) * weight for factor, weight in weights.items()) * 100
    return round(max(0.0, min(100.0, score)), 1)


def content_score(product):
    return round(_content_score(enrich_product(product)) / FACTOR_MAX["Content Potential"] * 100, 1)


def score_label(score):
    if score >= 85:
        return "🔥 PRIORITAS TINGGI"
    if score >= 70:
        return "🟢 LAYAK DIUJI"
    if score >= 55:
        return "🟡 PERLU DATA"
    return "🔴 SKIP"


def _missing_critical_fields(product):
    checks = {
        "Harga": _num(product.get("price")) > 0,
        "Rating produk": _num(product.get("rating")) > 0,
        "Terjual": _num(product.get("sales")) > 0,
        "Komisi": _num(product.get("commission_percent")) > 0,
        "Masalah": _has(product.get("problem")),
        "Manfaat": _has(product.get("benefit")),
    }
    return [label for label, complete in checks.items() if not complete]


def _weakest_factor(breakdown):
    return min(breakdown, key=lambda factor: breakdown[factor] / FACTOR_MAX[factor])


def decision(product, score, confidence, breakdown):
    missing = _missing_critical_fields(product)
    commission = _num(product.get("commission_percent"))
    aff = affiliate_score(product)
    if score < 55 or (aff < 45 and confidence >= 80):
        return "🔴 SKIP", "Peluang affiliate belum cukup menarik setelah memperhitungkan ekonomi, demand, konten, dan persaingan.", missing
    if missing or confidence < 80 or commission <= 0:
        reasons = []
        if missing:
            reasons.append("data kritis belum lengkap: " + ", ".join(missing))
        if confidence < 80:
            reasons.append(f"confidence baru {confidence}%")
        return "🟡 KUMPULKAN DATA", "; ".join(reasons) + ".", missing
    if aff >= 70 and score >= 65:
        return "🔥 AMBIL & TES", f"Affiliate Score {aff}/100 menunjukkan kombinasi uang, demand, konten, dan kompetisi cukup menarik untuk dites.", missing
    if aff >= 55:
        return "🟢 LAYAK DIUJI", f"Affiliate Score {aff}/100 cukup menarik, tetapi belum masuk prioritas utama.", missing
    return "🟡 KUMPULKAN DATA", f"Affiliate Score baru {aff}/100; cari produk dengan ekonomi atau potensi konten yang lebih kuat.", missing


def build_strategy(product):
    product = enrich_product(product)
    if _num(product.get("competition"), -1) < 0:
        competition, competition_source = estimate_competition(product)
        product["competition"] = competition
    else:
        competition_source = "manual"
    score = score_product(product)
    aff_score = affiliate_score(product)
    cont_score = content_score(product)
    name = product.get("name", "Produk")
    problem = product.get("problem", "ada masalah yang bisa diselesaikan")
    benefit = product.get("benefit", "lebih praktis")
    target = product.get("target", "calon pembeli")
    price = _num(product.get("price"))
    commission = _num(product.get("commission_percent"))
    estimated_commission = round(price * commission / 100, 0) if price and commission else 0
    confidence = _confidence(product)
    breakdown = score_breakdown(product)
    weakest = _weakest_factor(breakdown)
    decision_label, decision_reason, missing_critical = decision(product, score, confidence, breakdown)
    quality, suspicious_flags = data_quality(product)
    return {
        "product": name,
        "score": score,
        "label": score_label(score),
        "affiliate_score": aff_score,
        "content_score": cont_score,
        "decision": decision_label,
        "decision_reason": decision_reason,
        "missing_critical_fields": missing_critical,
        "priority": "🔥 PRIORITAS UTAMA" if aff_score >= 80 else ("🟢 LAYAK DIUJI" if aff_score >= 60 else "🟡 DATA / OPTIMASI"),
        "confidence": confidence,
        "data_quality": quality,
        "suspicious_flags": suspicious_flags,
        "intelligence_sources": product.get("intelligence_sources", {}),
        "competition_source": competition_source,
        "estimated_commission_per_sale": estimated_commission,
        "weakest_factor": weakest,
        "breakdown": breakdown,
        "angle": f"Solusi praktis untuk {problem}",
        "hook": f"Kalau kamu masih {problem}, coba lihat ini.",
        "script_15_30s": f"Kalau kamu masih {problem}, coba lihat {name}. Produk ini bisa bantu {benefit}. Cocok buat {target}. Sebelum beli, cek harga, ulasan, dan variasinya.",
        "cta": "Cek produknya dan bandingkan dengan kebutuhanmu.",
        "caption": f"Solusi simpel: {benefit}. #shopeeaffiliate #racunshopee #rekomendasiproduk",
        "video_style": "B-roll/demo produk + teks besar + cut cepat setiap 2–3 detik",
    }


def rank_products(products):
    return sorted((build_strategy(product) for product in products), key=lambda item: (item["affiliate_score"], item["score"]), reverse=True)


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
