"""
Inverted index creation script for product data
Author: TP Indexation
Description: Builds and saves inverted indexes from a JSONL file
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from urllib.parse import urlparse, parse_qs


class IndexBuilder:
    """
    Class to build inverted indexes for product data.
    """
    
    # Stopwords
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'am', 'be', 'been', 'being',
        'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    }
    
    def __init__(self, input_file: str, output_dir: str = "indexes"):
        """
        Initialize the index builder.
        
        Args:
            input_file: Path to input JSONL file
            output_dir: Output directory for index JSON files
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize different indexes
        self.title_index = defaultdict(lambda: defaultdict(list))
        self.description_index = defaultdict(lambda: defaultdict(list))
        self.brand_index = defaultdict(set)
        self.origin_index = defaultdict(set)
        self.reviews_index = {}
        
    def extract_url_info(self, url: str) -> Tuple[str, str | None]:
        """
        Extract product ID and variant from URL.
        
        Args:
            url: Product URL
            
        Returns:
            Tuple (product_id, variant) where variant can be None
        """
        # Extract product_id: last number in path
        match = re.search(r'/product/(\d+)', url)
        product_id = match.group(1) if match else None
        
        # Extract variant from query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        variant = query_params.get('variant', [None])[0]
        
        return product_id, variant
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text by removing punctuation and stopwords.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        # Keep only alphanumeric characters and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split by spaces
        tokens = text.split()
        # Remove stopwords and empty strings
        tokens = [t for t in tokens if t and t not in self.STOPWORDS]
        
        return tokens
    
    def process_jsonl(self):
        """
        Read and process the JSONL file.
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        product = json.loads(line.strip())
                        self._process_product(product)
                    except json.JSONDecodeError as e:
                        print(f"JSON Error at line {line_num}: {e}")
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
        except FileNotFoundError:
            print(f"Error: File '{self.input_file}' not found")
            raise
    
    def _process_product(self, product: Dict[str, Any]):
        """
        Process an individual product.
        """
        url = product.get('url', '')
        if not url:
            return
        
        # Process title
        title = product.get('title', '')
        if title:
            self._index_text(title, url, self.title_index)
        
        # Process description
        description = product.get('description', '')
        if description:
            self._index_text(description, url, self.description_index)
        
        # Process features (brand and origin only)
        features = product.get('product_features', {})
        
        # Brand
        if 'brand' in features:
            brand = features['brand']
            if isinstance(brand, str) and brand:
                tokens = self.tokenize(brand)
                for token in tokens:
                    self.brand_index[token].add(url)
        
        # Origin
        if 'made in' in features:
            origin = features['made in']
            if isinstance(origin, str) and origin:
                tokens = self.tokenize(origin)
                for token in tokens:
                    self.origin_index[token].add(url)
        
        # Reviews
        reviews = product.get('product_reviews', [])
        if reviews:
            ratings = [review.get('rating', 0) for review in reviews]
            self.reviews_index[url] = {
                'total_reviews': len(reviews),
                'mean_mark': round(sum(ratings) / len(ratings), 2) if ratings else 0,
                'last_rating': ratings[-1] if ratings else 0
            }
        else:
            self.reviews_index[url] = {
                'total_reviews': 0,
                'mean_mark': 0,
                'last_rating': 0
            }
    
    def _index_text(self, text: str, url: str, index: Dict):
        """
        Add text to an inverted index with positions.
        
        Args:
            text: Text to index
            url: Document URL
            index: Inverted index to update
        """
        tokens = self.tokenize(text)
        for position, token in enumerate(tokens):
            if token:
                index[token][url].append(position)
    
    def save_indexes(self):
        """
        Save all indexes to JSON files.
        """
        try:
            title_index_dict = {
                token: {url: positions for url, positions in urls.items()}
                for token, urls in self.title_index.items()
            }
            
            description_index_dict = {
                token: {url: positions for url, positions in urls.items()}
                for token, urls in self.description_index.items()
            }
            
            brand_index_dict = {
                token: list(urls) for token, urls in self.brand_index.items()
            }
            
            origin_index_dict = {
                token: list(urls) for token, urls in self.origin_index.items()
            }
            
            # Save title index
            with open(self.output_dir / 'title_index.json', 'w', encoding='utf-8') as f:
                json.dump(title_index_dict, f, ensure_ascii=False, indent=2)
            print(f"✓ Title index saved")
            
            # Save description index
            with open(self.output_dir / 'description_index.json', 'w', encoding='utf-8') as f:
                json.dump(description_index_dict, f, ensure_ascii=False, indent=2)
            print(f"✓ Description index saved")
            
            # Save brand index
            with open(self.output_dir / 'brand_index.json', 'w', encoding='utf-8') as f:
                json.dump(brand_index_dict, f, ensure_ascii=False, indent=2)
            print(f"✓ Brand index saved")
            
            # Save origin index
            with open(self.output_dir / 'origin_index.json', 'w', encoding='utf-8') as f:
                json.dump(origin_index_dict, f, ensure_ascii=False, indent=2)
            print(f"✓ Origin index saved")
            
            # Save reviews index
            with open(self.output_dir / 'reviews_index.json', 'w', encoding='utf-8') as f:
                json.dump(self.reviews_index, f, ensure_ascii=False, indent=2)
            print(f"✓ Reviews index saved")
            
        except Exception as e:
            print(f"Error saving indexes: {e}")
            raise
    
    @staticmethod
    def load_index(filename: str) -> Dict:
        """
        Load an index from a JSON file.
        
        Args:
            filename: Path to file to load
            
        Returns:
            Dictionary containing the index
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            raise
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{filename}'")
            raise
    
    def search_title(self, query: str, index_dict: Dict) -> List[str]:
        """
        Search in title index.
        
        Args:
            query: Search term
            index_dict: Dictionary of title index
            
        Returns:
            List of URLs containing the term
        """
        tokens = self.tokenize(query)
        if not tokens:
            return []
        
        results = None
        for token in tokens:
            if token in index_dict:
                urls = set(index_dict[token].keys())
                results = urls if results is None else results & urls
            else:
                return []  # No results if a token finds nothing
        
        return list(results) if results else []
    


def main():
    """Main function."""
    print("Starting index building...")
    print("-" * 50)
    
    builder = IndexBuilder('products.jsonl', 'indexes')
    
    # Process JSONL file
    print("Reading and processing JSONL file...")
    builder.process_jsonl()
    
    # Save indexes
    print("\nSaving indexes...")
    builder.save_indexes()
    
    print("\n✓ Indexation completed successfully!")


if __name__ == '__main__':
    main()
