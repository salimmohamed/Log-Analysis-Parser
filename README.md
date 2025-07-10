# WoW Raid Log Analysis Parser

A Python tool for processing and summarizing the *text output* from the [Log Analysis Discord bot](https://discord.gg/BsDUfgKddA), which itself analyzes World of Warcraft raid logs. This project does **not** directly parse raw combat logs; instead, it works with the formatted summaries provided by the Discord bot, making it easy for raid teams to extract actionable insights from the bot's output. It supports multiple boss encounters and provides detailed performance metrics.

> **Note:** In the future, I hope to integrate with the WarcraftLogs API so this tool can directly analyze logs and become a standalone solution.

## Features
- Parses Discord bot-formatted raid summaries into structured data
- Tracks player deaths, raid-wide and boss-specific mechanics
- Generates CSV and text reports for analysis
- Validates data for consistency and accuracy
- Modular design for easy extension to new bosses and mechanics

## Usage
1. Ensure Python 3.x is installed (no external dependencies required)
2. Copy the *text output* from the Log Analysis App Discord bot into `data.txt`
3. Run:
   ```bash
   python clean_data.py
   ```
4. Output files:
   - `cleaned_data.csv`: For spreadsheet analysis
   - `cleaned_data.txt`: Human-readable stats
   - `verification_results.txt`: Data validation

## Extending & Contributing
- Modular boss class system for easy addition of new encounters
- Contributions welcome via Pull Request

---

*Developed to enhance the Log Analysis Discord bot. Join the [Log Analysis Discord](https://discord.gg/BsDUfgKddA) to learn more.* 
