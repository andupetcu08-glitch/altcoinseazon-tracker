<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Altcoin Tracker - Command Center 2026</title>
    <style>
        body { background: #0b0e14; color: #e1e1e1; font-family: 'Inter', sans-serif; padding: 20px; font-size: 11px; margin: 0; }
        
        /* 5. Text titlu casete (12px + Bold 800) */
        .m-label { font-size: 12px; color: #888; text-transform: uppercase; margin-bottom: 8px; font-weight: 800; letter-spacing: 0.8px; }
        .m-val { font-weight: bold; font-size: 22px; }

        /* 6. Glow pe toate liniile la hover */
        tr { transition: all 0.3s ease; border-bottom: 1px solid #1a1c24; }
        tr:hover { 
            background: rgba(0, 255, 136, 0.06) !important; 
            box-shadow: inset 0 0 25px rgba(0, 255, 136, 0.1);
        }

        .target-panel { 
            background: #052e16; border: 2px solid #22c55e; padding: 15px; border-radius: 12px; 
            margin-bottom: 20px; text-align: center; font-size: 15px; font-weight: bold; color: #fff;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
        }
        
        .top-nav { display: grid; grid-template-columns: repeat(5, 1fr) 1.5fr; gap: 12px; margin-bottom: 15px; }
        .macro-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 12px; }
        
        .m-card { 
            background: #1a1c24; padding: 18px; border-radius: 10px; border: 1px solid #333; 
            text-align: center; transition: transform 0.2s; 
        }
        .m-card:hover { border-color: #444; transform: translateY(-2px); }
        
        .up { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
        .down { color: #ef4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
        
        table { width: 100%; border-collapse: collapse; margin-top: 25px; background: #0f1218; border-radius: 12px; overflow: hidden; }
        th { text-align: left; color: #555; padding: 18px; border-bottom: 2px solid #222; text-transform: uppercase; font-size: 10px; }
        td { padding: 18px; font-size: 14px; }
        
        .st-btn { background: #111; border: 1px solid #222; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color
