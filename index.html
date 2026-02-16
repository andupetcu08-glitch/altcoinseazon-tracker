<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Altcoin Season Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0d1117; color: white; font-family: sans-serif; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
        .target-banner { background-color: #064e3b; border: 1px solid #10b981; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body class="p-6">

    <div class="target-banner text-green-400">
        🎯 TARGETS: BTC.D: 46% | VIX: 13.8 | USDT.D: 5.1% | URPD: 86% | ETH/BTC: 0.085 | ML SELL Prob Target: 50% | ROTATION SCORE: 70%
    </div>

    <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="card text-center">
            <div class="text-gray-400 text-xs uppercase mb-1">Rotation Score</div>
            <div id="rotation" class="text-2xl font-bold text-red-500">--</div>
        </div>
        <div class="card text-center">
            <div class="text-gray-400 text-xs uppercase mb-1">BTC.D Live</div>
            <div id="btcd" class="text-2xl font-bold">--</div>
        </div>
        <div class="card text-center">
            <div class="text-gray-400 text-xs uppercase mb-1">ETH / BTC</div>
            <div id="ethbtc" class="text-2xl font-bold text-purple-400">--</div>
        </div>
        <div class="card text-center">
            <div class="text-gray-400 text-xs uppercase mb-1">USDT.D Live</div>
            <div id="usdtd" class="text-2xl font-bold text-green-400">--</div>
        </div>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="card">
            <div class="text-gray-400 text-xs uppercase mb-1">Portofoliu Actual (EUR)</div>
            <div id="port_eur" class="text-3xl font-bold text-green-400">--</div>
        </div>
        <div class="card text-right">
            <div class="text-gray-400 text-xs uppercase mb-1">Multiplier Actual</div>
            <div id="multiplier" class="text-3xl font-bold text-green-400">--</div>
            <div class="text-[10px] text-gray-500">(Investit: €101,235)</div>
        </div>
    </div>

    <div class="card overflow-hidden">
        <table class="w-full text-left">
            <thead>
                <tr class="text-gray-500 text-xs uppercase border-b border-gray-800">
                    <th class="pb-3">Moneda</th>
                    <th>Cantitate</th>
                    <th>Entry</th>
                    <th>Preț Actual</th>
                    <th>Target APR</th>
                    <th>Target MAI</th>
                    <th>Final Target</th>
                </tr>
            </thead>
            <tbody id="coin-table-body" class="text-sm">
                </tbody>
        </table>
    </div>

    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('data.json');
                if (!response.ok) throw new Error("Nu pot citi data.json");
                const data = await response.json();

                // 1. Actualizare Casete Principale
                // Rotation Score: Devine verde la 70%
                const rotEl = document.getElementById('rotation');
                rotEl.innerText = data.rotation + '%';
                rotEl.style.color = data.rotation >= 70 ? '#10b981' : '#ef4444';

                document.getElementById('btcd').innerText = data.btcd + '%';
                document.getElementById('ethbtc').innerText = data.ethbtc;
                document.getElementById('usdtd').innerText = data.usdtd + '%';
                
                // 2. Multiplier & Portofoliu (Fix undefinedx)
                document.getElementById('port_eur').innerText = '€' + data.port_eur.toLocaleString();
                document.getElementById('multiplier').innerText = data.mult + 'x';

                // 3. Populare Tabel Monede
                const tbody = document.getElementById('coin-table-body');
                tbody.innerHTML = ''; // Curatam tabelul inainte de refresh

                data.coins.forEach(coin => {
                    const colorClass = coin.change >= 0 ? 'text-green-400' : 'text-red-400';
                    tbody.innerHTML += `
                        <tr class="border-b border-gray-800 hover:bg-gray-800/50 transition">
                            <td class="py-4 font-bold uppercase">${coin.name} <span class="${colorClass} text-[10px] ml-1">${coin.change}%</span></td>
                            <td>${coin.q.toLocaleString()}</td>
                            <td class="text-gray-400">$${coin.entry}</td>
                            <td class="text-blue-400 font-bold">$${coin.price}</td>
                            <td class="text-yellow-500 font-semibold">$${coin.apr}</td>
                            <td class="text-yellow-500 font-semibold">$${coin.mai}</td>
                            <td class="text-purple-500 font-bold">$${coin.fib}</td>
                        </tr>
                    `;
                });

            } catch (error) {
                console.error("Eroare la incarcarea datelor:", error);
            }
        }

        // Ruleaza imediat, apoi la fiecare 30 de secunde
        updateDashboard();
        setInterval(updateDashboard, 30000);
    </script>
</body>
</html>
