// /frontend/src/components/Armory/Armory.tsx
import React, { useState, useEffect } from 'react';
import './Armory.css';

// --- CATALOG OF ITEMS ---
const SHOP_CATALOG = [
    {
        id: 'leviathan_axe',
        name: 'Leviathan Axe',
        description: 'Imbued with frost. Grants +10% XP bonus on History & Culture tasks.',
        cost: 200,
        icon: '🪓'
    },
    {
        id: 'chaos_blades',
        name: 'Blades of Chaos',
        description: 'Forged in fire. Grants +10% XP bonus on Polity & IR tasks.',
        cost: 350,
        icon: '⚔️'
    },
    {
        id: 'guardian_shield',
        name: 'Guardian Shield',
        description: 'Protects your streak. Allows you to miss 1 day without penalty.',
        cost: 150,
        icon: '🛡️'
    },
    {
        id: 'mimir_head',
        name: 'Mimir Upgrade',
        description: 'Unlocks deeper wisdom. Mimir gives more detailed answers.',
        cost: 500,
        icon: '🗣️'
    },
    {
        id: 'spartan_rage',
        name: 'Greater Rage',
        description: 'Increases Focus Timer duration options.',
        cost: 300,
        icon: '🔥'
    }
];

interface InventoryItem {
    item_id: string;
    equipped: boolean;
}

const Armory: React.FC = () => {
    const [hacksilver, setHacksilver] = useState(0);
    const [ownedItems, setOwnedItems] = useState<Set<string>>(new Set());
    const [loading, setLoading] = useState(true);

    const fetchInventory = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/shop/inventory');
            if (res.ok) {
                const data = await res.json();
                setHacksilver(data.hacksilver);
                
                // Convert list to Set for easy lookup
                const ownedSet = new Set<string>(data.owned_items.map((i: InventoryItem) => i.item_id));
                setOwnedItems(ownedSet);
            }
        } catch (err) {
            console.error("Shop closed", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInventory();
    }, []);

    const handleBuy = async (item: typeof SHOP_CATALOG[0]) => {
        if (hacksilver < item.cost) return;
        if (!confirm(`Purchase ${item.name} for ${item.cost} Hacksilver?`)) return;

        try {
            const res = await fetch('http://localhost:5000/api/shop/buy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    item_id: item.id,
                    item_name: item.name,
                    cost: item.cost
                })
            });

            if (res.ok) {
                const data = await res.json();
                setHacksilver(data.new_balance);
                setOwnedItems(prev => new Set(prev).add(item.id));
                alert("Item forged successfully!");
            } else {
                alert("Transaction failed.");
            }
        } catch (err) {
            console.error("Buy failed", err);
        }
    };

    return (
        <div className="armory-container">
            <div className="armory-header">
                <h1 className="armory-title">Brok & Sindri's Shop</h1>
                <div className="wallet-display">
                    <div className="hacksilver-icon"></div>
                    <span className="wallet-amount">{hacksilver} HS</span>
                </div>
            </div>

            {loading ? (
                <div>Stoking the forge...</div>
            ) : (
                <div className="shop-grid">
                    {SHOP_CATALOG.map(item => {
                        const isOwned = ownedItems.has(item.id);
                        const canAfford = hacksilver >= item.cost;

                        return (
                            <div key={item.id} className="shop-item">
                                <div className="item-icon">{item.icon}</div>
                                <h2 className="item-name">{item.name}</h2>
                                <p className="item-desc">{item.description}</p>
                                
                                {isOwned ? (
                                    <div className="owned-badge">OWNED</div>
                                ) : (
                                    <button 
                                        className="buy-btn" 
                                        onClick={() => handleBuy(item)}
                                        disabled={!canAfford}
                                    >
                                        {canAfford ? `Craft (${item.cost})` : `Need ${item.cost}`}
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Armory;