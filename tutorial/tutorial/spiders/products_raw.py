import scrapy
from tutorial.items import ProductItem

class ProductsRawSpider(scrapy.Spider):
    name = "products_raw"
    allowed_domains = ["bumbleandbumble.com"]
    start_urls = [
        "https://www.bumbleandbumble.com/shop-all-hair-products"
    ]
    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'products_raw.jsonl',
        # Optionally throttle for good etiquette
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        # Find product links on category/listing pages
        product_links = response.css('a[href^="/product/"]::attr(href)').getall()
        for link in product_links:
            url = response.urljoin(link.split('#')[0])  # Remove fragment
            yield scrapy.Request(url, callback=self.save_raw_product)

        # Pagination (if exists)
        next_page = response.css('a.pagination__next::attr(href), a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

        # Discover category/collection pages from nav/menu if needed (optional)
        category_links = response.css('a[href^="/shop-by-concern/"]::attr(href), a[href^="/collections/"]::attr(href)').getall()
        for link in category_links:
            yield response.follow(link, self.parse)

    def save_raw_product(self, response):
        # Deduplicate using canonical URL
        canonical = response.css('link[rel="canonical"]::attr(href)').get()
        if hasattr(self, 'seen'):
            if canonical in self.seen:
                return
            self.seen.add(canonical)
        else:
            self.seen = {canonical}

        # Extract category from URL path
        url_path = response.url.split('/')
        category = ""
        if len(url_path) > 5:
            category = url_path[-2].replace('-', ' ').title()

        # Save raw HTML content for later parsing
        raw_html = response.body.decode('utf-8')
        
        # Extract basic metadata
        meta_title = response.css('meta[property="og:title"]::attr(content)').get()
        meta_description = response.css('meta[property="og:description"]::attr(content)').get()
        
        # Create a ProductItem with raw data
        product = ProductItem(
            url=response.url,
            raw_html=raw_html,
            meta_title=meta_title,
            meta_description=meta_description,
            category=category
        )
        
        yield product
