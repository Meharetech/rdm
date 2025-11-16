# add_product.py - Add products to items.json by extracting name from Croma URL
import json
import re
import sys
from urllib.parse import urlparse, unquote

ITEMS_FILE = "items.json"

def extract_product_name_from_url(url):
    """Extract product name from Croma URL"""
    try:
        # Parse URL
        parsed = urlparse(url)
        path = parsed.path
        
        # Extract product slug from path (e.g., /apple-iphone-17-256gb-lavender-/p/317401)
        # Pattern: /product-name-/p/product-id
        match = re.search(r'/([^/]+)-/p/', path)
        if match:
            product_slug = match.group(1)
            
            # Convert slug to readable name
            # Replace hyphens with spaces and capitalize words
            name = product_slug.replace('-', ' ')
            
            # Split into words and capitalize each
            words = name.split()
            capitalized_words = []
            for word in words:
                # Capitalize first letter
                if word:
                    capitalized_words.append(word.capitalize())
            
            # Join back with spaces
            product_name = ' '.join(capitalized_words)
            
            return product_name
        
        return None
    except Exception as e:
        print(f"Error extracting name from URL: {e}")
        return None


def load_items():
    """Load existing items from items.json"""
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: {ITEMS_FILE} is corrupted. Please fix it manually.")
        return None


def save_items(items):
    """Save items to items.json"""
    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving items: {e}")
        return False


def check_duplicate(url):
    """Check if URL already exists in items.json"""
    items = load_items()
    if items is None:
        return None, None
    
    for item in items:
        if item.get("url") == url:
            return True, item.get("name")
    
    return False, None


def add_product(url, custom_name=None, ask_new_link=False):
    """Add a new product to items.json"""
    # Validate URL
    if not url.startswith("http"):
        print("❌ Invalid URL. Please provide a full URL starting with http:// or https://")
        if ask_new_link:
            return ask_for_new_link()
        return False
    
    if "croma.com" not in url:
        print("⚠️  Warning: URL doesn't seem to be from Croma.com")
    
    # Check if URL already exists FIRST (before processing)
    is_duplicate, existing_name = check_duplicate(url)
    
    if is_duplicate:
        print("\n" + "=" * 60)
        print("❌ PRODUCT ALREADY ADDED!")
        print("=" * 60)
        print(f"📦 Product Name: {existing_name}")
        print(f"🔗 URL: {url}")
        print("\n⚠️  This product is already in your monitoring list.")
        
        if ask_new_link:
            print("\nPlease provide a new/different link:")
            return ask_for_new_link()
        else:
            # Command line mode - just exit
            print("\n💡 Tip: Use a different product URL or remove the existing one from items.json")
            return False
    
    # Load items (we know it's not a duplicate now)
    items = load_items()
    if items is None:
        return False
    
    # Extract product name
    if custom_name:
        product_name = custom_name
    else:
        product_name = extract_product_name_from_url(url)
        if not product_name:
            product_name = input("Could not auto-detect product name. Enter name manually: ").strip()
            if not product_name:
                print("❌ Product name is required. Cancelled.")
                return False
    
    # Create new product entry
    new_product = {
        "name": product_name,
        "url": url,
        "check_type": "text",
        "available_indicators": ["Buy Now", "Add to Cart", "Add to Bag"],
        "unavailable_indicators": [
            "Notify Me", 
            "Out of Stock", 
            "Currently unavailable", 
            "Not Available", 
            "Not Available for your pincode", 
            "Not Available at pincode"
        ]
    }
    
    # Add to items list
    items.append(new_product)
    
    # Save to file
    if save_items(items):
        print(f"✅ Product added successfully!")
        print(f"   Name: {product_name}")
        print(f"   URL: {url}")
        print(f"\n📝 {len(items)} product(s) in {ITEMS_FILE}")
        return True
    else:
        print("❌ Failed to save product.")
        return False


def ask_for_new_link():
    """Ask user for a new link in interactive mode"""
    print("\n" + "-" * 60)
    new_url = input("Enter new Croma product URL (or 'q' to quit): ").strip()
    
    if new_url.lower() == 'q':
        print("❌ Cancelled.")
        return False
    
    if not new_url:
        print("❌ URL cannot be empty. Please try again.")
        return ask_for_new_link()
    
    # Try to auto-detect name
    auto_name = extract_product_name_from_url(new_url)
    if auto_name:
        print(f"\n📦 Auto-detected product name: {auto_name}")
        use_auto = input("Use this name? (y/n): ").lower().strip()
        if use_auto == 'y':
            return add_product(new_url, auto_name, ask_new_link=True)
        else:
            custom_name = input("Enter custom name: ").strip()
            return add_product(new_url, custom_name if custom_name else None, ask_new_link=True)
    else:
        return add_product(new_url, None, ask_new_link=True)


if __name__ == "__main__":
    print("=" * 60)
    print("Croma Product Adder")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        # URL provided as command line argument
        url = sys.argv[1]
        custom_name = sys.argv[2] if len(sys.argv) > 2 else None
        add_product(url, custom_name, ask_new_link=False)
    else:
        # Interactive mode
        print("Enter Croma product URL:")
        url = input("URL: ").strip()
        
        if not url:
            print("❌ URL is required.")
            sys.exit(1)
        
        # Try to auto-detect name
        auto_name = extract_product_name_from_url(url)
        if auto_name:
            print(f"\n📦 Auto-detected product name: {auto_name}")
            use_auto = input("Use this name? (y/n): ").lower().strip()
            if use_auto == 'y':
                add_product(url, auto_name, ask_new_link=True)
            else:
                custom_name = input("Enter custom name: ").strip()
                add_product(url, custom_name if custom_name else None, ask_new_link=True)
        else:
            add_product(url, None, ask_new_link=True)

