from app.db import get_db
from datetime import datetime, timedelta
import traceback

class ShopService:
    """
    Service for managing the virtual rewards shop.
    """
    
    def __init__(self):
        pass
    
    def get_all_items(self):
        """Get all shop items."""
        try:
            conn = get_db()
            items = conn.execute('SELECT * FROM shop_items ORDER BY category, price').fetchall()
            return [dict(row) for row in items]
        except Exception:
            return []
    
    def get_user_balance(self, user_id):
        """Get user's XP and Hacksilver balance."""
        try:
            conn = get_db()
            user = conn.execute('''
                SELECT current_xp, hacksilver
                FROM users WHERE id = ?
            ''', (user_id,)).fetchone()

            if not user:
                return {'xp': 0, 'hacksilver': 0}

            return {
                'xp': user['current_xp'],
                'hacksilver': user['hacksilver']
            }
        except Exception:
            return {'xp': 0, 'hacksilver': 0}
    
    def purchase_item(self, user_id, item_id):
        """
        Purchase an item from the shop.
        Returns success status and new balance.
        """
        conn = get_db()
        try:
            # Get item details
            item = conn.execute('''
                SELECT * FROM shop_items WHERE item_id = ?
            ''', (item_id,)).fetchone()

            if not item:
                return {'success': False, 'message': 'Item not found'}

            # Get user balance
            user = conn.execute('''
                SELECT current_xp, hacksilver FROM users WHERE id = ?
            ''', (user_id,)).fetchone()

            if not user:
                return {'success': False, 'message': 'User not found'}

            # Check if user can afford
            currency = item['currency']
            price = item['price']

            if currency == 'xp' and user['current_xp'] < price:
                return {'success': False, 'message': f'Not enough XP. Need {price}, have {user["current_xp"]}'}
            elif currency == 'hacksilver' and user['hacksilver'] < price:
                return {'success': False, 'message': f'Not enough Hacksilver. Need {price}, have {user["hacksilver"]}'}

            # Deduct currency
            if currency == 'xp':
                conn.execute('''
                    UPDATE users SET current_xp = current_xp - ? WHERE id = ?
                ''', (price, user_id))
                new_balance = user['current_xp'] - price
            else:  # hacksilver
                conn.execute('''
                    UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?
                ''', (price, user_id))
                new_balance = user['hacksilver'] - price

            # Add to inventory
            quantity = item['max_uses'] if item['max_uses'] else 1
            conn.execute('''
                INSERT INTO user_inventory (user_id, item_id, quantity)
                VALUES (?, ?, ?)
            ''', (user_id, item_id, quantity))

            # Record transaction
            conn.execute('''
                INSERT INTO transactions (user_id, item_id, amount, currency, transaction_type)
                VALUES (?, ?, ?, ?, 'purchase')
            ''', (user_id, item_id, price, currency))

            conn.commit()

            return {
                'success': True,
                'message': f'Purchased {item["name"]}!',
                'new_balance': new_balance,
                'currency': currency
            }
        except Exception as e:
            conn.rollback()
            print(f"Purchase Error: {e}")
            return {'success': False, 'message': 'Transaction failed'}
    
    def get_user_inventory(self, user_id):
        """Get user's inventory with item details."""
        try:
            conn = get_db()
            inventory = conn.execute('''
                SELECT ui.*, si.name, si.description, si.icon, si.category, si.duration_hours
                FROM user_inventory ui
                JOIN shop_items si ON ui.item_id = si.item_id
                WHERE ui.user_id = ?
                ORDER BY ui.purchased_at DESC
            ''', (user_id,)).fetchall()

            return [dict(row) for row in inventory]
        except Exception:
            return []
    
    def activate_item(self, user_id, inventory_id):
        """
        Activate/use an item from inventory.
        """
        conn = get_db()
        try:
            # Get inventory item
            inv_item = conn.execute('''
                SELECT ui.*, si.duration_hours, si.max_uses
                FROM user_inventory ui
                JOIN shop_items si ON ui.item_id = si.item_id
                WHERE ui.id = ? AND ui.user_id = ?
            ''', (inventory_id, user_id)).fetchone()

            if not inv_item:
                return {'success': False, 'message': 'Item not found in inventory'}

            # Check if already activated and not expired
            if inv_item['activated_at']:
                if inv_item['expires_at']:
                    expires = datetime.fromisoformat(inv_item['expires_at'])
                    if datetime.now() < expires:
                        return {'success': False, 'message': 'Item already active'}

            # Activate the item
            now = datetime.now()
            expires_at = None

            if inv_item['duration_hours']:
                expires_at = now + timedelta(hours=inv_item['duration_hours'])

            conn.execute('''
                UPDATE user_inventory
                SET activated_at = ?, expires_at = ?
                WHERE id = ?
            ''', (now.isoformat(), expires_at.isoformat() if expires_at else None, inventory_id))

            # Decrease quantity for consumable items
            if inv_item['max_uses']:
                new_quantity = inv_item['quantity'] - 1
                if new_quantity <= 0:
                    conn.execute('DELETE FROM user_inventory WHERE id = ?', (inventory_id,))
                else:
                    conn.execute('''
                        UPDATE user_inventory SET quantity = ? WHERE id = ?
                    ''', (new_quantity, inventory_id))

            conn.commit()

            return {
                'success': True,
                'message': 'Item activated!',
                'expires_at': expires_at.isoformat() if expires_at else None
            }
        except Exception as e:
            conn.rollback()
            print(f"Activation Error: {e}")
            return {'success': False, 'message': 'Activation failed'}
    
    def get_active_powerups(self, user_id):
        """Get currently active power-ups for the user."""
        try:
            conn = get_db()
            now = datetime.now().isoformat()

            active = conn.execute('''
                SELECT ui.*, si.name, si.icon, si.category
                FROM user_inventory ui
                JOIN shop_items si ON ui.item_id = si.item_id
                WHERE ui.user_id = ?
                AND ui.activated_at IS NOT NULL
                AND (ui.expires_at IS NULL OR ui.expires_at > ?)
            ''', (user_id, now)).fetchall()

            return [dict(row) for row in active]
        except Exception:
            return []

shop_service = ShopService()
