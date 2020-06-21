import csv
import json
from requests_html import HTMLSession

from get_product_links import get_product_urls

session = HTMLSession()
base_url = "https://www.epetdiscount.com"
collection_tag = input("Please enter collection url tag ie. dog-food-dry: ")
url = f"{base_url}/collections/{collection_tag}"

website = session.get(url)
total_items = website.html.find(".filters-toolbar__product-count", first=True).text.replace(" products", "")
if int(total_items) > 40:
    total_num_pages = website.html.search('<li class="pagination__text">\n    Page 1 of {total_num_pages}\n  </li>')['total_num_pages']
else:
    total_num_pages = 1
    
print(f" Pages: {total_num_pages} \t Records: {total_items}. \t Please Wait...")
product_urls = get_product_urls(session, url, total_num_pages)
page_count = 0
with open(f'{collection_tag}.csv', 'w', newline='',  encoding='utf-8') as csv_file:
    fieldnames = ["name", "vendor", "stock", "eur_price", "gbp_price", "modified_price", "description", "product_url", "image_url"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for product_url in product_urls:
        search_url = f"{base_url}{product_url}"
        product_page = session.get(search_url)
        product_name = product_page.html.find(".product-single__title", first=True).text
        product_thumbnails = product_page.html.find(".product-single__thumbnails-item")
        o_s_m = "This item is currently out of stock"
        stock = "0" if o_s_m in product_page.html.html else "1"
        img_url = product_page.html.search('property="og:image:secure_url" content={IMG_URL}">')['IMG_URL']
        print(img_url)
        eur_url = "https://api.exchangeratesapi.io/latest"
        api_page = session.get(eur_url)
        api_data = json.loads(api_page.html.text)
        eur_gbp_con = api_data["rates"]["GBP"]
        eur_price = product_page.html.find("#ProductPrice-product-template", first=True).text.replace("€", "")
        gbp_price = round(float(eur_price) * eur_gbp_con, 2)
        modified_price = round(gbp_price * 1.4, 2)
        product_dict = {
            "name": product_name,
            "vendor": product_page.html.find(".product-single__vendor", first=True).text,
            "stock": stock,
            "eur_price": eur_price,
            "gbp_price": gbp_price,
            "modified_price": modified_price,
            "description": product_page.html.find(".product_desc_trunc", first=True).text,
            "product_url": search_url,
            "image_url": img_url,
        }
        writer.writerow(product_dict)
        page_count += 1
        print(f" Product {page_count} / {total_items} done")

print(f" Finished, please look for {collection_tag}.csv")
