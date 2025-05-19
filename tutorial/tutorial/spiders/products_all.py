import scrapy
import re
from tutorial.items import ProductItem

class ProductsAllSpider(scrapy.Spider):
    name = "products_all"
    allowed_domains = ["bumbleandbumble.com"]
    start_urls = [
        "https://www.bumbleandbumble.com/shop-all-hair-products"
    ]
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'products.json',
        # Optionally throttle for good etiquette
        'DOWNLOAD_DELAY': 1
    }

    def parse(self, response):
        # Find product links on category/listing pages
        product_links = response.css('a[href^="/product/"]::attr(href)').getall()
        for link in product_links:
            url = response.urljoin(link.split('#')[0])  # Remove fragment
            yield scrapy.Request(url, callback=self.parse_product)

        # Pagination (if exists)
        next_page = response.css('a.pagination__next::attr(href), a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

        # Discover category/collection pages from nav/menu if needed (optional)
        category_links = response.css('a[href^="/shop-by-concern/"]::attr(href), a[href^="/collections/"]::attr(href)').getall()
        for link in category_links:
            yield response.follow(link, self.parse)

    def parse_product(self, response):
        # Deduplicate using canonical URL
        canonical = response.css('link[rel="canonical"]::attr(href)').get()
        if hasattr(self, 'seen'):
            if canonical in self.seen:
                return
            self.seen.add(canonical)
        else:
            self.seen = {canonical}

        # Extract product name from URL if not available on page
        name = response.css('h1.product-full__name::text, h3::text').get()
        if not name or name == "Sign in":
            name = response.css('meta[property="og:title"]::attr(content)').get()
            if not name:
                # Extract product name from URL path
                url_path = response.url.split('/')
                if len(url_path) > 5:
                    # Get the last part of the URL path and replace hyphens with spaces
                    product_name = url_path[-1].replace('-', ' ')
                    name = product_name.title()

        # Clean up the product name
        if name:
            # Remove website name if present
            name = re.sub(r'\s*\|\s*Bumble and bumble\.?$', '', name)
            # Clean up any extra whitespace
            name = re.sub(r'\s+', ' ', name).strip()

        # Extract product options (size and price)
        options = []
        option_blocks = response.css('li.product-full__size-selector-item')
        for block in option_blocks:
            size = block.css('::text').get()
            price_elem = response.css('span.product-full__price::text, div.product-full__price::text').get()
            if size and price_elem:
                options.append({
                    "size": size.strip(),
                    "price": price_elem.strip()
                })

        # If no options found, try alternative selectors
        if not options:
            sizes = response.css('select option::text').getall()
            price = response.css('span.product-full__price::text, div.product-full__price::text').get()
            if sizes and price:
                for size in sizes:
                    if size.strip() and not size.strip().startswith('Select'):
                        options.append({
                            "size": size.strip(),
                            "price": price.strip()
                        })

            # If still no options, extract from URL path
            if not options:
                # Try to find price in the page content
                price_text = response.css('*::text').re_first(r'\$\d+\.\d{2}')
                if price_text:
                    options.append({
                        "size": "Standard",
                        "price": price_text
                    })

        # Extract ingredients - try multiple methods
        ingredients_list = []

        # Method 1: Try to find ingredients section
        ingredients = response.xpath(
            "//h4[contains(translate(text(), 'INGREDIENTS', 'ingredients'), 'ingredients')]/following-sibling::div[1]//text() | "
            "//h3[contains(translate(text(), 'INGREDIENTS', 'ingredients'), 'ingredients')]/following-sibling::div[1]//text()"
        ).getall()
        if ingredients:
            ingredients_list = [i.strip() for i in ingredients if i.strip()]

        # Method 2: Try to extract ingredients from product details
        if not ingredients_list:
            # Look for ingredient list pattern in product details
            details_text = ' '.join(response.css('div.product-full__detail-content::text').getall())
            if details_text:
                # Look for ingredient list that typically starts after application instructions
                ingredients_match = re.search(r'(?:Ingredients:|ingredients:)?\s*(Water\\Aqua\\Eau.+?)(?:<|$)', details_text)
                if ingredients_match:
                    ingredients_list = [ingredients_match.group(1).strip()]
                else:
                    # Try to find a list of chemical ingredients
                    ingredients_match = re.search(r'(?:[A-Z][a-z]+\s*,\s*){3,}[A-Z][a-z]+', details_text)
                    if ingredients_match:
                        ingredients_list = [ingredients_match.group(0).strip()]

        ingredients = ', '.join(ingredients_list)

        # Extract other product information
        other_info = []

        # Try to extract product description
        description = response.css('div.product-full__description::text').get()
        if description:
            description = description.strip()
            if description:
                other_info.append(f"DESCRIPTION\n{description}")

        # Extract product details from URL path if other methods fail
        if not other_info:
            url_path = response.url.split('/')
            if len(url_path) > 5:
                category = url_path[-2].replace('-', ' ').title()
                other_info.append(f"CATEGORY\n{category}")

        # Extract any text content that might be useful
        product_text = response.css('div.product-full__detail-content::text').getall()
        if product_text:
            product_text = [t.strip() for t in product_text if t.strip()]
            if product_text:
                # Join the text and clean it up
                details_text = ' '.join(product_text)

                # Remove ingredient list if present
                ingredients_pattern = r'(?:Ingredients:|ingredients:)?\s*(Water\\Aqua\\Eau.+?)(?:<|$)'
                details_text = re.sub(ingredients_pattern, '', details_text)

                # Remove chemical ingredient lists
                chemical_pattern = r'(?:[A-Z][a-z]+\s*,\s*){3,}[A-Z][a-z]+'
                details_text = re.sub(chemical_pattern, '', details_text)

                # Clean up the text
                details_text = re.sub(r'\s+', ' ', details_text).strip()

                # Add to other info if not empty
                if details_text:
                    other_info.append(f"DETAILS\n{details_text}")

        other = "\n\n".join(other_info)

        # Create a ProductItem
        product = ProductItem(
            url=response.url,
            name=name.strip() if name else "",
            options=options,
            ingredients=ingredients,
            other=other
        )

        yield product
