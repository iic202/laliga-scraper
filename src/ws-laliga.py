#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict, Optional

class LaLigaScraper:
    
    def __init__(self, season: str = "2019"):

        self.season = season
        self.base_url = f"https://espndeportes.espn.com/futbol/posiciones/_/liga/ESP.1/temporada/{season}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """
        Fetch the ESPN page and return parsed HTML
        
        Returns:
            BeautifulSoup object or None if failed
        """
        print(f"Fetching La Liga {self.season} standings from ESPN...")
        
        try:
            
            time.sleep(1)
            
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()

            print(f"Page fetched successfully ({len(response.content):,} bytes)")
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.Timeout:
            print("Request timed out after 10 seconds")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def clean_team_name(self, raw_name: str) -> str:
        """
        Clean team name by removing abbreviations and extra text
        
        Args:
            raw_name (str): Raw team name from HTML
            
        Returns:
            str: Cleaned team name
        """
        if not raw_name:
            return ""
            
        # Remove content in parentheses (abbreviations)
        cleaned = re.sub(r'\s*\([^)]*\)', '', raw_name)
        
        # Remove extra whitespace
        cleaned = cleaned.strip()
        
        # If cleaned name is too short, return original
        if len(cleaned) < 3:
            return raw_name.strip()
            
        return cleaned
    
    def extract_standings_data(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract standings data from the parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            List[Dict]: List of team data dictionaries
        """
        print("\n🔍 Extracting standings data...")
        
        teams_data = []
        
        # Method 1: Try to find the standings table
        table = soup.find('table', class_='Table')
        if table:
            print("✅ Found standings table")
            teams_data = self._extract_from_table(table)
        
        # Method 2: If table method fails, try individual selectors
        if not teams_data:
            print("⚠️ Table method failed, trying individual selectors...")
            teams_data = self._extract_with_selectors(soup)
        
        # Method 3: If both fail, try a more generic approach
        if not teams_data:
            print("⚠️ Selector method failed, trying generic approach...")
            teams_data = self._extract_generic(soup)
        
        print(f"🎯 Extracted data for {len(teams_data)} teams")
        return teams_data
    
    def _extract_from_table(self, table) -> List[Dict]:
        """
        Extract data from HTML table structure
        ESPN uses two separate tables: one for teams, one for stats
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            List[Dict]: Team data
        """
        teams_data = []
        
        try:
            # Find all tables on the page
            all_tables = table.find_parent().find_all('table', class_='Table')
            
            if len(all_tables) < 2:
                print("❌ Not enough tables found")
                return teams_data
            
            # Table 1: Teams and positions
            teams_table = all_tables[0]
            # Table 2: Statistics  
            stats_table = all_tables[1]
            
            print(f"📊 Processing teams table with {len(teams_table.find_all('tr'))} rows")
            print(f"📊 Processing stats table with {len(stats_table.find_all('tr'))} rows")
            
            # Extract team data from first table
            team_rows = teams_table.find_all('tr')[1:]  # Skip header
            stat_rows = stats_table.find_all('tr')[1:]  # Skip header
            
            # Process each team
            for i, (team_row, stat_row) in enumerate(zip(team_rows, stat_rows), 1):
                try:
                    # Extract position and team name from team row
                    team_cell = team_row.find('td')
                    if not team_cell:
                        continue
                    
                    cell_text = team_cell.get_text(strip=True)
                    
                    # Extract position (first number in the cell)
                    position_match = re.search(r'^(\d+)', cell_text)
                    position = int(position_match.group(1)) if position_match else i
                    
                    # Extract team name (look for team links)
                    team_links = team_cell.find_all('a', href=lambda x: x and '/futbol/equipo/' in x)
                    team_name = ""
                    
                    # Find the best team name (prefer full name over abbreviation)
                    for link in team_links:
                        link_text = link.get_text(strip=True)
                        if len(link_text) > len(team_name) and len(link_text) > 3:
                            team_name = link_text
                    
                    # Clean the team name
                    team_name = self.clean_team_name(team_name) if team_name else f"Team {position}"
                    
                    # Extract stats from stats row
                    stat_cells = stat_row.find_all('td')
                    stats = []
                    
                    for cell in stat_cells:
                        stat_text = cell.get_text(strip=True)
                        try:
                            # Handle goal difference which might have + or -
                            if stat_text.startswith(('+', '-')):
                                stats.append(int(stat_text))
                            else:
                                stats.append(int(stat_text))
                        except ValueError:
                            stats.append(0)
                    
                    # Ensure we have 8 stats minimum
                    while len(stats) < 8:
                        stats.append(0)
                    
                    # Create team data
                    team_data = {
                        'position': position,
                        'team': team_name,
                        'games_played': stats[0],
                        'wins': stats[1],
                        'draws': stats[2],
                        'losses': stats[3],
                        'goals_for': stats[4],
                        'goals_against': stats[5],
                        'goal_difference': stats[6],
                        'points': stats[7]
                    }
                    
                    teams_data.append(team_data)
                    print(f"✅ {position:2d}. {team_name:<25} - {team_data['points']} pts")
                    
                except Exception as e:
                    print(f"⚠️ Error processing team {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error extracting from tables: {e}")
            
        return teams_data
    
    def _extract_with_selectors(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract data using specific CSS selectors
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            List[Dict]: Team data
        """
        teams_data = []
        
        try:
            # Find the main standings table
            table = soup.find('table', class_='Table')
            if not table:
                return teams_data
            
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')
            print(f"📊 Found {len(rows)} team rows")
            
            for i, row in enumerate(rows, 1):
                try:
                    cells = row.find_all('td')
                    if len(cells) < 8:
                        continue
                    
                    # Position (first cell)
                    position_text = cells[0].get_text(strip=True)
                    position = int(re.search(r'\d+', position_text).group()) if re.search(r'\d+', position_text) else i
                    
                    # Team name (second cell) - look for the main team link
                    team_cell = cells[1]
                    team_link = team_cell.find('a', class_='AnchorLink')
                    if team_link and '/futbol/equipo/' in team_link.get('href', ''):
                        team_name = self.clean_team_name(team_link.get_text(strip=True))
                    else:
                        # Fallback: get any link in the cell
                        all_links = team_cell.find_all('a')
                        team_name = ""
                        for link in all_links:
                            if '/futbol/equipo/' in link.get('href', ''):
                                team_name = self.clean_team_name(link.get_text(strip=True))
                                break
                        
                        if not team_name:
                            team_name = self.clean_team_name(team_cell.get_text(strip=True))
                    
                    # Stats (remaining cells)
                    stats = []
                    for cell in cells[2:10]:  # Take next 8 cells for stats
                        stat_text = cell.get_text(strip=True)
                        try:
                            # Handle goal difference which might have + or -
                            if stat_text.startswith('+') or stat_text.startswith('-'):
                                stats.append(int(stat_text))
                            else:
                                stats.append(int(stat_text))
                        except ValueError:
                            stats.append(0)
                    
                    # Ensure we have enough stats
                    while len(stats) < 8:
                        stats.append(0)
                    
                    team_data = {
                        'position': position,
                        'team': team_name,
                        'games_played': stats[0],
                        'wins': stats[1],
                        'draws': stats[2],
                        'losses': stats[3],
                        'goals_for': stats[4],
                        'goals_against': stats[5],
                        'goal_difference': stats[6],
                        'points': stats[7]
                    }
                    
                    teams_data.append(team_data)
                    print(f"✅ {position:2d}. {team_name:<25} - {team_data['points']} pts")
                    
                except Exception as e:
                    print(f"⚠️ Error processing row {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error with selector method: {e}")
            
        return teams_data
    
    def _extract_generic(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Generic extraction method as fallback
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            List[Dict]: Team data
        """
        teams_data = []
        
        try:
            # Look for any tables
            tables = soup.find_all('table')
            print(f"🔍 Found {len(tables)} tables on page")
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) >= 20:  # La Liga should have 20 teams
                    print(f"📊 Processing table with {len(rows)} rows")
                    
                    for i, row in enumerate(rows[1:], 1):  # Skip header
                        cells = row.find_all(['td', 'th'])
                        
                        if len(cells) >= 8:
                            try:
                                # Try to extract basic info
                                position = i
                                team_name = "Team " + str(i)
                                
                                # Look for team name in cells
                                for cell in cells[:3]:
                                    text = cell.get_text(strip=True)
                                    if len(text) > 3 and not text.isdigit():
                                        team_name = self.clean_team_name(text)
                                        break
                                
                                team_data = {
                                    'position': position,
                                    'team': team_name,
                                    'games_played': 0,
                                    'wins': 0,
                                    'draws': 0,
                                    'losses': 0,
                                    'goals_for': 0,
                                    'goals_against': 0,
                                    'goal_difference': 0,
                                    'points': 0
                                }
                                
                                teams_data.append(team_data)
                                print(f"✅ {position:2d}. {team_name}")
                                
                                if len(teams_data) >= 20:
                                    break
                                    
                            except Exception as e:
                                continue
                    
                    if teams_data:
                        break
                        
        except Exception as e:
            print(f"❌ Generic method failed: {e}")
            
        return teams_data
    
    def validate_data(self, teams_data: List[Dict]) -> bool:
        """
        Validate the scraped data
        
        Args:
            teams_data (List[Dict]): Team data to validate
            
        Returns:
            bool: True if data is valid
        """
        print("\n🔍 Validating data...")
        
        if not teams_data:
            print("❌ No data to validate")
            return False
        
        # Check number of teams
        if len(teams_data) != 20:
            print(f"⚠️ Expected 20 teams, got {len(teams_data)}")
        
        # Check positions
        positions = [team['position'] for team in teams_data]
        if positions == list(range(1, len(teams_data) + 1)):
            print("✅ Positions are sequential")
        else:
            print(f"⚠️ Positions not sequential: {positions[:5]}...")
        
    
    def save_to_csv(self, teams_data: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save data to CSV file
        
        Args:
            teams_data (List[Dict]): Team data to save
            filename (str, optional): Custom filename
            
        Returns:
            str: Filename of saved file
        """
        if not teams_data:
            print("❌ No data to save")
            return ""
        
        if filename is None:
            filename = f"laliga_{self.season}_standings.csv"
        
        # Create DataFrame
        df = pd.DataFrame(teams_data)
        df = df.sort_values('position')
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Data saved to {filename}")
        
        # Print summary
        print(f"\n📊 {self.season} La Liga Standings Summary:")
        print("=" * 50)
        for _, team in df.head(10).iterrows():
            print(f"{team['position']:2d}. {team['team']:<25} {team['points']:3d} pts")
        
        if len(df) > 10:
            print("    ...")
            for _, team in df.tail(3).iterrows():
                print(f"{team['position']:2d}. {team['team']:<25} {team['points']:3d} pts")
        
        return filename
    
    def scrape(self) -> Optional[pd.DataFrame]:
        """
        Main scraping method
        
        Returns:
            pd.DataFrame or None: Scraped data as DataFrame
        """
        print(f"🚀 Starting La Liga {self.season} scraper")
        print("=" * 60)
        
        # Step 1: Fetch page
        soup = self.fetch_page()
        if not soup:
            return None
        
        # Step 2: Extract data
        teams_data = self.extract_standings_data(soup)
        if not teams_data:
            print("❌ Failed to extract any data")
            return None
        
        # Step 3: Validate data
        is_valid = self.validate_data(teams_data)
        
        # Step 4: Save to CSV
        filename = self.save_to_csv(teams_data)
        
        # Step 5: Return DataFrame
        df = pd.DataFrame(teams_data).sort_values('position')
        
        print(f"\n✅ Scraping completed! Data saved to {filename}")
        return df


def main():
    """
    Main function to run the scraper
    """
    # You can change the season here
    season = "2019"
    
    # Create scraper instance
    scraper = LaLigaScraper(season=season)
    
    # Run scraper
    df = scraper.scrape()
    
    if df is not None:
        print(f"\n🎉 Successfully scraped {len(df)} teams!")
        print(f"📈 Points leader: {df.iloc[0]['team']} with {df.iloc[0]['points']} points")
    else:
        print("\n❌ Scraping failed")


if __name__ == "__main__":
    main()
