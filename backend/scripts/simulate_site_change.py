"""
NeuroScrape - Site Change Simulation & Live Self-Healing Test Tool (Section 5.2.4)
Mutates class names, IDs, and structure of HTML snapshots programmatically
to test and demonstrate instant Two-Layer Self-Healing on stage.
"""

import sys
import os
import argparse
from bs4 import BeautifulSoup

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Demo Store</title></head>
<body>
  <div class="product-card">
    <h2 class="product-title">MacBook Pro 16" M3 Max</h2>
    <div class="price-box">
      <span class="price">$2,499.00</span>
    </div>
    <span class="stock-status">In Stock</span>
    <p class="description">Pro laptop with Apple Silicon.</p>
  </div>
</body>
</html>
"""


def mutate_html(html: str) -> str:
    """Mutates CSS class names and tags to simulate a breaking website update."""
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.find_all(class_=True):
        new_classes = []
        for c in el["class"]:
            if "price" in c:
                new_classes.append("cost-amount-v2")
            elif "title" in c:
                new_classes.append("product-heading-v2")
            elif "stock" in c:
                new_classes.append("inventory-badge-v2")
            else:
                new_classes.append(c + "-updated")
        el["class"] = new_classes
    return str(soup)


def main():
    parser = argparse.ArgumentParser(description="NeuroScrape Site Change Simulator")
    parser.add_argument("--file", type=str, help="HTML file path to mutate", default=None)
    parser.add_argument("--output", type=str, help="Output file path", default=None)
    args = parser.parse_args()

    html_content = SAMPLE_HTML
    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            html_content = f.read()

    mutated = mutate_html(html_content)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(mutated)
        print(f"Mutated HTML saved to {args.output}")
    else:
        print("=== MUTATED HTML ===")
        print(mutated)


if __name__ == "__main__":
    main()
