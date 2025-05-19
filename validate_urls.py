#!/usr/bin/env python
"""
URL Validator for sources.json

This script validates all URLs in the sources.json file to ensure they are properly formatted
and optionally checks if they are reachable.

Usage:
    python validate_urls.py [--check-reachable] [--timeout SECONDS] [--verbose] [--browser-check] [--headless]

Options:
    --check-reachable    Check if URLs are reachable (makes HTTP requests)
    --timeout SECONDS    Timeout for HTTP requests in seconds (default: 10)
    --verbose            Show detailed information for each URL
    --browser-check      Open URLs that return 403/timeout in a browser for manual verification
    --headless           Use headless browser for URLs that fail initial reachability test
"""

import json
import os
import sys
import time
import argparse
import requests
import webbrowser
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Selenium imports for headless browser testing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


def load_sources(file_path):
    """Load sources from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading sources.json: {str(e)}")
        sys.exit(1)


def validate_url_format(url):
    """Validate URL format."""
    parsed_url = urlparse(url)

    # Check URL has scheme and netloc
    if not parsed_url.scheme:
        return False, "URL missing scheme"

    if not parsed_url.netloc:
        return False, "URL missing domain"

    # Check URL uses HTTPS
    if parsed_url.scheme != 'https':
        return False, "URL should use HTTPS"

    return True, "Valid URL format"


def check_url_with_headless_browser(url, timeout=10):
    """Check if URL is reachable using a headless browser."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Disable logging
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = None
    try:
        # Suppress the ChromeDriverManager output
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(timeout)

        # Navigate to the URL
        driver.get(url)

        # Check if page loaded successfully
        if driver.title or len(driver.page_source) > 100:
            return True, f"Loaded successfully with headless browser (title: {driver.title[:30]}...)"
        else:
            return False, "Page loaded but appears empty"

    except TimeoutException:
        return False, "Timeout loading page in headless browser"
    except WebDriverException as e:
        error_msg = str(e)
        # Handle specific errors
        if "net::ERR_NAME_NOT_RESOLVED" in error_msg:
            return False, "Domain name could not be resolved"
        elif "net::ERR_CONNECTION_TIMED_OUT" in error_msg:
            return False, "Connection timed out"
        elif "zip file" in error_msg.lower():
            # For the Kérastase error, try a different approach
            try:
                # Try with requests as a fallback
                response = requests.get(url, timeout=timeout,
                                       headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
                if 200 <= response.status_code < 300:
                    return True, f"Loaded successfully with requests fallback (status: {response.status_code})"
            except:
                pass
            return False, f"Browser error: {error_msg[:100]}..."
        else:
            return False, f"Browser error: {error_msg[:100]}..."
    finally:
        if driver:
            driver.quit()


def check_url_reachable(brand, url, timeout=10):
    """Check if URL is reachable."""
    # More browser-like headers to avoid detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    try:
        # Try GET request with full headers
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)

        status_code = response.status_code
        if 200 <= status_code < 300:
            return True, f"Status code: {status_code}"
        elif status_code == 403:
            # Many sites return 403 for bot protection but work in browsers
            return False, f"Status code: 403 (May be bot protection - try browser)"
        else:
            return False, f"Status code: {status_code}"
    except requests.RequestException as e:
        return False, str(e)


def validate_source(source, check_reachable=False, timeout=10, verbose=False, browser_check=False, use_headless=False):
    """Validate a single source."""
    brand = source.get('brand', 'Unknown')
    url = source.get('url', '')

    if not url:
        print(f"❌ {brand}: Missing URL")
        return False, None

    # Validate URL format
    format_valid, format_message = validate_url_format(url)
    if not format_valid:
        print(f"❌ {brand}: {format_message} - {url}")
        return False, None

    # Check if URL is reachable
    if check_reachable:
        reachable, reachable_message = check_url_reachable(brand, url, timeout)

        # If initial check fails and headless browser option is enabled, try with headless browser
        if not reachable and use_headless and ("403" in reachable_message or
                                              "timeout" in reachable_message.lower() or
                                              "failed to resolve" in reachable_message.lower()):
            if verbose:
                print(f"🔄 {brand}: Retrying with headless browser - {url}")

            headless_reachable, headless_message = check_url_with_headless_browser(url, timeout)

            if headless_reachable:
                if verbose:
                    print(f"✅ {brand}: {url} - {headless_message}")
                return True, None
            elif verbose:
                print(f"❌ {brand}: Headless browser check failed - {headless_message} - {url}")

        if not reachable:
            error_message = f"❌ {brand}: Unreachable - {reachable_message} - {url}"
            print(error_message)

            # Return the URL for browser check if it's a 403 error or timeout
            if browser_check and ("403" in reachable_message or
                                 "timeout" in reachable_message.lower() or
                                 "failed to resolve" in reachable_message.lower()):
                return False, (brand, url, reachable_message)
            return False, None
        elif verbose:
            print(f"✅ {brand}: {url} - {reachable_message}")
    elif verbose:
        print(f"✅ {brand}: {url} - {format_message}")

    return True, None


def main():
    parser = argparse.ArgumentParser(description='Validate URLs in sources.json')
    parser.add_argument('--check-reachable', action='store_true', help='Check if URLs are reachable')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout for HTTP requests in seconds')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information for each URL')
    parser.add_argument('--browser-check', action='store_true', help='Open URLs that return 403/timeout in a browser for manual verification')
    parser.add_argument('--headless', action='store_true', help='Use headless browser for URLs that fail initial reachability test')
    args = parser.parse_args()

    # Load sources
    file_path = os.path.join('tutorial', 'sources.json')
    sources = load_sources(file_path)

    print(f"Validating {len(sources)} URLs from sources.json...")
    if args.check_reachable:
        print("Checking URL reachability (this may take a while)...")
        if args.headless:
            print("Using headless browser for URLs that fail initial check...")

    # Validate all sources
    valid_count = 0
    invalid_count = 0
    browser_check_urls = []

    if args.check_reachable:
        # Use ThreadPoolExecutor for parallel requests
        with ThreadPoolExecutor(max_workers=5 if args.headless else 10) as executor:
            futures = {
                executor.submit(
                    validate_source,
                    source,
                    args.check_reachable,
                    args.timeout,
                    args.verbose,
                    args.browser_check,
                    args.headless
                ): source
                for source in sources
            }

            for future in as_completed(futures):
                source = futures[future]
                try:
                    result, browser_check_info = future.result()
                    if result:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        if browser_check_info:
                            browser_check_urls.append(browser_check_info)
                except Exception as e:
                    print(f"❌ {source.get('brand', 'Unknown')}: Error - {str(e)}")
                    invalid_count += 1
    else:
        # Sequential validation for format only
        for source in sources:
            result, _ = validate_source(
                source,
                args.check_reachable,
                args.timeout,
                args.verbose,
                args.browser_check,
                args.headless
            )
            if result:
                valid_count += 1
            else:
                invalid_count += 1

    # Print summary
    print(f"\nValidation complete: {valid_count} valid, {invalid_count} invalid URLs")

    # Print detailed summary if there are invalid URLs
    if invalid_count > 0 and browser_check_urls:
        print("\nInvalid URLs that may need manual verification:")
        for brand, url, error in browser_check_urls:
            print(f"  - {brand}: {url}")
            print(f"    Error: {error}")

        print("\nPossible solutions:")
        print("1. Try accessing these URLs in a regular browser to verify if they're actually valid")
        print("2. Check if the domain has changed or if the URL needs to be updated")
        print("3. For timeouts, try increasing the timeout value with --timeout")
        print("4. For 403 errors, the site may have strict bot protection that even headless browsers can't bypass")

    # Open problematic URLs in browser if requested
    if args.browser_check and browser_check_urls:
        print("\nOpening problematic URLs in browser for manual verification...")
        for brand, url, error in browser_check_urls:
            print(f"Opening {brand}: {url} ({error})")
            webbrowser.open(url)
            time.sleep(1)  # Pause between opening URLs to avoid overwhelming the browser

    # Return non-zero exit code if any URLs are invalid
    return 0 if invalid_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
