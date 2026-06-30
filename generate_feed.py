"""
Bio Bone - Gerador de Feed XML para Meta Catalog
Lê o XML da Loja Integrada e converte para o formato aceito pela Meta.
"""

import re
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone

SOURCE_URL = "https://www.biobonebrazil.com.br/xml/41b49/facebook.xml"
OUTPUT_FILE = "docs/feed.xml"


def get_tag(xml, tag):
    """Retorna o conteúdo da primeira ocorrência de uma tag."""
    escaped = tag.replace(":", "\\:").replace(".", "\\.")
    pattern = rf"<{tag}[^>]*>([\s\S]*?)</{tag}>"
    match = re.search(pattern, xml)
    return clean(match.group(1)) if match else ""


def clean(text):
    """Remove CDATA e espaços extras."""
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    return text.strip()


def escape_xml(text):
    """Escapa caracteres especiais para XML."""
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def fix_price(price):
    """Garante o formato 'XX.XX BRL' que a Meta exige."""
    if not price:
        return ""
    price = price.strip()
    if "BRL" in price:
        return price
    # Converte vírgula para ponto se necessário
    price = price.replace(",", ".")
    return f"{price} BRL"


def fetch_source():
    """Baixa o XML da Loja Integrada."""
    print(f"Buscando feed de: {SOURCE_URL}")
    req = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MetaFeedBot/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_items(xml_text):
    """Extrai todos os <item> do XML."""
    pattern = r"<item>([\s\S]*?)</item>"
    return re.findall(pattern, xml_text)


def convert_item(item_xml):
    """Converte um item do formato Loja Integrada para o formato Meta."""
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

    # Pular itens sem campos obrigatórios
    if not id_ or not link or not title or not price:
        return None

    lines = [
        "    <item>",
        f"      <g:id>{escape_xml(id_)}</g:id>",
        f"      <g:title>{escape_xml(title)}</g:title>",
        f"      <g:description>{escape_xml(desc)}</g:description>",
        f"      <g:link>{escape_xml(link)}</g:link>",
        f"      <g:image_link>{escape_xml(image)}</g:image_link>",
        f"      <g:availability>{escape_xml(avail)}</g:availability>",
        f"      <g:condition>{escape_xml(condition)}</g:condition>",
        f"      <g:price>{escape_xml(price)}</g:price>",
    ]

    if sale:
        lines.append(f"      <g:sale_price>{escape_xml(sale)}</g:sale_price>")
    if brand:
        lines.append(f"      <g:brand>{escape_xml(brand)}</g:brand>")
    if ptype:
        lines.append(f"      <g:product_type>{escape_xml(ptype)}</g:product_type>")
    if gtin:
        lines.append(f"      <g:gtin>{escape_xml(gtin)}</g:gtin>")

    lines.append("    </item>")
    return "\n".join(lines)


def build_feed(items_xml):
    """Monta o XML final no formato aceito pela Meta."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    header = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:g="http://base.google.com/ns#" version="2.0">
  <channel>
    <title>Bio Bone - Catálogo de Produtos</title>
    <link>https://www.biobonebrazil.com.br</link>
    <description>Catálogo de produtos Bio Bone para Meta Ads</description>
    <lastBuildDate>{now}</lastBuildDate>"""

    footer = """  </channel>
</rss>"""

    return header + "\n" + "\n".join(items_xml) + "\n" + footer


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

    feed = build_feed(valid)

    import os
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(feed)

    print(f"Feed salvo em: {OUTPUT_FILE}")
    print(f"Total de produtos no feed Meta: {len(valid)}")


if __name__ == "__main__":
    main()
