import unittest
import json
import requests
from urllib.parse import urlparse
import os

class TestSourcesJson(unittest.TestCase):
    """Test cases for validating the sources.json file."""

    def setUp(self):
        """Load the sources.json file before each test."""
        # Use the correct path to sources.json
        file_path = os.path.join('tutorial', 'sources.json')
        with open(file_path, 'r') as f:
            self.sources = json.load(f)

    def test_sources_is_list(self):
        """Test that sources.json contains a list."""
        self.assertIsInstance(self.sources, list)
        self.assertGreater(len(self.sources), 0)

    def test_sources_have_required_fields(self):
        """Test that each source has the required fields."""
        for source in self.sources:
            self.assertIn('brand', source)
            self.assertIn('url', source)
            self.assertIsInstance(source['brand'], str)
            self.assertIsInstance(source['url'], str)

    def test_urls_are_valid_format(self):
        """Test that each URL is properly formatted."""
        for source in self.sources:
            url = source['url']
            parsed_url = urlparse(url)

            # Check URL has scheme and netloc
            self.assertTrue(parsed_url.scheme, f"URL missing scheme: {url}")
            self.assertTrue(parsed_url.netloc, f"URL missing domain: {url}")

            # Check URL uses HTTPS
            self.assertEqual(parsed_url.scheme, 'https', f"URL should use HTTPS: {url}")

    def test_urls_are_reachable(self):
        """Test that each URL is reachable (returns a 200-299 status code).

        Note: This test is commented out by default as it makes actual HTTP requests,
        which can be slow and might fail due to network issues. Uncomment it when you
        want to perform a full validation of all URLs.
        """
        # Skip this test by default to avoid making HTTP requests
        self.skipTest("Skipping URL reachability test to avoid making HTTP requests")

        timeout = 5  # seconds
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for source in self.sources:
            url = source['url']
            brand = source['brand']

            try:
                response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)

                # If HEAD request fails, try GET
                if response.status_code >= 400:
                    response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)

                status_code = response.status_code
                self.assertTrue(
                    200 <= status_code < 300,
                    f"URL for {brand} returned status code {status_code}: {url}"
                )
            except requests.RequestException as e:
                self.fail(f"Failed to connect to {url} for {brand}: {str(e)}")

    def test_bumble_and_bumble_url(self):
        """Test specifically for the Bumble and bumble URL.

        This test checks if the Bumble and bumble URL is valid and properly formatted.
        """
        # Find the Bumble and bumble entry
        bumble_entry = None
        for source in self.sources:
            if source['brand'].lower() == 'bumble and bumble':
                bumble_entry = source
                break

        # Verify that Bumble and bumble exists in the sources
        self.assertIsNotNone(bumble_entry, "Bumble and bumble entry not found in sources.json")

        # Check the URL format
        url = bumble_entry['url']
        parsed_url = urlparse(url)

        # Check URL has scheme and netloc
        self.assertTrue(parsed_url.scheme, f"URL missing scheme: {url}")
        self.assertTrue(parsed_url.netloc, f"URL missing domain: {url}")

        # Check URL uses HTTPS
        self.assertEqual(parsed_url.scheme, 'https', f"URL should use HTTPS: {url}")

        # Check domain is correct
        self.assertEqual(parsed_url.netloc, 'www.bumbleandbumble.com',
                         f"Domain should be www.bumbleandbumble.com, got {parsed_url.netloc}")

        # Check that the URL doesn't end with a specific path that's known to be invalid
        self.assertNotEqual(url, 'https://www.bumbleandbumble.com/products',
                           "URL should not be the invalid path /products")

    def test_bumble_and_bumble_url_reachable(self):
        """Test that the Bumble and bumble URL is reachable.

        This test makes an actual HTTP request to verify the URL is accessible.
        """
        # Find the Bumble and bumble entry
        bumble_entry = None
        for source in self.sources:
            if source['brand'].lower() == 'bumble and bumble':
                bumble_entry = source
                break

        self.assertIsNotNone(bumble_entry, "Bumble and bumble entry not found in sources.json")

        url = bumble_entry['url']
        timeout = 10  # seconds
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)

            # If HEAD request fails, try GET
            if response.status_code >= 400:
                response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)

            status_code = response.status_code
            self.assertTrue(
                200 <= status_code < 300,
                f"Bumble and bumble URL returned status code {status_code}: {url}"
            )
        except requests.RequestException as e:
            self.fail(f"Failed to connect to Bumble and bumble URL {url}: {str(e)}")

    def test_virtue_url(self):
        """Test specifically for the Virtue URL.

        This test checks if the Virtue URL is valid and reachable.
        """
        # Find the Virtue entry
        virtue_entry = None
        for source in self.sources:
            if source['brand'].lower() == 'virtue':
                virtue_entry = source
                break

        self.assertIsNotNone(virtue_entry, "Virtue entry not found in sources.json")

        # Check the URL format
        url = virtue_entry['url']
        self.assertEqual(url, "https://virtuelabs.com/", "Virtue URL should be https://virtuelabs.com/")

        # Check if the URL is reachable
        timeout = 10  # seconds
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)

            # If HEAD request fails, try GET
            if response.status_code >= 400:
                response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)

            status_code = response.status_code
            self.assertTrue(
                200 <= status_code < 300,
                f"Virtue URL returned status code {status_code}: {url}"
            )
        except requests.RequestException as e:
            self.fail(f"Failed to connect to Virtue URL {url}: {str(e)}")

if __name__ == '__main__':
    unittest.main()
