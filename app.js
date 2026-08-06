// Telegram WebApp SDK
const tg = window.Telegram?.WebApp;

// Initialize Telegram Mini App
if (tg) {
    tg.ready();
    tg.expand();
    tg.setHeaderColor('#161b22');
    tg.setBackgroundColor('#0d1117');
}

// State
let currentSymbol = 'ALL';
let signals = [];
let refreshInterval = null;

// Sample data - will be replaced with API calls
const sampleSignals = [
    {
        id: 1,
        symbol: 'XAUUSD',
        timeframe: 'M1',
        type: 'SELL',
        confirmation: 'SELL',
        sellZone: {
            rec1: { from: 4033.204, to: 4034.837 },
            rec2: { from: 4035.250, to: 4036.325 },
            rec3: { from: 4034.339, to: 4035.616 }
        },
        buyZone: {
            rec1: { from: 4026.578, to: 4027.146 },
            rec2: { from: 4019.013, to: 4025.784 },
            rec3: { from: 4020.839, to: 4021.757 }
        },
        active: true,
        timestamp: Date.now()
    },
    {
        id: 2,
        symbol: 'EURUSD',
        timeframe: 'M5',
        type: 'BUY',
        confirmation: 'BUY',
        sellZone: {
            rec1: { from: 1.0890, to: 1.0910 },
            rec2: { from: 1.0920, to: 1.0945 },
            rec3: { from: 1.0905, to: 1.0925 }
        },
        buyZone: {
            rec1: { from: 1.0820, to: 1.0835 },
            rec2: { from: 1.0790, to: 1.0815 },
            rec3: { from: 1.0805, to: 1.0820 }
        },
        active: true,
        timestamp: Date.now() - 60000
    },
    {
        id: 3,
        symbol: 'GBPUSD',
        timeframe: 'M15',
        type: 'SELL',
        confirmation: 'WAIT',
        sellZone: {
            rec1: { from: 1.2720, to: 1.2745 },
            rec2: { from: 1.2760, to: 1.2785 },
            rec3: { from: 1.2740, to: 1.2760 }
        },
        buyZone: {
            rec1: { from: 1.2650, to: 1.2670 },
            rec2: { from: 1.2620, to: 1.2645 },
            rec3: { from: 1.2635, to: 1.2655 }
        },
        active: false,
        timestamp: Date.now() - 120000
    }
];

// DOM Elements
const symbolSelect = document.getElementById('symbolSelect');
const resetBtn = document.getElementById('resetBtn');
const signalCards = document.getElementById('signalCards');
const navItems = document.querySelectorAll('.nav-item');

// Initialize
function init() {
    loadSignals();
    setupEventListeners();
    startAutoRefresh();
}

// Setup Event Listeners
function setupEventListeners() {
    symbolSelect.addEventListener('change', (e) => {
        currentSymbol = e.target.value;
        renderSignals();
    });

    resetBtn.addEventListener('click', () => {
        currentSymbol = 'ALL';
        symbolSelect.value = 'ALL';
        renderSignals();
        showToast('Filter direset');
    });

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            const tab = item.dataset.tab;
            handleTabChange(tab);
        });
    });
}

// Handle Tab Change
function handleTabChange(tab) {
    switch(tab) {
        case 'package':
            showToast('Halaman Package');
            break;
        case 'signals':
            renderSignals();
            break;
        case 'profile':
            showToast('Halaman Profile');
            break;
    }
}

// API Configuration
const API_URL = 'https://forex-signals-api.onrender.com';

// Load Signals
async function loadSignals() {
    showLoading();

    // Try to fetch from API if configured
    if (API_URL) {
        try {
            const response = await fetch(`${API_URL}/api/signals`);
            if (response.ok) {
                signals = await response.json();
                renderSignals();
                return;
            }
        } catch (error) {
            console.log('API not available, using sample data');
        }
    }

    // Fallback to sample data
    signals = sampleSignals;
    renderSignals();
}

// Render Signals
function renderSignals() {
    const filtered = currentSymbol === 'ALL'
        ? signals
        : signals.filter(s => s.symbol === currentSymbol);

    if (filtered.length === 0) {
        signalCards.innerHTML = `
            <div class="empty-state">
                <h3>Tidak Ada Sinyal</h3>
                <p>Saat ini tidak ada sinyal aktif untuk symbol ini.</p>
            </div>
        `;
        return;
    }

    signalCards.innerHTML = filtered.map(signal => createSignalCard(signal)).join('');

    // Add event listeners to buttons
    document.querySelectorAll('.btn-confirm-sell, .btn-confirm-buy').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const symbol = e.currentTarget.dataset.symbol;
            const type = e.currentTarget.dataset.type;
            confirmSignal(symbol, type);
        });
    });
}

// Create Signal Card HTML
function createSignalCard(signal) {
    const isSell = signal.type === 'SELL';
    const typeClass = isSell ? 'sell' : 'buy';
    const arrowSvg = isSell
        ? '<svg viewBox="0 0 24 24"><path d="M7 14l5-5 5 5H7z"/></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M7 10l5 5 5-5H7z"/></svg>';

    const timeAgo = getTimeAgo(signal.timestamp);

    return `
        <div class="signal-card">
            <div class="symbol-header">
                <span class="symbol-name">${signal.symbol}</span>
                <span class="timeframe-badge">${signal.timeframe}</span>
            </div>

            <div class="signal-type ${typeClass}">
                <div class="signal-icon ${typeClass}">
                    ${arrowSvg}
                </div>
                <div>
                    <div class="signal-label">${signal.type}</div>
                    <div class="signal-confirm">Konfirmasi: ${signal.confirmation}</div>
                </div>
            </div>

            <div class="zone-section">
                <div class="zone-title sell">SELL ZONE</div>
                <div class="zone-recommendations">
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 1</div>
                        <div class="rec-range">${formatPrice(signal.sellZone.rec1.from)} - ${formatPrice(signal.sellZone.rec1.to)}</div>
                    </div>
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 2</div>
                        <div class="rec-range">${formatPrice(signal.sellZone.rec2.from)} - ${formatPrice(signal.sellZone.rec2.to)}</div>
                    </div>
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 3</div>
                        <div class="rec-range">${formatPrice(signal.sellZone.rec3.from)} - ${formatPrice(signal.sellZone.rec3.to)}</div>
                    </div>
                </div>
            </div>

            <div class="zone-section">
                <div class="zone-title buy">BUY ZONE</div>
                <div class="zone-recommendations">
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 1</div>
                        <div class="rec-range">${formatPrice(signal.buyZone.rec1.from)} - ${formatPrice(signal.buyZone.rec1.to)}</div>
                    </div>
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 2</div>
                        <div class="rec-range">${formatPrice(signal.buyZone.rec2.from)} - ${formatPrice(signal.buyZone.rec2.to)}</div>
                    </div>
                    <div class="recommendation">
                        <div class="rec-label">RECOMMENDATION 3</div>
                        <div class="rec-range">${formatPrice(signal.buyZone.rec3.from)} - ${formatPrice(signal.buyZone.rec3.to)}</div>
                    </div>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-active">
                    <span class="btn-dot"></span>
                    ACTIVE
                </button>
                <button class="btn btn-confirm-${typeClass}" data-symbol="${signal.symbol}" data-type="${signal.type}">
                    <span class="btn-dot"></span>
                    KONFIRMASI ${signal.type}
                </button>
            </div>
        </div>
    `;
}

// Format Price
function formatPrice(price) {
    if (price >= 1000) {
        return price.toFixed(3);
    } else if (price >= 100) {
        return price.toFixed(3);
    } else {
        return price.toFixed(4);
    }
}

// Get Time Ago
function getTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);

    if (seconds < 60) return `${seconds} detik lalu`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)} menit lalu`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} jam lalu`;
    return `${Math.floor(seconds / 86400)} hari lalu`;
}

// Confirm Signal
function confirmSignal(symbol, type) {
    if (tg?.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred('success');
    }

    showToast(`Sinyal ${type} ${symbol} dikonfirmasi`);

    // Send to bot
    if (tg?.sendData) {
        tg.sendData(JSON.stringify({
            action: 'confirm',
            symbol: symbol,
            type: type,
            timestamp: Date.now()
        }));
    }
}

// Show Loading
function showLoading() {
    signalCards.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Memuat sinyal...</p>
        </div>
    `;
}

// Show Toast
function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// Start Auto Refresh
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadSignals();
    }, 60000); // Refresh every 60 seconds
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Start app
document.addEventListener('DOMContentLoaded', init);
