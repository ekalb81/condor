# Bumble and Bumble Product Scraper

This project contains Scrapy spiders for scraping product information from the Bumble and Bumble website.

## Two-Step Process

The scraping process is split into two steps:

1. **Collect raw data**: Use the `products_raw` spider to collect raw HTML data from product pages
2. **Parse the data**: Use the `parse_products.py` script to parse the raw data into structured format

This approach has several advantages:
- Reduces the number of requests to the website
- Allows you to refine the parsing process without making additional requests
- Makes it easier to debug and improve the data extraction

## How to Use

### Step 1: Collect Raw Data

Run the `products_raw` spider to collect raw HTML data:

```bash
cd tutorial
python -m scrapy crawl products_raw
```

This will save the raw data to `products_raw.jsonl` in the tutorial directory.

### Step 2: Parse the Raw Data

Run the parsing script to extract structured data from the raw HTML:

```bash
cd tutorial
python -m tutorial.parse_products products_raw.jsonl products_parsed.json
```

This will parse the raw data and save the structured data to `products_parsed.json`.

## Data Structure

The parsed data includes the following fields for each product:

- `url`: The URL of the product page
- `name`: The name of the product
- `options`: A list of product options (size and price)
- `ingredients`: The ingredients of the product
- `other`: Other product information, including category and details

## Requirements

- Python 3.6+
- Scrapy
- BeautifulSoup4

Install the required packages:

```bash
pip install scrapy beautifulsoup4
```
