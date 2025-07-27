# ESPN La Liga Standings Scraper

A web scraper for extracting La Liga football standings from ESPN Deportes. This scraper can extract complete season data including team positions, statistics, and points for any La Liga season.

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

## Usage

Run with the command shown below, you will we asked to enter your desired season between 2003 and 2025 (default season is 2019).

```bash
python ws-laliga.py
```

## Output

The scraper generates:

1. **Console Output**: Real-time progress and results
2. **CSV File**: Complete data saved as `laliga_YYYY_standings.csv`
3. **Pandas DataFrame**: For programmatic data access

### CSV Structure

| Column | Description |
|--------|-------------|
| season | League season (2003-2024)
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This scraper relies on ESPN Deportes' current HTML structure. If ESPN changes their website layout, the scraper may need updates.
