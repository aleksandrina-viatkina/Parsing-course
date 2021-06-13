CATEGORY_XPATH = '//a[@class = "rubricator-list-item-link-12kOm"][@title="Все квартиры"]/@href'

ADV_LINK_XPATH = '//div[contains(@class, "iva-item-titleStep-2bjuh")]//a[contains(@class, "link-link-39EVK")]/@href'

ADV_PAGE = {
    'title': '//span[@class="title-info-title-text"]//text()',
    'price_rub': '//div[contains(@class, "item-price-wrapper")]//span[@itemprop = "price"]/@content',
    'address': '//span[@class = "item-address__string"]//text()',
    'apart_params': '//ul[@class="item-params-list"]/li',
    'author_url': '//div[@class = "seller-info-name"]//@a/@href'
}
