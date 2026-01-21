# Product Indexation System

## Indexes

| Index | Type | Purpose |
|-------|------|---------|
| `title_index.json` | Inverted | Full-text search on product titles |
| `description_index.json` | Inverted | Full-text search on descriptions |
| `brand_index.json` | Simple | Filter products by brand |
| `origin_index.json` | Simple | Filter products by origin |
| `reviews_index.json` | Structured | Review statistics (count, average rating) |

**Inverted indexes** map tokens to URLs with character positions. **Simple indexes** map values to URL lists. Both apply tokenization, punctuation removal, and stopword filtering.

## Key Features

- **Tokenization**: Lowercase conversion, punctuation removal, stopword filtering
- **Positions**: Inverted indexes store token positions for phrase search capability
- **Variant handling**: Product URLs with parameters are treated as separate documents
- **No external dependencies**: Uses only Python standard library

## Setup & Run

**Command**:
```bash
python index_builder.py
```

This reads `products.jsonl` and generates index files in the `indexes/` folder.

## Usage Examples

```python
import json
from index_builder import IndexBuilder

# Load indexes
with open('indexes/title_index.json') as f:
    title_index = json.load(f)

# Search titles
print(title_index.get('chocolate', {}))

# Load reviews
with open('indexes/reviews_index.json') as f:
    reviews = json.load(f)

# Top-rated products
sorted_reviews = sorted(reviews.items(), 
                       key=lambda x: x[1]['mean_mark'], reverse=True)
```

## Main Methods

| Method | Purpose |
|--------|---------|
| `process_jsonl()` | Read and process JSONL file |
| `tokenize()` | Tokenize and clean text |
| `save_indexes()` | Save all indexes to JSON files |
| `load_index()` | Load index from file |

