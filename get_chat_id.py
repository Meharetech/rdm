# get_chat_id.py - Helper script to get your Telegram Chat ID
import requests

TELEGRAM_TOKEN = "8007630165:AAEBUZH0rjU3XPzx8JrUQ0DTeCKRKUmPXRw"

print("Getting your Telegram Chat ID...")
print("Please send a message to your bot first, then press Enter to continue.")
input()

try:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()
    
    if data.get("ok"):
        updates = data.get("result", [])
        if updates:
            # Get the latest message
            latest_update = updates[-1]
            chat = latest_update.get("message", {}).get("chat", {})
            chat_id = chat.get("id")
            chat_type = chat.get("type")
            chat_title = chat.get("title") or chat.get("first_name", "Unknown")
            
            print("\n" + "="*50)
            print(f"✅ Found Chat ID: {chat_id}")
            print(f"   Chat Type: {chat_type}")
            print(f"   Chat Name: {chat_title}")
            print("="*50)
            print(f"\nCopy this Chat ID and update TELEGRAM_CHAT_ID in your scripts:")
            print(f"TELEGRAM_CHAT_ID = \"{chat_id}\"")
        else:
            print("❌ No messages found. Please send a message to your bot first.")
    else:
        print(f"❌ Error: {data.get('description', 'Unknown error')}")
except Exception as e:
    print(f"❌ Error getting chat ID: {e}")

