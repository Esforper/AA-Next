import requests
import xml.etree.ElementTree as ET

url = "https://www.aa.com.tr/tr/rss/default?cat=guncel"

# RSS verisini çek
response = requests.get(url)
response.encoding = "utf-8"  # Türkçe karakterler düzgün çıksın
xml_data = response.text

# XML parse et
root = ET.fromstring(xml_data)

# Namespace (bazı RSS'lerde gerekli)
namespaces = {"media": "http://search.yahoo.com/mrss/"}

print("=== RSS'deki tüm alanlar ===\n")

# item'ları gez
for i, item in enumerate(root.findall(".//item"), start=1):
    print(f"\n--- Haber {i} ---")
    for child in item:
        # XML element adı ve text
        tag = child.tag.split("}")[-1]  # namespace varsa temizle
        text = (child.text or "").strip()
        print(f"{tag}: {text}")

        # eğer attribute varsa onları da yaz
        if child.attrib:
            print(f"  Attributes: {child.attrib}")
