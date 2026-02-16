import requests
import sys

BASE_URL = "http://localhost:5000"

def test_shop_security():
    print("🛡️ Sentinel: Testing Shop Security...")

    # 1. Test Invalid Item ID
    print("\n🧪 Testing Invalid Item ID...")
    resp = requests.post(f"{BASE_URL}/api/shop/buy", json={"item_id": "invalid_item", "cost": 0})
    if resp.status_code == 400 and "Invalid item ID" in resp.text:
        print("✅ Correctly rejected invalid item ID.")
    else:
        print(f"❌ Failed to reject invalid item ID. Status: {resp.status_code}, Resp: {resp.text}")

    # 2. Test Already Owned Item
    print("\n🧪 Testing Already Owned Item (leviathan_axe)...")
    # Assuming leviathan_axe is already owned from previous tests
    resp = requests.post(f"{BASE_URL}/api/shop/buy", json={"item_id": "leviathan_axe", "cost": 0})
    if resp.status_code == 400 and "Item already owned" in resp.text:
        print("✅ Correctly rejected duplicate purchase.")
    else:
        print(f"❌ Failed to reject duplicate purchase. Status: {resp.status_code}, Resp: {resp.text}")

    # 3. Test Price Tampering (attempt to buy unowned item for 0)
    # I need an item I don't own. 'spartan_rage' (300)
    print("\n🧪 Testing Price Tampering (spartan_rage)...")

    # Check if owned first
    inv_resp = requests.get(f"{BASE_URL}/api/shop/inventory")
    owned = [i['item_id'] for i in inv_resp.json()['owned_items']]

    item_id = "spartan_rage"
    if item_id in owned:
        print(f"⚠️ {item_id} is already owned, skipping tampering test.")
    else:
        initial_balance = inv_resp.json()['hacksilver']
        real_cost = 300

        # Check if we can afford it
        if initial_balance < real_cost:
             print(f"⚠️ Not enough funds ({initial_balance}) to buy {item_id} ({real_cost}). Cannot test purchase success.")
             # But we can test that it doesn't buy for 0
             resp = requests.post(f"{BASE_URL}/api/shop/buy", json={"item_id": item_id, "cost": 0})
             # It should fail with "Not enough Hacksilver" (because server uses 500) OR succeed if we have funds.
             # Wait, if we DON'T have funds, it should fail with "Not enough Hacksilver" because it checks real_cost.
             if resp.status_code == 400 and "Not enough Hacksilver" in resp.text:
                 print("✅ Correctly rejected purchase due to insufficient funds (using real cost).")
             elif resp.status_code == 200:
                 print("❌ Purchase succeeded despite insufficient funds! (Did it use 0 cost?)")
             else:
                 print(f"❓ Unexpected response: {resp.status_code} {resp.text}")
        else:
             # We can afford it. Try to buy for 0.
             resp = requests.post(f"{BASE_URL}/api/shop/buy", json={"item_id": item_id, "cost": 0})
             if resp.status_code == 200:
                 new_balance = resp.json()['new_balance']
                 if new_balance == initial_balance - real_cost:
                     print("✅ Purchase successful but charged REAL cost (Attack Mitigated).")
                 elif new_balance == initial_balance:
                     print("🚨 VULNERABILITY: Purchase successful for 0 cost!")
                 else:
                     print(f"❓ Unexpected balance change. Old: {initial_balance}, New: {new_balance}")
             else:
                 print(f"❌ Purchase failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_shop_security()
