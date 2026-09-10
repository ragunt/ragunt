import re
from collections import Counter


CATEGORY_TARGETS = {
    "gamis": "wanita muslim yang mencari pakaian praktis",
    "abaya": "wanita muslim yang mencari busana longgar dan nyaman",
    "hijab": "wanita muslim yang membutuhkan hijab praktis",
    "fashion": "pembeli fashion yang mencari produk sesuai gaya dan kebutuhan",
    "sepatu": "pengguna yang mencari alas kaki nyaman dan sesuai aktivitas",
    "tas": "pengguna yang membutuhkan tas praktis dan fungsional",
    "skincare": "pengguna yang mencari perawatan kulit sesuai kebutuhannya",
    "beauty": "pengguna yang mencari produk kecantikan praktis",
    "dapur": "rumah tangga yang mencari solusi dapur praktis",
    "rumah": "rumah tangga yang ingin rumah lebih rapi dan praktis",
    "organizer": "orang yang ingin barang lebih rapi dan mudah ditemukan",
    "kabel": "pengguna gadget atau meja kerja yang ingin kabel lebih rapi",
    "gadget": "pengguna gadget yang membutuhkan aksesori fungsional",
    "hp": "pengguna smartphone yang membutuhkan aksesori praktis",
    "elektronik": "pengguna elektronik yang mencari solusi praktis",
}

PROBLEM_PATTERNS = [
    (r"anti.?kusut|tidak mudah kusut", "sulit menjaga barang tetap rapi"),
    (r"praktis|mudah dipakai|busui|menyusui", "membutuhkan produk yang praktis digunakan"),
    (r"rapi|organizer|penyimpanan", "barang mudah berantakan dan sulit ditata"),
    (r"kabel|cable", "kabel mudah berantakan dan sulit dijangkau"),
    (r"hemat|portable|mini|ringkas", "membutuhkan solusi yang ringkas dan efisien"),
    (r"nyaman|premium|lembut", "mencari produk yang lebih nyaman digunakan"),
    (r"airflow|adem|dingin", "membutuhkan produk yang terasa lebih nyaman saat digunakan"),
    (r"jerawat|acne|flek|kusam|kering", "memiliki kebutuhan perawatan kulit tertentu"),
]

BENEFIT_PATTERNS = [
    (r"praktis|mudah", "lebih praktis digunakan"),
    (r"rapi|organizer|penyimpanan", "membantu barang lebih rapi dan mudah ditemukan"),
    (r"hemat", "membantu penggunaan lebih efisien"),
    (r"nyaman|premium|lembut", "memberikan pengalaman penggunaan yang lebih nyaman"),
    (r"portable|mini|ringkas", "mudah dibawa dan tidak memakan banyak ruang"),
    (r"airflow|adem|dingin", "membantu penggunaan terasa lebih nyaman"),
    (r"anti.?kusut", "membantu menjaga tampilan tetap rapi"),
]


def _text(product):
    parts = [
        product.get("name", ""),
        product.get("description", ""),
        product.get("category", ""),
    ]
    return " ".join(str(p or "") for p in parts).strip().lower()


def infer_problem(product):
    existing = str(product.get("problem", "")).strip()
    if existing:
        return existing, "manual"
    text = _text(product)
    for pattern, result in PROBLEM_PATTERNS:
        if re.search(pattern, text, re.I):
            return result, "inferred"
    category = str(product.get("category", "")).lower()
    for key, target in CATEGORY_TARGETS.items():
        if key in text or key in category:
            return f"mencari solusi yang sesuai kebutuhan {key}", "inferred"
    return "belum cukup data untuk menentukan masalah utama", "unknown"


def infer_benefit(product):
    existing = str(product.get("benefit", "")).strip()
    if existing:
        return existing, "manual"
    text = _text(product)
    for pattern, result in BENEFIT_PATTERNS:
        if re.search(pattern, text, re.I):
            return result, "inferred"
    return "membantu kebutuhan utama pengguna", "inferred" if text else "unknown"


def infer_target(product):
    existing = str(product.get("target", "")).strip()
    if existing:
        return existing, "manual"
    text = _text(product)
    for key, target in CATEGORY_TARGETS.items():
        if key in text:
            return target, "inferred"
    return "calon pembeli yang membutuhkan produk ini", "inferred" if text else "unknown"


def enrich_product(product):
    enriched = dict(product)
    problem, problem_source = infer_problem(enriched)
    benefit, benefit_source = infer_benefit(enriched)
    target, target_source = infer_target(enriched)
    enriched["problem"] = problem if problem_source != "unknown" else enriched.get("problem", "")
    enriched["benefit"] = benefit if benefit_source != "unknown" else enriched.get("benefit", "")
    enriched["target"] = target if target_source != "unknown" else enriched.get("target", "")
    enriched["intelligence_sources"] = {
        "problem": problem_source,
        "benefit": benefit_source,
        "target": target_source,
    }
    return enriched


def detect_suspicious_data(product):
    flags = []
    sales = product.get("sales")
    sales_is_lower_bound = bool(product.get("sales_is_lower_bound"))
    if sales_is_lower_bound:
        flags.append("Terjual memakai lower-bound seperti 10RB+; jangan dianggap angka pasti.")
    rating = float(product.get("rating") or 0)
    reviews = float(product.get("review_count") or 0)
    if rating > 0 and reviews == 0:
        flags.append("Rating ada tetapi jumlah ulasan kosong; sumber data perlu diverifikasi.")
    if rating > 0 and reviews > 0 and reviews > (sales or 0) and sales > 0:
        flags.append("Jumlah ulasan melebihi terjual; kemungkinan field berasal dari sumber berbeda atau parsing keliru.")
    if product.get("price_is_range"):
        flags.append("Harga produk berupa rentang/varian; estimasi komisi memakai harga yang dipilih parser.")
    if product.get("seller_rating") and rating and abs(float(product["seller_rating"]) - rating) >= 0.5:
        flags.append("Rating seller dan rating produk berbeda signifikan; jangan dicampur.")
    return flags


def data_quality(product):
    enriched = enrich_product(product)
    flags = detect_suspicious_data(enriched)
    source_bonus = sum(1 for value in enriched.get("intelligence_sources", {}).values() if value == "manual")
    core = ["name", "price", "rating", "sales", "review_count", "category"]
    present = sum(1 for field in core if enriched.get(field) not in (None, "", 0))
    score = present / len(core) * 70 + source_bonus / 3 * 30
    score -= min(len(flags) * 8, 24)
    return round(max(0, min(100, score)), 1), flags


def estimate_competition(product):
    if product.get("competition") is not None and float(product.get("competition")) >= 0:
        return float(product.get("competition")), "manual"
    text = _text(product)
    terms = re.findall(r"\b[a-z0-9]+\b", text)
    counts = Counter(terms)
    repeated = sum(1 for _, count in counts.items() if count >= 2)
    score = min(10, 3 + repeated * 1.5)
    return round(score, 1), "heuristic"
