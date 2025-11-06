// Base URL for our Flask API
// We must use the full URL
const API_URL = '';

let chartInstance = null;
let challengeState = {
    ticker: '',
    targetDate: '',
    actualPrice: 0,
    dataForPrediction: [] // The 7 days *before* the target
};

// =========================================
// 1. FETCH & PROCESS DATA
// =========================================
async function loadStockChallenge() {
    const ticker = document.getElementById('stockSelect').value;
    const period = document.getElementById('periodSelect').value;
    challengeState.ticker = ticker;
    
    // --- UI Reset ---
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('gameArea').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('resultsCard').classList.add('hidden');
    document.getElementById('resultsCard').classList.remove('opacity-100');
    document.getElementById('userGuess').value = '';
    
    const revealBtn = document.getElementById('revealBtn');
    revealBtn.disabled = false;
    revealBtn.innerText = "Reveal Results";

    // Reset model name text on new challenge
    const modelNameEl = document.getElementById('resModelName');
    if (modelNameEl) {
        modelNameEl.innerText = "(Model: ---)";
    }

    try {
        // --- Call our Flask API to get chart data ---
        const response = await fetch(`${API_URL}/get_stock_data?ticker=${ticker}&period=${period}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Failed to fetch data from server.");
        }
        
        const data = await response.json();
        
        // --- Core Game Logic ---
        // We need at least 8 days of data (7 for prediction + 1 for target)
        if (data.close_prices.length < 8) {
            throw new Error("Not enough data to run a challenge. Try a longer period.");
        }
        
        // The "target" is the most recent day
        challengeState.targetDate = data.dates[data.dates.length - 1];
        challengeState.actualPrice = data.close_prices[data.close_prices.length - 1];
        
        // The "visible data" is everything *before* the target
        const visibleDates = data.dates.slice(0, -1);
        const visiblePrices = data.close_prices.slice(0, -1);
        
        // The "data for prediction" is the 7 days *just before* the target day
        // The API expects 7 items
        challengeState.dataForPrediction = data.close_prices.slice(-8, -1);
         if (challengeState.dataForPrediction.length !== 7) {
            throw new Error("Data integrity error. Could not extract 7 days for prediction.");
         }
        
        // --- Render UI ---
        renderGameUI(visibleDates, visiblePrices);

    } catch (err) {
        showError(err.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

// =========================================
// 2. RENDER CHART & GAME UI
// =========================================
function renderGameUI(dates, prices) {
    document.getElementById('gameArea').classList.remove('hidden');
    
    // Update text elements
    document.getElementById('targetDateDisplay').innerText = challengeState.targetDate;
    document.querySelectorAll('.targetDateRef').forEach(el => {
        el.innerText = challengeState.targetDate;
    });

    // --- Draw Chart.js ---
    if (chartInstance) {
        chartInstance.destroy();
    }
    const ctx = document.getElementById('stockChart').getContext('2d');
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `${challengeState.ticker} Closing Price`,
                data: prices,
                borderColor: 'rgb(59, 130, 246)', // Tailwind blue-500
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                pointRadius: 2,
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: { color: '#9CA3AF' }, // gray-400
                    grid: { color: '#374151' }  // gray-700
                },
                x: {
                    ticks: { color: '#9CA3AF' },
                    grid: { color: '#374151' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#D1D5DB' } // gray-300
                }
            }
        }
    });
}

// =========================================
// 3. REVEAL & CALCULATE RESULTS
// =========================================
async function revealResults() {
    const userGuessStr = document.getElementById('userGuess').value;
    if (!userGuessStr) {
        showError("Please enter your prediction first!");
        return;
    }
    
    document.getElementById('error').classList.add('hidden');
    const revealBtn = document.getElementById('revealBtn');
    revealBtn.disabled = true;
    revealBtn.innerText = "Working...";

    try {
        // --- Call our Flask API to get the ML prediction ---
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ticker: challengeState.ticker,
                recent_data: challengeState.dataForPrediction
            })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Failed to get prediction from model.");
        }
        
        const result = await response.json();
        
        const userGuess = parseFloat(userGuessStr);
        const actual = challengeState.actualPrice;

        // --- ⭐ HERE ARE THE UPDATES ⭐ ---
        const modelPrediction = result.predicted_price;
        const modelName = result.model_name || 'Unknown'; // Get name, or fallback
        // --- ⭐ END OF UPDATES ⭐ ---


        // Calculate differences
        const userDiff = Math.abs(userGuess - actual);
        const modelDiff = Math.abs(modelPrediction - actual);

        // --- Populate Results Card ---
        document.getElementById('resActual').innerText = `$${actual.toFixed(2)}`;
        
        document.getElementById('resUser').innerText = `$${userGuess.toFixed(2)}`;
        const resUserDiff = document.getElementById('resUserDiff');
        resUserDiff.innerText = `Off by: $${userDiff.toFixed(2)}`;
        resUserDiff.className = userDiff <= modelDiff ? "text-sm mt-2 text-green-400 font-bold" : "text-sm mt-2 text-red-400";

        document.getElementById('resModel').innerText = `$${modelPrediction.toFixed(2)}`;
        
        // --- ⭐ HERE IS THE OTHER UPDATE ⭐ ---
        document.getElementById('resModelName').innerText = `(Model: ${modelName})`;
        // --- ⭐ END OF UPDATE ⭐ ---

        const resModelDiff = document.getElementById('resModelDiff');
        resModelDiff.innerText = `Off by: $${modelDiff.toFixed(2)}`;
        resModelDiff.className = modelDiff < userDiff ? "text-sm mt-2 text-green-400 font-bold" : "text-sm mt-2 text-red-400";

        // Determine Winner
        const banner = document.getElementById('winnerBanner');
        if (userDiff < modelDiff) {
            banner.innerText = "🎉 YOU BEAT THE MODEL! 🎉";
            banner.className = "text-center py-3 px-4 rounded-lg font-bold text-lg mt-6 bg-green-600 animate-bounce";
        } else if (modelDiff < userDiff) {
            banner.innerText = "🤖 THE ML MODEL WINS!";
            banner.className = "text-center py-3 px-4 rounded-lg font-bold text-lg mt-6 bg-gray-800";
        } else {
            banner.innerText = "IT'S A TIE!";
            banner.className = "text-center py-3 px-4 rounded-lg font-bold text-lg mt-6 bg-yellow-600";
        }

        // Show Results
        const resultsCard = document.getElementById('resultsCard');
        resultsCard.classList.remove('hidden');
        setTimeout(() => resultsCard.classList.add('opacity-100'), 10);
        
        revealBtn.innerText = "Results Revealed";

    } catch (err) {
        showError(err.message);
        revealBtn.disabled = false;
        revealBtn.innerText = "Reveal Results";
    }
}

function showError(msg) {
    const errorEl = document.getElementById('error');
    document.getElementById('errorMsg').innerText = msg;
    errorEl.classList.remove('hidden');
}
