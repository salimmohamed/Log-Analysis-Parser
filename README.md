# WoW Raid Log Analysis Parser

A sophisticated Python-based log analysis tool designed to process and analyze World of Warcraft raid logs from the [Log Analysis App](https://discord.gg/BsDUfgKddA) Discord bot. This project demonstrates advanced data processing, pattern recognition, and statistical analysis capabilities, transforming raw raid logs into actionable insights for raid teams.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Discord](https://img.shields.io/badge/Discord-Log%20Analysis%20App-7289DA)

## 🎯 Project Overview

This tool was developed to enhance the capabilities of the Log Analysis App Discord bot, which provides real-time raid log analysis for World of Warcraft raid teams. Currently focused on the Mug'Zee encounter, the parser:

- Transforms Discord-formatted logs into structured data
- Provides deeper analysis than the bot's basic output
- Tracks specific mechanics and player performance
- Generates comprehensive statistics for performance analysis
- Helps raid teams make data-driven decisions to improve performance

## 🔌 Integration

### Log Analysis App Integration
- Processes logs directly from the [Log Analysis App](https://discord.gg/BsDUfgKddA) Discord bot
- Compatible with the bot's standard output format
- Enhances the bot's basic analysis with additional insights
- Designed for easy extension to future boss encounters

### Current Scope
- **Boss Focus**: Mug'Zee encounter analysis
- **Mechanics Tracked**: 
  - Unstable Cluster Bomb soaking
  - Goblin-Guided Rocket soaking
  - Boss/Goon enrage
  - Player-specific mechanics (Frostshatter Spear, Stormfury stun, etc.)
- **Analysis Depth**: Detailed tracking of both raid-wide and individual player performance

### Extensibility
The modular design allows for easy adaptation to:
- Future boss encounters in the current tier
- New mechanics and abilities in upcoming tiers
- Additional analysis metrics and statistics
- Integration with other analysis tools

## 💻 Technical Implementation

### Core Technologies
- **Python 3.x**: Leveraged for robust data processing and analysis
- **Regular Expressions**: Advanced pattern matching for log parsing
- **Data Structures**: Efficient use of defaultdict for data aggregation
- **CSV Processing**: Structured data export for easy analysis
- **Character Encoding**: Sophisticated handling of Unicode characters

### Key Technical Features
- **Pattern Recognition**: Complex regex patterns to identify and categorize raid events
- **Data Normalization**: Intelligent handling of special characters and inconsistent formatting
- **Statistical Analysis**: Automated generation of detailed performance metrics
- **Data Verification**: Built-in validation system ensuring parsing accuracy
- **Modular Design**: Clean, maintainable code structure with separate concerns

## 📊 Features

### Data Processing
- Intelligent parsing of raid logs with timestamp tracking
- Automated extraction of player deaths and raid mechanics
- Special character normalization for consistent data handling
- Duration calculation and attempt sequencing

### Analysis Capabilities
- **Raid Mistakes Tally**: Tracks non-player mistakes (e.g., unsoaked mechanics)
- **Player Mistake Tally**: Individual player performance metrics
- **Mechanic Mistake Tally**: Detailed analysis of specific mechanic failures
- **Time-based Analysis**: Duration tracking for performance optimization

### Output Generation
- **CSV Export**: Structured data for spreadsheet analysis
- **Text Reports**: Human-readable detailed statistics
- **Verification Logs**: Data integrity validation reports

## 🛠️ Usage

### Prerequisites
- Python 3.x
- Standard library modules (no external dependencies)
- Access to Log Analysis App Discord bot output

### Quick Start
1. Clone the repository
2. Copy your Log Analysis App Discord bot output into `data.txt`
3. Run the script:
   ```bash
   python clean_data.py
   ```
4. Access the generated reports:
   - `cleaned_data.csv` for spreadsheet analysis
   - `cleaned_data.txt` for detailed statistics
   - `verification_results.txt` for data validation

### Input Format Example
The script processes logs in the Log Analysis App format:
```
Mug'Zee #1   (4:33)
:warning: Experimental :warning:
:MugZee_mine: Player died to popping a mine (1:23.4)
:MugZee_spear: Player died to Frostshatter Spear (2:45.6)
5/24/2025 6:40 PM
```

## 🔍 Technical Details

### Tracked Mechanics
- **Raid Mechanics**:
  - Unstable Cluster Bomb soaking
  - Goblin-Guided Rocket soaking
  - Boss/Goon enrage tracking
- **Player Mechanics**:
  - Frostshatter Spear
  - Stormfury stun
  - Goon's frontal
  - Molten Golden Knuckles frontal
  - Electric fence
  - Mine management

### Data Verification System
- Attempt count validation
- Timestamp consistency checking
- Event pattern verification
- Player death record validation
- Comprehensive error reporting

### Character Handling
Sophisticated normalization of special characters:
```
'é' → 'e'    'ò' → 'o'    'ñ' → 'n'
'ç' → 'c'    'ß' → 'ss'   (and more)
```

## 🚀 Future Enhancements

Planned improvements include:
- Support for additional boss encounters in current tier
- Framework for easy addition of new boss mechanics
- Direct Discord bot integration for real-time analysis
- Web interface for real-time log analysis
- Machine learning integration for pattern prediction
- API development for integration with other tools
- Enhanced visualization capabilities
- Support for cross-boss performance comparison

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

*Developed as a personal project to enhance the capabilities of the Log Analysis App Discord bot. Currently focused on the Mug'Zee encounter, this tool demonstrates the potential for automated raid log analysis across multiple boss encounters. The modular design allows for easy extension to future boss fights and raid tiers. Join the [Log Analysis App Discord](https://discord.gg/BsDUfgKddA) to learn more about raid log analysis.* 