#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict, Optional
import os

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
    
    # Transforms team names from "Real Madrid (RMCF)" to "Real Madrid" for example
    def clean_team_name(self, raw_name: str) -> str:

        if not raw_name:
            return ""
            
        cleaned = re.sub(r'\s*\([^)]*\)', '', raw_name)
        
        cleaned = cleaned.strip()
        
        if len(cleaned) < 3:
            return raw_name.strip()
            
        return cleaned
    
    def extract_standings_data(self, soup: BeautifulSoup) -> List[Dict]:
        print("\n[?] Extracting standings data...")
        
        teams_data = []
        
        table = soup.find('table', class_='Table')
        if table:
            print("[+] Found standings table")
            teams_data = self._extract_from_table(table)
        else:
            print("[-] No standings table found")
        
        print(f"\n[??] Extracted data for {len(teams_data)} teams")
        return teams_data
    
    def _extract_from_table(self, table) -> List[Dict]:
        teams_data = []
        
        try:
            all_tables = table.find_parent().find_all('table', class_='Table')
            
            if len(all_tables) < 2:
                print("[-]Not enough tables found")
                return teams_data
            
            teams_table = all_tables[0] # Table 1: Teams and positions
            stats_table = all_tables[1] # Table 2: Statistics  
            
            print(f"[+] Processing teams table with {len(teams_table.find_all('tr'))} rows")
            print(f"[+] Processing stats table with {len(stats_table.find_all('tr'))} rows\n")
            
            # Extract team data from first table
            team_rows = teams_table.find_all('tr')[1:]  # Skip header
            stat_rows = stats_table.find_all('tr')[1:]  # Skip header
            
            # Process each team
            for i, (team_row, stat_row) in enumerate(zip(team_rows, stat_rows), 1):
                try:
                    # Extract position and team name from team row
                    team_cell = team_row.find('td')
                    
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
                    print(f"{position:2d}. {team_name:<25} - {team_data['points']} pts")
                    
                except Exception as e:
                    print(f"[-] Error processing team {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"[-] Error extracting from tables: {e}")
            
        return teams_data
    
    def validate_data(self, teams_data: List[Dict]) -> bool:
        
        if not teams_data:
            print("[-] No data to validate")
            return False
        
        if len(teams_data) != 20:
            print(f"[-] Expected 20 teams, got {len(teams_data)}")

        positions = [team['position'] for team in teams_data]
        if positions == list(range(1, len(teams_data) + 1)):
            print("[+] Positions are sequential")
        else:
            print(f"[-] Positions not sequential")

    def save_to_csv(self, teams_data: List[Dict], filename: Optional[str] = None) -> str:
    
        if not teams_data:
            print("[-] No data to save")
            return ""
        
        if filename is None:
            filename = f"laliga_{self.season}_standings.csv"
        
        full_path = os.path.join("data/laliga", filename)
        
        df = pd.DataFrame(teams_data)
        df = df.sort_values('position')
        
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"[+] Data saved to {full_path}")
         
        return full_path
    
    def scrape(self) -> Optional[pd.DataFrame]:
        print(f"[+] Starting La Liga {self.season} scraper")
        print("=" * 60)
        
        # Step 1: Fetch page
        soup = self.fetch_page()
        if not soup:
            return None
        
        # Step 2: Extract data
        teams_data = self.extract_standings_data(soup)
        if not teams_data:
            print("[-] Failed to extract any data")
            return None
        
        # Step 3: Validate data
        is_valid = self.validate_data(teams_data)
        
        # Step 4: Save to CSV
        filename = self.save_to_csv(teams_data)
        
        # Step 5: Return DataFrame
        df = pd.DataFrame(teams_data).sort_values('position')
        
        print(f"[+] Scraping completed! Data saved to {filename}")
        return df


def main():
    while True:
        try:
            season = input("[?] Which La Liga season do you want to scrape? (default: 2019): ").strip() or "2019"
            digit = int(season)
            if digit < 2003 or digit > 2025:
                print("[-] Invalid season! Please enter a year between 2003 and 2025.")
                continue
            break
        except ValueError:
            print("[-] Invalid input! Please enter a valid year.")
    
    scraper = LaLigaScraper(season=season)
    
    df = scraper.scrape()
    
    if df is not None:
        print(f"[+] Successfully scraped {len(df)} teams!")
        print(f"[+] Points leader: {df.iloc[0]['team']} with {df.iloc[0]['points']} points")
    else:
        print("\n[-] Scraping failed")


if __name__ == "__main__":
    main()
