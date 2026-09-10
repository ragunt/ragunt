import json
import re
from html import unescape
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

SHOPEE_HOSTS = {"shopee.co.id", "www.shopee.co.id"}


def is_shopee_url(url):
    try:
        parsed = urlparse(str(url).strip())
        return parsed.scheme in {"http", "https"} and parsed.netloc.lower() in SHOPEE_HOSTS
    except Exception:
        return False


def _first_text(soup, selectors):
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            value = node.get("content") or node.get_text(" ", strip=True)
            if value:
                return unescape(value).strip()
    return ""


def _number(value):
    if value is None:
        return 0
    text = str(value).strip().lower()
    match = re.search(r"([0-9]+(?:[.,][0-9]+)?)\s*(rb|ribu|k|jt|juta|m)?", text)
    if not match:
        return 0
    raw = match.group(1)
    suffix = match.group(2) or ""
    if "," in raw and "." in raw:
        raw = raw.replace(".", "") if raw.rfind(".") > raw.rfind(",") else raw.replace(",", "")
        if raw.count(","):
            raw = raw.replace(",", ".")
    elif "," in raw:
        parts = raw.split(",")
        raw = raw.replace(",", ".") if len(parts[-1]) <= 2 else raw.replace(",", "")
    elif "." in raw:
        parts = raw.split(".")
        raw = raw.replace(".", ".") if len(parts[-1]) <= 2 else raw.replace(".", "")
    try:
        number = float(raw)
    except ValueError:
        return 0
    multiplier = {"rb": 1000, "ribu": 1000, "k": 1000, "jt": 1000000, "juta": 1000000, "m": 1000000}.get(suffix, 1)
    return int(number * multiplier)


def _price(value):
    if value is None:
        return 0
    digits = re.sub(r"[^0-9]", "", str(value))
    return int(digits) if digits else 0


def _json_ld(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or tag.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and (item.get("@type") == "Product" or "name" in item):
                return item
    return {}


def _extract_sales_and_reviews(page_text):
    sales = 0
    review_count = 0
    sales_lower_bound = False
    for pattern in [
        r"([0-9][0-9.,]*\s*(?:rb|ribu|k|jt|juta|m)?\+?)\s*(?:terjual|sold)",
        r"terjual\s*([0-9][0-9.,]*\s*(?:rb|ribu|k|jt|juta|m)?\+?)",
    ]:
        match = re.search(pattern, page_text, re.I)
        if match:
            raw = match.group(1)
            sales_lower_bound = "+" in raw
            sales = _number(raw)
            break
    for pattern in [
        r"([0-9][0-9.,]*\s*(?:rb|ribu|k|jt|juta|m)?)\s*(?:ulasan|penilaian|review)",
        r"(?:ulasan|penilaian|review)\s*([0-9][0-9.,]*\s*(?:rb|ribu|k|jt|juta|m)?)",
    ]:
        match = re.search(pattern, page_text, re.I)
        if match:
            review_count = _number(match.group(1))
            break
    return sales, review_count, sales_lower_bound


def _extract_category(soup):
    for selector in ['meta[property="product:category"]', 'meta[name="category"]']:
        value = _first_text(soup, [selector])
        if value:
            return value
    breadcrumb = soup.select_one("nav")
    if breadcrumb:
        text = breadcrumb.get_text(" > ", strip=True)
        if text:
            return text[:200]
    return ""


def analyze_shopee_url(url, timeout=15):
    """Best-effort public Shopee metadata extraction; never bypasses access controls."""
    if not is_shopee_url(url):
        return {"ok": False, "error": "Masukkan URL produk Shopee Indonesia yang valid."}
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }
    try:
        response = requests.get(url.strip(), headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code >= 400:
            return {"ok": False, "error": f"Halaman Shopee tidak bisa diakses otomatis (HTTP {response.status_code}).", "fallback": True}
    except requests.RequestException as exc:
        return {"ok": False, "error": f"Gagal mengambil halaman Shopee: {exc}", "fallback": True}

    soup = BeautifulSoup(response.text, "html.parser")
    ld = _json_ld(soup)
    page_text = soup.get_text(" ", strip=True)
    name = ld.get("name", "") or _first_text(soup, ['meta[property="og:title"]', 'meta[name="twitter:title"]', "title"])
    description = ld.get("description", "") or _first_text(soup, ['meta[property="og:description"]', 'meta[name="description"]'])
    image = ld.get("image", "") or _first_text(soup, ['meta[property="og:image"]'])
    offers = ld.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = _price(offers.get("price", 0)) if isinstance(offers, dict) else 0
    rating = 0.0
    aggregate = ld.get("aggregateRating", {})
    if isinstance(aggregate, dict):
        try:
            rating = float(aggregate.get("ratingValue", 0))
        except (TypeError, ValueError):
            rating = 0.0
    if not price:
        match = re.search(r"Rp\s?([0-9.]+)", page_text)
        if match:
            price = _price(match.group(1))
    if not rating:
        match = re.search(r"([0-5](?:[.,][0-9])?)\s*(?:dari\s*5|/5)", page_text, re.I)
        if match:
            rating = float(match.group(1).replace(",", "."))
    sales, review_count, sales_lower_bound = _extract_sales_and_reviews(page_text)
    category = _extract_category(soup)
    data = {
        "name": name, "price": price, "rating": rating, "sales": sales,
        "review_count": review_count, "category": category, "image": image,
        "description": description, "commission_percent": 0, "problem": "",
        "benefit": "", "target": "", "seller_rating": 0, "source_url": url.strip(),
        "sales_is_lower_bound": sales_lower_bound,
    }
    data["missing_fields"] = [field for field in ("name", "price", "rating", "sales", "review_count", "category") if not data[field]]
    data["auto_fields"] = [field for field in ("name", "price", "rating", "sales", "review_count", "category", "image") if data.get(field)]
    if sales_lower_bound:
        data["data_warnings"] = ["Angka terjual bertanda + adalah batas bawah, bukan jumlah penjualan pasti."]
    else:
        data["data_warnings"] = []
    if not data["name"] and not data["price"] and not data["rating"]:
        return {"ok": False, "error": "Halaman berhasil diakses, tetapi data produk tidak terbaca. Shopee mungkin mengirim halaman dinamis atau membatasi akses otomatis.", "fallback": True, "data": data}
    return {"ok": True, "data": data}
