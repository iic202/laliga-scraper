# ESPN La Liga Standings Scraper

A comprehensive web scraper for extracting La Liga football standings from ESPN Deportes. This scraper can extract complete season data including team positions, statistics, and points for any La Liga season.

## Features

- Scrape complete La Liga standings for any season from 2003/04 to Current
- Extract detailed team statistics (games played, wins, draws, losses, goals, points)
- CSV export


## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Dependencies

- `requests` - For HTTP requests
- `beautifulsoup4` - For HTML parsing
- `pandas` - For data manipulation and CSV export
- `lxml` - For improved HTML parsing performance

## Usage

### Basic Usage

Run the scraper for the 2019 season (default):

```bash
python ws-laliga.py
```

### Custom Season

To scrape a different season, modify the `season` variable in the `main()` function:

```python
def main():
    # Change this to your desired season
    season = "2020"  # or "2021", "2022", etc.
    
    scraper = LaLigaScraper(season=season)
    df = scraper.scrape()
```

## Output

The scraper generates:

1. **Console Output**: Real-time progress and results
2. **CSV File**: Complete data saved as `laliga_YYYY_standings.csv`
3. **Pandas DataFrame**: For programmatic data access

### CSV Structure

| Column | Description |
|--------|-------------|
| position | League position (1-20) |
| team | Team name |
| games_played | Number of games played |
| wins | Number of wins |
| draws | Number of draws |
| losses | Number of losses |
| goals_for | Goals scored |
| goals_against | Goals conceded |
| goal_difference | Goal difference (+/-) |
| points | Total points |


## How It Works

The scraper uses a sophisticated multi-method approach:

1. **Primary Method**: Parses ESPN's dual-table structure (team names + statistics)
2. **Fallback Methods**: CSS selectors and generic table parsing
3. **Data Validation**: Checks for expected team count and famous teams
4. **Error Handling**: Graceful fallbacks and detailed error reporting

### Anti-Bot Measures

- Uses realistic browser headers (Safari/macOS)
- Implements request delays
- Handles redirects and timeouts
- Multiple extraction strategies

## URL Format

ESPN URLs follow this pattern:
```
https://espndeportes.espn.com/futbol/posiciones/_/liga/ESP.1/temporada/{YEAR}
```

## Legal and Ethical Use

- This scraper is for educational and personal use
- Respect ESPN's robots.txt and terms of service
- Use delays between requests to avoid overloading servers
- Consider ESPN's public API if available for commercial use

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This means you can freely use, modify, and distribute this code for personal, educational, or commercial purposes, as long as you include the original license notice.

---

**Note**: This scraper relies on ESPN Deportes' current HTML structure. If ESPN changes their website layout, the scraper may need updates.
