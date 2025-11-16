# stock_alert_selenium.py
import json
import time
import schedule
import requests
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ====== CONFIG ======
ITEMS_FILE = "items.json"
CHECK_INTERVAL_MIN = 1
TELEGRAM_TOKEN = "8007630165:AAEBUZH0rjU3XPzx8JrUQ0DTeCKRKUmPXRw"
TELEGRAM_CHAT_ID = "8186826029"

# Initialize Telegram bot using requests (more reliable)
def send_telegram_message(text):
    """Send message via Telegram Bot API using requests"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

# Setup Chrome options (optimized for server/VPS hosting)
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")  # Required for servers/VPS
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevents /dev/shm issues on servers
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR messages
chrome_options.add_argument("--silent")
chrome_options.add_argument("--disable-setuid-sandbox")  # For server environments
chrome_options.add_argument("--remote-debugging-port=9222")  # For headless debugging
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("prefs", {
    "logging.browser.enabled": False,
    "logging.driver.enabled": False
})
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Suppress Chrome/ChromeDriver output
service = Service()
service.log_path = os.devnull  # Suppress service logs

# Initialize driver (use system ChromeDriver - no webdriver_manager needed)
driver = None
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Suppress console output from Chrome
    driver.set_window_size(1920, 1080)
    print("✅ ChromeDriver initialized successfully")
    print("ℹ️  Chrome warnings are normal and can be ignored\n")
except Exception as e:
    print(f"❌ Error initializing ChromeDriver: {e}")
    print("\nPlease ensure:")
    print("1. Google Chrome is installed")
    print("   On Linux: sudo apt-get install google-chrome-stable")
    print("2. ChromeDriver is in PATH or same folder as script")
    print("   Download from: https://chromedriver.chromium.org/downloads")
    print("\nFor Server/VPS (Hostinger):")
    print("- Run with: xvfb-run -a python3 stock_alert_selenium.py")
    print("- Or use: nohup xvfb-run -a python3 stock_alert_selenium.py &")
    print("\n💡 RECOMMENDATION: Use stock_alert_simple.py for shared hosting!")
    print("   It works without Chrome and has the same features.")

notified = {}  # Track if we've sent stock available notification
delivery_status = {}  # Track delivery availability status: True = available, False = not available, None = unknown


def load_items():
    """Load items from items.json file"""
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_once():
    """Check all items once for stock availability using Selenium"""
    if not driver:
        print("Error: ChromeDriver not initialized. Cannot check items.")
        return
    
    items = load_items()
    
    print(f"\n{'='*70}")
    print(f"📊 CHECKING {len(items)} PRODUCT(S) - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    for item in items:
        name = item.get("name") or item.get("url")
        url = item["url"]
        
        try:
            driver.get(url)
            time.sleep(3)  # wait for JS to render; increase if needed
            
            # STEP 1: FIRST CHECK DELIVERY AVAILABILITY (HIGHEST PRIORITY)
            delivery_unavailable = False
            delivery_text = ""
            
            try:
                # Check delivery section specifically for "Not Available"
                delivery_elements = driver.find_elements("css selector", ".delivery-not-available, .not-available-color, .cp-ship-opt, .delivery-option-margin")
                for elem in delivery_elements:
                    elem_text = elem.text.lower()
                    if elem_text:
                        delivery_text += " " + elem_text
                        # Check for delivery unavailable indicators
                        delivery_unavailable_phrases = ["not available", "not available for", "not available at", "delivery not available"]
                        for phrase in delivery_unavailable_phrases:
                            if phrase in elem_text:
                                delivery_unavailable = True
                                break
                        if delivery_unavailable:
                            break
            except Exception:
                pass  # Continue if delivery section not found
            
            # If delivery is not available, mark as unavailable immediately
            if delivery_unavailable:
                avail = False
                matched_indicator = "Delivery Not Available"
                
                # Check if delivery status changed (to notify only once)
                prev_delivery_status = delivery_status.get(url)
                
                if prev_delivery_status is not False:  # First time or changed from available
                    msg = f"🚚 DELIVERY NOT AVAILABLE\n\n📦 Product: {name}\n❌ Delivery Not Available for your pincode\n🔗 {url}\n\n⏳ Monitoring... Will notify when delivery becomes available!"
                    print(f"\n[{name}]")
                    print(f"  🚚 Delivery: ❌ NOT AVAILABLE (for your pincode)")
                    print(f"  📦 Stock: ❌ Cannot determine (delivery unavailable)")
                    print(f"  📢 Status: Notification sent via Telegram")
                    send_telegram_message(msg)
                else:
                    print(f"\n[{name}]")
                    print(f"  🚚 Delivery: ❌ NOT AVAILABLE (for your pincode)")
                    print(f"  📦 Stock: ❌ Cannot determine (delivery unavailable)")
                    print(f"  📢 Status: Monitoring...")
                
                delivery_status[url] = False  # Update delivery status
            else:
                # STEP 2: Get text content from page for other indicators
                if item.get("check_type") == "css":
                    try:
                        el = driver.find_element("css selector", item["css_selector"])
                        txt = el.text.lower()
                    except Exception:
                        txt = driver.page_source.lower()
                else:
                    txt = driver.page_source.lower()
                    # Include delivery text in the search
                    if delivery_text:
                        txt += " " + delivery_text
                
                avail = None
                matched_indicator = None
                
                # Check for available indicators (only if delivery is available)
                for ph in item.get("available_indicators", []):
                    if ph.lower() in txt:
                        avail = True
                        matched_indicator = ph
                        break
                
                # Check for unavailable indicators (only if available indicators not found)
                if avail is None:
                    for ph in item.get("unavailable_indicators", []):
                        if ph.lower() in txt:
                            avail = False
                            matched_indicator = ph
                            break
            
            # Update delivery status if delivery is available
            prev = notified.get(url, False)
            
            # Print detailed status for this product
            if not delivery_unavailable:
                prev_delivery_status = delivery_status.get(url)
                if prev_delivery_status is False:  # Delivery was unavailable, now available
                    msg = f"✅ DELIVERY NOW AVAILABLE!\n\n📦 Product: {name}\n🚚 Delivery is now available for your pincode\n🔗 {url}\n\n✨ You can now purchase this product!"
                    print(f"\n[{name}]")
                    print(f"  🚚 Delivery: ✅ NOW AVAILABLE!")
                    print(f"  📢 Status: Notification sent via Telegram")
                    send_telegram_message(msg)
                    delivery_status[url] = True
                else:
                    print(f"\n[{name}]")
                    print(f"  🚚 Delivery: ✅ Available")
                    delivery_status[url] = True
                
                if avail is True and not prev:
                    msg = f"✅ STOCK ALERT: {name}\n🎉 Product is in stock!\n{url}"
                    print(f"  📦 Stock: ✅ IN STOCK!")
                    print(f"  🔍 Matched: {matched_indicator or 'Available indicator found'}")
                    print(f"  📢 Status: 🚨 STOCK ALERT - Notification sent!")
                    send_telegram_message(msg)
                    notified[url] = True
                elif avail is True and prev:
                    print(f"  📦 Stock: ✅ IN STOCK")
                    print(f"  🔍 Matched: {matched_indicator or 'Available indicator found'}")
                    print(f"  📢 Status: Already notified (stock still available)")
                elif avail is False:
                    notified[url] = False
                    print(f"  📦 Stock: ❌ OUT OF STOCK")
                    print(f"  🔍 Matched: {matched_indicator or 'Unavailable indicator found'}")
                    print(f"  📢 Status: Monitoring...")
                else:
                    # Status unclear - show some context for debugging
                    page_text_sample = driver.find_element("tag name", "body").text[:500].replace("\n", " ")
                    print(f"  📦 Stock: ⚠️  STATUS UNCLEAR")
                    print(f"  🔍 Looking for: {item.get('available_indicators', []) + item.get('unavailable_indicators', [])}")
                    print(f"  📝 Page sample: {page_text_sample[:100]}...")
        
        except Exception as e:
            print(f"\n[{name}]")
            print(f"  ❌ Error: {e}")
            print(f"  📢 Status: Failed to check")
    
    print(f"\n{'='*70}")
    print(f"✅ CHECK COMPLETE - {time.strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    if not driver:
        print("Cannot start: ChromeDriver not available.")
        exit(1)
    
    print(f"\nStarting stock monitor...")
    print(f"Checking every {CHECK_INTERVAL_MIN} minutes...")
    print("Press Ctrl+C to stop.\n")
    
    check_once()  # first run immediately
    
    schedule.every(CHECK_INTERVAL_MIN).minutes.do(check_once)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        if driver:
            driver.quit()
        print("Done!")
