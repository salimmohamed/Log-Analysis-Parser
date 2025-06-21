# WoW Raid Log Analysis Parser

A sophisticated Python-based log analysis tool designed to process and analyze World of Warcraft raid logs from the [Log Analysis App](https://discord.gg/BsDUfgKddA) Discord bot. This project demonstrates advanced data processing, pattern recognition, and statistical analysis capabilities, transforming raw raid logs into actionable insights for raid teams.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Discord](https://img.shields.io/badge/Discord-Log%20Analysis%20App-7289DA)

## 🎯 Project Overview

This tool was developed to enhance the capabilities of the Log Analysis App Discord bot, which provides real-time raid log analysis for World of Warcraft raid teams. The parser supports multiple boss encounters and:

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
- **Supported Bosses**: 
  - **Mug'Zee**: Goblin-themed encounter with cluster bombs and rockets
  - **Stix Bunkjunker**: Mechanical boss with scrapmaster mechanics and bombshells
  - **Gallywix**: Complex encounter with canisters, enrage mechanics, and multiple phases
- **Mechanics Tracked**: 
  - Boss-specific mechanics for each encounter
  - Player deaths and mistake analysis
  - Raid-wide mechanic failures
  - Performance timing and duration tracking
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
- **Object-Oriented Design**: Modular boss class system for easy extension

### Key Technical Features
- **Pattern Recognition**: Complex regex patterns to identify and categorize raid events
- **Data Normalization**: Intelligent handling of special characters and inconsistent formatting
- **Statistical Analysis**: Automated generation of detailed performance metrics
- **Data Verification**: Built-in validation system ensuring parsing accuracy
- **Modular Design**: Clean, maintainable code structure with separate concerns
- **Boss-Specific Parsing**: Custom logic for each boss encounter's unique mechanics

## 📊 Features

### Data Processing
- Intelligent parsing of raid logs with timestamp tracking
- Automated extraction of player deaths and raid mechanics
- Special character normalization for consistent data handling
- Duration calculation and attempt sequencing
- Boss-specific event detection and parsing

### Analysis Capabilities
- **Raid Mistakes Tally**: Tracks non-player mistakes (e.g., unsoaked mechanics)
- **Player Mistake Tally**: Individual player performance metrics
- **Mechanic Mistake Tally**: Detailed analysis of specific mechanic failures
- **Time-based Analysis**: Duration tracking for performance optimization
- **Boss-Specific Analysis**: Custom metrics for each boss encounter

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

### Tracked Mechanics by Boss

#### Mug'Zee
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

#### Stix Bunkjunker
- **Raid Mechanics**:
  - Ball management and expiration
  - Bombshell handling
  - Scrapmaster mechanics with markers
- **Player Mechanics**:
  - Ball expiration
  - Bombshell hits
  - Missed scrapmaster assignments

#### Gallywix
- **Raid Mechanics**:
  - Canister soaking (DPS and Heal variants)
  - Wrenchmonger enrage management
  - Sentry Shock Barrage handling
  - Technician Juice It mechanics
- **Player Mechanics**:
  - Giga Blast and residue damage
  - Cuff Bomb management
  - Various boss abilities and adds

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

*Developed as a personal project to enhance the capabilities of the Log Analysis App Discord bot. Currently supporting Mug'Zee, Stix Bunkjunker, and Gallywix encounters, this tool demonstrates the potential for automated raid log analysis across multiple boss encounters. The modular design allows for easy extension to future boss fights and raid tiers. Join the [Log Analysis App Discord](https://discord.gg/BsDUfgKddA) to learn more about raid log analysis.* 