def get_product_urls(session, url, total_num_pages):
    item_links = []
    for i in range(1, int(total_num_pages) + 1):
        page_url = f"{url}?page={i}"
        website = session.get(page_url)
        grid = website.html.find("#Collection")[0]
        items = grid.find(".grid-view-item__title > .grid-view-item__link")
        for item in items:
            item_links.append(item.attrs['href'])
    return item_links