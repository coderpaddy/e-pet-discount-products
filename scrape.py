import csv

from requests_html import HTMLSession

from get_product_links import get_product_urls

session = HTMLSession()
base_url = "https://www.epetdiscount.com"
collection_tag = input("Please enter collection url tag ie. dog-food-dry: ")
url = f"{base_url}/collections/{collection_tag}"

website = session.get(url)
total_items = website.html.search('<span class="filters-toolbar__product-count">{total_items} products</span>')['total_items']
total_num_pages = website.html.search('<li class="pagination__text">\n    Page 1 of {total_num_pages}\n  </li>')['total_num_pages']
print(f" Pages: {total_num_pages} \t Records: {total_items}. \t Please Wait...")
product_urls = get_product_urls(session, url, total_num_pages)
page_count = 0
with open(f'{collection_tag}.csv', 'w', newline='') as csv_file:
    fieldnames = ["name", "vendor", "price", "description", "product_url", "image_urls"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for product_url in product_urls:
        search_url = f"{base_url}{product_url}"
        product_page = session.get(search_url)
        product_name = product_page.html.find(".product-single__title", first=True).text
        product_thumbnails = product_page.html.find(".product-single__thumbnails-item")
        new_list = []
        for x in product_thumbnails:
            new_list.append(x.find("a", first=True))
        prod_links = [x.attrs['href'] for x in new_list]
        product_dict = {
            "name": product_name,
            "vendor": product_page.html.find(".product-single__vendor", first=True).text,
            "price": product_page.html.find("#ProductPrice-product-template", first=True).text,
            "description": product_page.html.find(".product_desc_trunc", first=True).text,
            "product_url": search_url,
            "image_urls": [f"https:{x}" for x in prod_links]
        }
        writer.writerow(product_dict)
        page_count += 1
        print(f" Product {page_count} / {total_items} done")

print(f" Finished, please look for {collection_tag}.csv")