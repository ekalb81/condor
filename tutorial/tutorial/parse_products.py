import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def clean_text(text):
    """Clean up text by removing extra whitespace."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_name(soup, meta_title):
    """Extract product name from the page."""
    # Try to get name from h1 tag
    name = soup.select_one('h1.product-full__name')
    if name:
        name = name.get_text().strip()
    
    # If not found or is "Sign in", try meta title
    if not name or name == "Sign in":
        if meta_title:
            # Remove website name if present
            name = re.sub(r'\s*\|\s*Bumble and bumble\.?$', '', meta_title)
    
    # If still not found, try to extract from URL
    if not name:
        # This would be implemented based on your URL structure
        pass
    
    return clean_text(name)

def extract_options(soup):
    """Extract product options (size and price)."""
    options = []
    
    # Try to find size selector items
    option_blocks = soup.select('li.product-full__size-selector-item')
    for block in option_blocks:
        size = block.get_text().strip()
        price_elem = soup.select_one('span.product-full__price, div.product-full__price')
        if size and price_elem:
            options.append({
                "size": size,
                "price": price_elem.get_text().strip()
            })
    
    # If no options found, try alternative selectors
    if not options:
        sizes = [opt.get_text().strip() for opt in soup.select('select option')]
        price = soup.select_one('span.product-full__price, div.product-full__price')
        if sizes and price:
            price_text = price.get_text().strip()
            for size in sizes:
                if size and not size.startswith('Select'):
                    options.append({
                        "size": size,
                        "price": price_text
                    })
    
    # If still no options, try to find a price anywhere
    if not options:
        price_pattern = r'\$\d+\.\d{2}'
        price_matches = re.findall(price_pattern, soup.get_text())
        if price_matches:
            options.append({
                "size": "Standard",
                "price": price_matches[0]
            })
    
    return options

def extract_ingredients(soup):
    """Extract ingredients from the page."""
    ingredients = []
    
    # Method 1: Look for ingredients section
    ingredient_section = soup.select_one('h4:-soup-contains("INGREDIENTS"), h3:-soup-contains("INGREDIENTS")')
    if ingredient_section and ingredient_section.find_next():
        ingredients_text = ingredient_section.find_next().get_text().strip()
        if ingredients_text:
            ingredients.append(ingredients_text)
    
    # Method 2: Look for ingredient list pattern in product details
    if not ingredients:
        details_text = ' '.join([d.get_text() for d in soup.select('div.product-full__detail-content')])
        if details_text:
            # Look for ingredient list that typically starts with Water\Aqua\Eau
            ingredients_match = re.search(r'(?:Ingredients:|ingredients:)?\s*(Water\\Aqua\\Eau.+?)(?:<|$)', details_text)
            if ingredients_match:
                ingredients.append(ingredients_match.group(1).strip())
            else:
                # Try to find a list of chemical ingredients
                ingredients_match = re.search(r'(?:[A-Z][a-z]+\s*,\s*){3,}[A-Z][a-z]+', details_text)
                if ingredients_match:
                    ingredients.append(ingredients_match.group(0).strip())
    
    return ', '.join(ingredients)

def extract_other_info(soup, category):
    """Extract other product information."""
    other_info = []
    
    # Add category if available
    if category:
        other_info.append(f"CATEGORY\n{category}")
    
    # Try to extract product description
    description = soup.select_one('div.product-full__description')
    if description:
        description_text = description.get_text().strip()
        if description_text:
            other_info.append(f"DESCRIPTION\n{description_text}")
    
    # Extract product details
    details = soup.select_one('div.product-full__detail-content')
    if details:
        details_text = details.get_text().strip()
        
        # Remove ingredient list if present
        ingredients_pattern = r'(?:Ingredients:|ingredients:)?\s*(Water\\Aqua\\Eau.+?)(?:<|$)'
        details_text = re.sub(ingredients_pattern, '', details_text)
        
        # Remove chemical ingredient lists
        chemical_pattern = r'(?:[A-Z][a-z]+\s*,\s*){3,}[A-Z][a-z]+'
        details_text = re.sub(chemical_pattern, '', details_text)
        
        # Clean up the text
        details_text = clean_text(details_text)
        
        if details_text:
            other_info.append(f"DETAILS\n{details_text}")
    
    return "\n\n".join(other_info)

def parse_product(product_data):
    """Parse a single product from raw data."""
    url = product_data.get('url', '')
    raw_html = product_data.get('raw_html', '')
    meta_title = product_data.get('meta_title', '')
    category = product_data.get('category', '')
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    # Extract product information
    name = extract_name(soup, meta_title)
    options = extract_options(soup)
    ingredients = extract_ingredients(soup)
    other = extract_other_info(soup, category)
    
    # Return parsed product data
    return {
        'url': url,
        'name': name,
        'options': options,
        'ingredients': ingredients,
        'other': other
    }

def main():
    parser = argparse.ArgumentParser(description='Parse raw product data from Bumble and Bumble website')
    parser.add_argument('input_file', help='Path to the raw product data file (JSONL format)')
    parser.add_argument('output_file', help='Path to save the parsed product data (JSON format)')
    args = parser.parse_args()
    
    # Read raw product data
    raw_products = []
    with open(args.input_file, 'r', encoding='utf-8') as f:
        for line in f:
            raw_products.append(json.loads(line))
    
    # Parse each product
    parsed_products = []
    for raw_product in raw_products:
        parsed_product = parse_product(raw_product)
        parsed_products.append(parsed_product)
    
    # Save parsed product data
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_products, f, indent=2)
    
    print(f"Parsed {len(parsed_products)} products and saved to {args.output_file}")

if __name__ == "__main__":
    main()
