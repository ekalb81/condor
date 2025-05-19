import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import random
import logging
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('conditioner_scraper')

class ConditionerScraper:
    def __init__(self, retail_sites, mock_mode=False):
        """
        Initialize scraper with a list of retail websites

        Args:
            retail_sites: List of retail website URLs to scrape
        """
        self.retail_sites = retail_sites
        self.mock_mode = mock_mode
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        self.headers = {
            'User-Agent': self._get_random_user_agent()
        }
        self.results = []
        self.session = self._create_session()

    def _get_random_user_agent(self):
        """
        Get a random user agent from the list

        Returns:
            Random user agent string
        """
        return random.choice(self.user_agents)

    def _create_session(self):
        """
        Create a requests session with retry capabilities

        Returns:
            Requests session with retry configuration
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=5,  # Increased maximum number of retries
            backoff_factor=2,  # Increased exponential backoff factor
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
            allowed_methods=["GET"],
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _make_request(self, url):
        """
        Make a request with retry capabilities and rotating user agents

        Args:
            url: URL to request

        Returns:
            Response object or mock response if in mock mode
        """
        # If in mock mode, return a mock response
        if self.mock_mode:
            logger.info(f"Mock mode: Simulating request to {url}")
            from unittest.mock import MagicMock
            mock_response = MagicMock()
            mock_response.text = '<html><body><div class="product-name">Mock Product</div><div class="product-brand">Mock Brand</div></body></html>'
            mock_response.status_code = 200
            return mock_response

        # Update user agent for each request
        self.headers['User-Agent'] = self._get_random_user_agent()

        try:
            # Add additional headers to appear more like a browser
            self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            self.headers['Accept-Language'] = 'en-US,en;q=0.5'
            self.headers['Connection'] = 'keep-alive'
            self.headers['Upgrade-Insecure-Requests'] = '1'

            # Increased timeout
            response = self.session.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise

    def get_site_specific_rules(self, domain):
        """
        Get site-specific CSS selectors and rules for each website

        Args:
            domain: Website domain name

        Returns:
            Dictionary of selectors for that site
        """
        rules = {
            'sephora.com': {
                'search_url': 'https://www.sephora.com/search?keyword=hair%20conditioner',
                'product_links': '.css-ix8km1',
                'product_name': '.css-1pgnl76',
                'company': '.css-cjz2sh',
                'ingredients_selector': '#ingredients',
                'pagination': '.css-1kceze8'
            },
            'ulta.com': {
                'search_url': 'https://www.ulta.com/hair-care-products/hair-treatments/conditioner?N=26yd',
                'product_links': '.ProductCard__link',
                'product_name': '.Text-ds--title-3',
                'company': '.Text-ds--title-5',
                'ingredients_selector': '#product-ingredients',
                'pagination': '.Pagination__page-link'
            },
            'sallybeauty.com': {
                'search_url': 'https://www.sallybeauty.com/hair-care/shop-by-product/conditioner/',
                'product_links': '.product-tile-link',
                'product_name': '.product-name',
                'company': '.product-brand',
                'ingredients_selector': '.product-ingredients',
                'pagination': '.page-next'
            },
            'target.com': {
                'search_url': 'https://www.target.com/c/conditioner-hair-care-beauty/-/N-5xu0i',
                'product_links': 'a[data-test="product-title"]',
                'product_name': 'h1[data-test="product-title"]',
                'company': '[data-test="product-brand"]',
                'ingredients_selector': '[data-test="ingredients-content"]',
                'pagination': '.iUWCMa'
            }
        }

        # Get domain without www
        domain = domain.replace('www.', '')

        # Return default rules if site not in our list
        if domain not in rules:
            return {
                'search_url': f'https://{domain}/search?q=hair+conditioner',
                'product_links': 'a',
                'product_name': 'h1',
                'company': None,
                'ingredients_selector': None,
                'pagination': None
            }

        return rules[domain]

    def get_product_urls(self, site_url, max_pages=3, max_products=3):
        """
        Get product URLs from a retail site

        Args:
            site_url: Base URL of the retail site
            max_pages: Maximum number of search result pages to process
            max_products: Maximum number of products to collect

        Returns:
            List of product URLs
        """
        domain = urlparse(site_url).netloc
        rules = self.get_site_specific_rules(domain)
        search_url = rules['search_url']
        product_urls = []
        current_page = 1

        # If in mock mode, return mock product URLs
        if self.mock_mode:
            logger.info(f"Mock mode: Generating {max_products} mock product URLs for {domain}")
            for i in range(max_products):
                product_urls.append(f"{site_url}/mock-product-{i}")
            return product_urls

        while current_page <= max_pages and len(product_urls) < max_products:
            try:
                logger.info(f"Scanning page {current_page} of {domain}...")

                # Add delay to be respectful
                time.sleep(random.uniform(1.5, 3.5))  # Randomized delay to appear more human-like

                # Get search results page with retry mechanism
                response = self._make_request(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract product links
                links = soup.select(rules['product_links'])
                for link in links:
                    if len(product_urls) >= max_products:
                        break

                    href = link.get('href')
                    if href:
                        # Make sure we have absolute URLs
                        if not href.startswith('http'):
                            href = urljoin(site_url, href)
                        product_urls.append(href)

                # Try to find next page link
                if rules['pagination']:
                    # Try different pagination strategies
                    next_page = soup.select(rules['pagination'])
                    if next_page:
                        # Strategy 1: Last pagination element is next page
                        next_href = next_page[-1].get('href')

                        # Strategy 2: Look for elements with 'next' in text or class
                        if not next_href:
                            for page_link in next_page:
                                if page_link.text.lower().strip() in ['next', '›', '>', '»'] or \
                                   'next' in page_link.get('class', []) or \
                                   'next' in page_link.get('id', ''):
                                    next_href = page_link.get('href')
                                    break

                        # Strategy 3: Look for a page number higher than current
                        if not next_href:
                            for page_link in next_page:
                                try:
                                    page_num = int(page_link.text.strip())
                                    if page_num == current_page + 1:
                                        next_href = page_link.get('href')
                                        break
                                except (ValueError, TypeError):
                                    continue

                        if next_href:
                            search_url = urljoin(site_url, next_href)
                            current_page += 1
                            logger.info(f"Moving to page {current_page}")
                        else:
                            logger.info("No next page found")
                            break
                    else:
                        logger.info("No pagination elements found")
                        break
                else:
                    logger.info("No pagination selector defined for this site")
                    break

            except Exception as e:
                logger.error(f"Error getting product URLs from {domain}: {str(e)}")
                break

        return product_urls[:max_products]

    def scrape_product(self, product_url):
        """
        Scrape a single product page

        Args:
            product_url: URL of the product page

        Returns:
            Dictionary with product data
        """
        # If in mock mode, return mock product data
        if self.mock_mode:
            # Extract a number from the URL to create varied mock data
            mock_id = ''.join(filter(str.isdigit, product_url)) or '0'
            mock_id = int(mock_id[-1:]) if mock_id else 0

            mock_brands = ['Pantene', 'Herbal Essences', 'Dove', 'TRESemmé', 'L\'Oréal', 'Garnier', 'Head & Shoulders', 'Aussie']
            mock_types = ['Moisturizing', 'Volumizing', 'Color Protection', 'Damage Repair', 'Curl Defining', 'Smoothing']

            return {
                'product_name': f"{mock_brands[mock_id % len(mock_brands)]} {mock_types[mock_id % len(mock_types)]} Conditioner",
                'company': mock_brands[mock_id % len(mock_brands)],
                'ingredients': "Water, Cetearyl Alcohol, Behentrimonium Chloride, Fragrance, Cetyl Esters, Isopropyl Alcohol, Methylparaben, Propylparaben",
                'source_url': product_url,
                'retailer': urlparse(product_url).netloc
            }

        try:
            domain = urlparse(product_url).netloc
            rules = self.get_site_specific_rules(domain)

            # Add delay to be respectful
            time.sleep(random.uniform(1.5, 3.5))  # Randomized delay

            # Get product page with retry mechanism
            response = self._make_request(product_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract product name
            product_name = None
            name_element = soup.select_one(rules['product_name'])
            if name_element:
                product_name = name_element.text.strip()

            # Extract company name
            company = None
            if rules['company']:
                company_element = soup.select_one(rules['company'])
                if company_element:
                    company = company_element.text.strip()

            # Extract ingredients
            ingredients = None
            if rules['ingredients_selector']:
                ingredients_section = soup.select_one(rules['ingredients_selector'])
                if ingredients_section:
                    ingredients = ingredients_section.text.strip()
                    # Clean up the ingredients text
                    ingredients = re.sub(r'\s+', ' ', ingredients)
                    ingredients = ingredients.replace('Ingredients:', '').replace('INGREDIENTS:', '').strip()

            return {
                'product_name': product_name,
                'company': company,
                'ingredients': ingredients,
                'source_url': product_url,
                'retailer': domain
            }

        except Exception as e:
            logger.error(f"Error scraping {product_url}: {str(e)}")
            return None

    def run(self, max_products_per_site=5):
        """
        Run the scraper on all configured retail sites

        Args:
            max_products_per_site: Maximum number of products to scrape per site

        Returns:
            DataFrame with all product data
        """
        all_products = []

        for site in self.retail_sites:
            logger.info(f"\nProcessing {site}...")

            # Get product URLs
            product_urls = self.get_product_urls(site, max_products=max_products_per_site)
            logger.info(f"Found {len(product_urls)} product URLs")

            # Scrape each product
            for url in product_urls:
                logger.info(f"Scraping: {url}")
                product_data = self.scrape_product(url)
                if product_data:
                    all_products.append(product_data)

        # Create DataFrame and update self.results
        df = pd.DataFrame(all_products)
        self.results = all_products
        return df

    def save_to_csv(self, filename='hair_conditioners_data.csv', df=None):
        """
        Save results to CSV file

        Args:
            filename: Name of the CSV file to save
            df: Optional DataFrame to save. If None, uses self.results
        """
        if df is None:
            df = pd.DataFrame(self.results)

        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")


def main():
    import argparse

    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Scrape hair conditioner product information')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode (no real requests)')
    parser.add_argument('--max-products', type=int, default=5, help='Maximum products per site')
    parser.add_argument('--output', type=str, default='hair_conditioners_data.csv', help='Output CSV filename')
    args = parser.parse_args()

    # Configure retail websites
    retail_sites = [
        "https://www.sephora.com",
        "https://www.ulta.com",
        "https://www.sallybeauty.com",
        "https://www.target.com"
    ]

    try:
        # Initialize and run scraper
        logger.info("Starting conditioner scraper...")
        logger.info(f"Mock mode: {'Enabled' if args.mock else 'Disabled'}")

        scraper = ConditionerScraper(retail_sites, mock_mode=args.mock)
        df = scraper.run(max_products_per_site=args.max_products)

        # Save results using the class method
        scraper.save_to_csv(args.output, df)
        logger.info(f"\nScraping complete! Collected data for {len(df)} products")
        logger.info(f"Data saved to {args.output}")
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred during scraping: {str(e)}")

if __name__ == "__main__":
    main()