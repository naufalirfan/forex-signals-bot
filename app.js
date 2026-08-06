const tg = window.Telegram?.WebApp;

if (tg) {
    tg.ready();
    tg.expand();
    tg.setHeaderColor('#161b22');
    tg.setBackgroundColor('#0d1117');
}

let currentSymbol = 'ALL';
let currentTimeframe = 'ALL';
let signals = [];
let refreshInterval = null;

const TIMEFRAMES = ['ALL', 'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN'];

const API_URL = 'https://forex-signals-api.onrender.com';

const symbolSelect = document.getElementById('symbolSelect');
const timeframeSelect = document.getElementById('timeframeSelect');
const resetBtn = document.getElementById('resetBtn');
const signalCards = document.getElementById('signalCards');
const navItems = document.querySelectorAll('.nav-item');

function init() {
    loadSignals();
    setupEventListeners();
    startAutoRefresh();
}

function setupEventListeners() {
    symbolSelect.addEventListener('change', (e) => {
        currentSymbol = e.target.value;
        renderSignals();
    });

    timeframeSelect.addEventListener('change', (e) => {
        currentTimeframe = e.target.value;
        renderSignals();
    });

    resetBtn.addEventListener('click', () => {
        currentSymbol = 'ALL';
        currentTimeframe = 'ALL';
        symbolSelect.value = 'ALL';
        timeframeSelect.value = 'ALL';
        renderSignals();
        showToast('Filter direset');
    });

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            handleTabChange(item.dataset.tab);
        });
    });
}

function handleTabChange(tab) {
    if (tab === 'signals') renderSignals();
    else showToast('Halaman ' + tab.charAt(0).toUpperCase() + tab.slice(1));
}

async function loadSignals() {
    showLoading();

    try {
        const response = await fetch(`${API_URL}/api/signals`);
        if (response.ok) {
            signals = await response.json();
            renderSignals();
            return;
        }
    } catch (error) {
        console.log('API not available');
    }

    signalCards.innerHTML = '<div class="empty-state"><h3>API Offline</h3><p>Tidak dapat terhubung ke server.</p></div>';
}

function renderSignals() {
    let filtered = signals;

    if (currentSymbol !== 'ALL') {
        filtered = filtered.filter(s => s.symbol === currentSymbol);
    }
    if (currentTimeframe !== 'ALL') {
        filtered = filtered.filter(s => s.timeframe === currentTimeframe);
    }

    if (filtered.length === 0) {
        signalCards.innerHTML = '<div class="empty-state"><h3>Tidak Ada Sinyal</h3><p>Saat ini tidak ada sinyal untuk filter ini.</p></div>';
        return;
    }

    signalCards.innerHTML = filtered.map(signal => createSignalCard(signal)).join('');

    document.querySelectorAll('.btn-confirm-sell, .btn-confirm-buy').forEach(btn => {
        btn.addEventListener('click', (e) => {
            confirmSignal(e.currentTarget.dataset.symbol, e.currentTarget.dataset.type);
        });
    });
}

function createSignalCard(signal) {
    const isSell = signal.type === 'SELL';
    const typeClass = isSell ? 'sell' : 'buy';
    const arrowSvg = isSell
        ? '<svg viewBox="0 0 24 24"><path d="M7 14l5-5 5 5H7z"/></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M7 10l5 5 5-5H7z"/></svg>';

    const confirmClass = signal.confirmation === 'WAIT' ? 'wait' : typeClass;

    return `
        <div class="signal-card">
            <div class="symbol-header">
                <span class="symbol-name">${signal.symbol}</span>
                <span class="timeframe-badge">${signal.timeframe}</span>
            </div>

            <div class="signal-type ${typeClass}">
                <div class="signal-icon ${typeClass}">${arrowSvg}</div>
                <div>
                    <div class="signal-label">${signal.type}</div>
                    <div class="signal-confirm">Konfirmasi: ${signal.confirmation}</div>
                </div>
            </div>

            <div class="entry-sl-tp">
                <div class="stat-box">
                    <div class="stat-label">ENTRY</div>
                    <div class="stat-value">${formatPrice(signal.entry)}</div>
                </div>
                <div class="stat-box tp">
                    <div class="stat-label">TAKE PROFIT</div>
                    <div class="stat-value tp-value">${formatPrice(signal.takeProfit)}</div>
                </div>
                <div class="stat-box sl">
                    <div class="stat-label">STOP LOSS</div>
                    <div class="stat-value sl-value">${formatPrice(signal.stopLoss)}</div>
                </div>
                <div class="stat-box rr">
                    <div class="stat-label">R:R</div>
                    <div class="stat-value">${signal.riskReward}:1</div>
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
                <button class="btn btn-confirm-${confirmClass}" data-symbol="${signal.symbol}" data-type="${signal.type}">
                    <span class="btn-dot"></span>
                    KONFIRMASI ${signal.type}
                </button>
            </div>
        </div>
    `;
}

function formatPrice(price) {
    if (price === undefined || price === null) return '-';
    if (price >= 1000) return price.toFixed(3);
    if (price >= 100) return price.toFixed(3);
    if (price >= 1) return price.toFixed(5);
    return price.toFixed(5);
}

function confirmSignal(symbol, type) {
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
    showToast(`Sinyal ${type} ${symbol} dikonfirmasi`);
    if (tg?.sendData) {
        tg.sendData(JSON.stringify({ action: 'confirm', symbol, type, timestamp: Date.now() }));
    }
}

function showLoading() {
    signalCards.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Memuat sinyal...</p></div>';
}

function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function startAutoRefresh() {
    refreshInterval = setInterval(loadSignals, 60000);
}

window.addEventListener('beforeunload', () => {
    if (refreshInterval) clearInterval(refreshInterval);
});

document.addEventListener('DOMContentLoaded', init);
