# ⚔️ ARCWorks Kathana Log Analyzer

Ever wondered which farming spot *actually* pays better? Drop in your exported Kathana chat logs and find out. Compare up to 6 sessions side by side: Rupiah, Prana, damage, mobs and loot. No spreadsheets, just cards, charts and crowns. 👑

## What you get
- **Overview**: one card per log with Rupiah, Prana and damage, per-hour and per-24h rates, estimated kills, drops, and quick tips. The best run gets a 🏆.
- **Compare**: see the difference against any log you pick, with a 👑 on the best result for each stat.
- **Charts**: Rupiah and Prana over time, damage per minute, per-hour bars.
- **Mobs & Loot**: damage dealt to and taken from each mob, plus your drops.
- Idle-time detection, best 10-minute window, an "inventory full" warning, merging exports from the same session, and **Save report** to an HTML file you can share with the guild.

## Getting your logs
Use the game's chat log export (it saves `.txt` files named like `2026_11_1_0.txt`). Each export keeps only the last ~1,100 lines (about 12–60 minutes of play), so export often during a long session and use **Merge** to join them.

## Build it (Windows)
1. Install **Python 3.13 64-bit** and tick "Add python.exe to PATH". (3.14/3.15 won't work yet.)
2. Install **Inno Setup 6**.
3. Double-click `BUILD-PERSONAL.bat`. Your installer appears in `installer\`.

Run the tests with `python tests/run_tests.py`. The sample logs in `tests/samples` only contain system lines; all player chat and names were removed.

## Disclaimer
All numbers are calculated only from the logs you load. Your in-game results may differ depending on play style, gear, buffs, map, party, and other game factors.

This is a fan-made tool and is **not affiliated with Kathana or its publisher**.

## License
MIT © 2026 ARCWorksPH. Includes Chart.js (MIT).
