ARCWorks Kathana Log Analyzer 1.0.0
===================================
Drop your exported Kathana chat logs in, compare up to 6 sessions side by side.

BUILD (once):
  1. Install Python 3.13 64-bit (tick "Add python.exe to PATH"). Not 3.14/3.15.
  2. Install Inno Setup 6.
  3. Double-click BUILD-PERSONAL.bat -> installer\ARCWorks-Kathana-Log-Analyzer-1.0.0-Setup.exe

USE:
  + Add logs (or drag .txt files in) -> Overview / Compare / Charts / Mobs & Loot.
  Click a log chip to make it the baseline for differences. Save report = HTML file.
  Merge = join several exports of the SAME session (duplicate lines counted once).

NOTES:
  * Rupiah = "[Auto] You gained" + "You earned" Rupiah. Selling to NPC is shown separately.
  * Kills are estimated from Prana rewards (the log has no kill line).
  * Active time skips gaps of 2+ minutes with no fighting/loot.
  * Kathana exports only the last ~1,100 lines, so one export covers about 12-60 min.

All numbers are calculated only from the logs you load. Your in-game results may differ
depending on play style, gear, buffs, map, party, and other game factors.
