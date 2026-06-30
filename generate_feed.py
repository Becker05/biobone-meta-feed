"""
Bio Bone - Gerador de Feed CSV para Meta Catalog
Lê o XML da Loja Integrada e converte para CSV aceito pela Meta.
"""

import re
import csv
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime, timezone

SOURCE_URL = "https://www.biobonebrazil.com.br/xml/41b49/facebook.xml"
OUTPUT_FILE = "docs/feed.csv"


def get_tag(xml, tag):
    pattern = rf"<{re.escape(tag)}[^>]*>([\s\S]*?)</{re.escape(tag)}>"
    match = re.search(pattern, xml)
    return clean(match.group(1)) if match else ""


def clean(text):
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    return text.strip()


def fix_price(price):
    if not price:
        return ""
    price = price.strip()
    if "BRL" in price:
        return price
    price = price.replace(",", ".")
    return f"{price} BRL"


def fetch_source():
    print(f"Buscando feed de: {SOURCE_URL}")
    req = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MetaFeedBot/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_items(xml_text):
    pattern = r"<item>([\s\S]*?)</item>"
    return re.findall(pattern, xml_text)


def convert_item(item_xml):
    id_       = get_tag(item_xml, "g:id")
    title     = get_tag(item_xml, "title")
    desc      = get_tag(item_xml, "description") or title
    link      = get_tag(item_xml, "link")
    image     = get_tag(item_xml, "g:image_link")
    price     = fix_price(get_tag(item_xml, "g:price"))
    sale      = fix_price(get_tag(item_xml, "g:sale_price"))
    avail     = get_tag(item_xml, "g:availability") or "in stock"
    condition = get_tag(item_xml, "g:condition") or "new"
    brand     = get_tag(item_xml, "g:brand") or "Bio Bone"
    ptype     = get_tag(item_xml, "g:product_type")
    gtin      = get_tag(item_xml, "g:gtin")

    if not id_ or not link or not title or not price:
        return None

    return {
        "id":           id_,
        "title":        title,
        "description":  desc,
        "availability": avail,
        "condition":    condition,
        "price":        price,
        "sale_price":   sale,
        "link":         link,
        "image_link":   image,
        "brand":        brand,
        "product_type": ptype,
        "gtin":         gtin,
    }


def main():
    try:
        raw_xml = fetch_source()
    except urllib.error.URLError as e:
        print(f"Erro ao buscar o feed: {e}")
        sys.exit(1)

    raw_items = parse_items(raw_xml)
    print(f"Itens encontrados no feed original: {len(raw_items)}")

    converted = [convert_item(item) for item in raw_items]
    valid = [item for item in converted if item is not None]
    skipped = len(raw_items) - len(valid)

    print(f"Itens convertidos: {len(valid)}")
    if skipped:
        print(f"Itens ignorados (campos obrigatórios ausentes): {skipped}")

    os.makedirs("docs", exist_ok=True)

    fieldnames = [
        "id", "title", "description", "availability", "condition",
        "price", "sale_price", "link", "image_link", "brand",
        "product_type", "gtin"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(valid)

    print(f"Feed salvo em: {OUTPUT_FILE}")
    print(f"Total de produtos: {len(valid)}")


if __name__ == "__main__":
    main()
