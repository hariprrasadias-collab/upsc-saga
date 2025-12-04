// Enhanced Armory with Badges, Shop, and Inventory tabs
import React, { useState, useEffect } from 'react';
import './Armory.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

// Shop catalog remains the same
const SHOP_CATALOG = [
    { id: 'leviathan_axe', name: 'Leviathan Axe', description: 'Imbued with frost. Grants +10% XP bonus on History & Culture tasks.', cost: 200, icon: '🪓' },
    { id: 'chaos_blades', name: 'Blades of Chaos', description: 'Forged in fire. Grants +10% XP bonus on Polity & IR tasks.', cost: 350, icon: '⚔️' },
    { id: 'guardian_shield', name: 'Guardian Shield', description: 'Protects your streak. Allows you to miss 1 day without penalty.', cost: 150, icon: '🛡️' },
    { id: 'mimir_head', name: 'Mimir Upgrade', description: 'Unlocks deeper wisdom. Mimir gives more detailed answers.', cost: 500, icon: '🗣️' },
    { id: 'spartan_rage', name: 'Greater Rage', description: 'Increases Focus Timer duration options.', cost: 300, icon: '🔥' }
];

interface Badge {
    id: number;
    name: string;
    description: string;
    category: string;
    rarity: string;
    icon_url: string;
    xp_reward: number;
    unlocked: boolean;
    unlocked_at?: string;
    progress?: number;
    current_value?: number;
    target_value?: number;
}

const Armory: React.FC = () => {
    const [activeTab, setActiveTab] = useState('badges');
    const [hacksilver, setHacksilver] = useState(0);
    const [ownedItems, setOwnedItems] = useState<Set<string>>(new Set());
    const [badges, setBadges] = useState<Badge[]>([]);
    const [loading, setLoading] = useState(true);
    const [recommendation, setRecommendation] = useState<string | null>(null);
    const [isConsulting, setIsConsulting] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            // Fetch shop inventory
            const shopRes = await fetch('http://localhost:5000/api/shop/inventory');
            if (shopRes.ok) {
                const shopData = await shopRes.json();
                setHacksilver(shopData.hacksilver);
                const ownedSet = new Set<string>(shopData.owned_items.map((i: any) => i.item_id));
                setOwnedItems(ownedSet);
            }

            // Fetch badges
            const badgesRes = await fetch('http://localhost:5000/api/badges/all');
            if (badgesRes.ok) {
                const badgesData = await badgesRes.json();
                setBadges(badgesData);
            }
        } catch (err) {
            console.error("Error fetching armory data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleBuy = async (item: typeof SHOP_CATALOG[0]) => {
        if (hacksilver < item.cost) return;
        if (!confirm(`Purchase ${item.name} for ${item.cost} Hacksilver?`)) return;

        try {
            const res = await fetch('http://localhost:5000/api/shop/buy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: item.id, item_name: item.name, cost: item.cost })
            });

            if (res.ok) {
                const data = await res.json();
                setHacksilver(data.new_balance);
                setOwnedItems(prev => new Set(prev).add(item.id));
                alert("Item forged successfully!");
            }
        } catch (err) {
            console.error("Buy failed", err);
        }
    };

    const handleAskBrok = async () => {
        setIsConsulting(true);
        try {
            const payload = {
                hacksilver: hacksilver,
                weak_areas: ['History', 'Polity'] // In a real app, fetch this from analytics
            };
            const result = await brainService.executeAction('RECOMMEND_ARMORY_ITEM', payload);
            if (result.success) {
                setRecommendation(result.recommendation);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsConsulting(false);
        }
    };

    const getRarityClass = (rarity: string) => {
        return `rarity-${rarity.toLowerCase()}`;
    };

    const getCategoryIcon = (category: string) => {
        const icons: Record<string, string> = {
            milestone: '🎯',
            mastery: '🏆',
            practice: '✍️',
            social: '🤝',
            special: '✨'
        };
        return icons[category] || '🎖️';
    };

    return (
        <div className="armory-container">
            <div className="armory-header">
                <h1 className="armory-title">Brok & Sindri's Armory</h1>
                <div className="wallet-display">
                    <div className="hacksilver-icon"></div>
                    <span className="wallet-amount">{hacksilver} HS</span>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="armory-tabs">
                <button
                    className={`tab-btn ${activeTab === 'badges' ? 'active' : ''}`}
                    onClick={() => setActiveTab('badges')}
                >
                    🎖️ Badges
                </button>
                <button
                    className={`tab-btn ${activeTab === 'shop' ? 'active' : ''}`}
                    onClick={() => setActiveTab('shop')}
                >
                    🛍️ Shop
                </button>
                <button
                    className={`tab-btn ${activeTab === 'inventory' ? 'active' : ''}`}
                    onClick={() => setActiveTab('inventory')}
                >
                    📦 Inventory
                </button>
            </div>

            {loading ? (
                <div className="loading neon-text-orange">Stoking the forge...</div>
            ) : (
                <>
                    {/* Badges Tab */}
                    {activeTab === 'badges' && (
                        <div className="badges-container">
                            <div className="badge-stats glass-panel">
                                <span>Unlocked: {badges.filter(b => b.unlocked).length} / {badges.length}</span>
                                <span>Total XP Earned: {badges.filter(b => b.unlocked).reduce((sum, b) => sum + b.xp_reward, 0)}</span>
                            </div>

                            {['milestone', 'mastery', 'practice', 'special'].map(category => {
                                const categoryBadges = badges.filter(b => b.category === category);
                                if (categoryBadges.length === 0) return null;

                                return (
                                    <div key={category} className="badge-category">
                                        <h2 className="category-title neon-text-blue">
                                            {getCategoryIcon(category)} {category.charAt(0).toUpperCase() + category.slice(1)} Badges
                                        </h2>
                                        <div className="badge-grid">
                                            {categoryBadges.map(badge => (
                                                <div
                                                    key={badge.id}
                                                    className={`badge-card glass-panel ${badge.unlocked ? 'unlocked' : 'locked'} ${getRarityClass(badge.rarity)}`}
                                                >
                                                    <div className="badge-icon">{badge.icon_url}</div>
                                                    <div className="badge-info">
                                                        <h3 className="badge-name">{badge.name}</h3>
                                                        <p className="badge-desc">{badge.description}</p>
                                                        <div className="badge-footer">
                                                            <span className="badge-rarity">{badge.rarity}</span>
                                                            <span className="badge-reward">+{badge.xp_reward} XP</span>
                                                        </div>
                                                        {!badge.unlocked && badge.progress !== undefined && (
                                                            <div className="badge-progress">
                                                                <div className="progress-bar">
                                                                    <div
                                                                        className="progress-fill"
                                                                        style={{ width: `${badge.progress}%` }}
                                                                    ></div>
                                                                </div>
                                                                <span className="progress-text">{badge.progress}%</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Shop Tab */}
                    {activeTab === 'shop' && (
                        <>
                            <div className="brok-consult" style={{ marginBottom: '20px', textAlign: 'center' }}>
                                <button
                                    onClick={handleAskBrok}
                                    disabled={isConsulting}
                                    style={{
                                        background: '#e67e22',
                                        border: '2px solid #d35400',
                                        color: 'white',
                                        padding: '10px 20px',
                                        borderRadius: '5px',
                                        cursor: 'pointer',
                                        fontWeight: 'bold'
                                    }}
                                >
                                    {isConsulting ? 'Brok is thinking...' : '🔨 Ask Brok what to buy'}
                                </button>
                                {recommendation && (
                                    <div style={{
                                        marginTop: '10px',
                                        background: 'rgba(0,0,0,0.5)',
                                        padding: '10px',
                                        borderRadius: '5px',
                                        borderLeft: '4px solid #e67e22',
                                        color: '#ddd',
                                        fontStyle: 'italic'
                                    }}>
                                        <MarkdownRenderer content={`"${recommendation}"`} />
                                    </div>
                                )}
                            </div>
                            <div className="shop-grid">
                                {SHOP_CATALOG.map(item => {
                                    const isOwned = ownedItems.has(item.id);
                                    const canAfford = hacksilver >= item.cost;

                                    return (
                                        <div key={item.id} className="shop-item glass-panel">
                                            <div className="item-icon">{item.icon}</div>
                                            <h2 className="item-name neon-text-orange">{item.name}</h2>
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
                        </>
                    )}

                    {/* Inventory Tab */}
                    {activeTab === 'inventory' && (
                        <div className="inventory-container">
                            <h2 className="neon-text-blue">Your Inventory</h2>
                            {Array.from(ownedItems).length === 0 ? (
                                <p className="empty-inventory">Your inventory is empty. Visit the Shop to acquire items!</p>
                            ) : (
                                <div className="inventory-grid">
                                    {Array.from(ownedItems).map(itemId => {
                                        const item = SHOP_CATALOG.find(i => i.id === itemId);
                                        if (!item) return null;

                                        return (
                                            <div key={itemId} className="inventory-item glass-panel">
                                                <div className="item-icon">{item.icon}</div>
                                                <h3>{item.name}</h3>
                                                <p>{item.description}</p>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Armory;