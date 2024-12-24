from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv2
from nba_api.stats.static import teams
import pandas as pd
from tqdm import tqdm

def get_nba_team_ids():
    """Fetch all NBA team IDs and names."""
    nba_teams = teams.get_teams()
    return {team['id']: team['full_name'] for team in nba_teams}

def fetch_games_for_team(team_id, season='2023-24'):
    """Fetch all games for a given team."""
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=season)
    games = gamefinder.get_data_frames()[0]
    return games

def fetch_box_scores(game_id):
    """Fetch box score data for a given game ID."""
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    player_stats = boxscore.player_stats.get_data_frame()
    return player_stats

def calculate_position_averages(team_id, season='2023-24'):
    """Calculate average points scored by positions against a team."""
    games = fetch_games_for_team(team_id, season)
    position_scores = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': []}

    for _, game in tqdm(games.iterrows(), total=len(games), desc=f"Processing games for team ID {team_id}"):
        game_id = game['GAME_ID']
        box_scores = fetch_box_scores(game_id)

        # Filter for opponents' players only
        opponent_stats = box_scores[box_scores['TEAM_ID'] != team_id]

        # Approximate positions based on player names (PG, SG, SF, PF, C)
        for _, player in opponent_stats.iterrows():
            position = player['START_POSITION']
            if position in position_scores:
                position_scores[position].append(player['PTS'])

    # Calculate average points for each position
    position_averages = {pos: (sum(scores) / len(scores)) if scores else 0 for pos, scores in position_scores.items()}
    return position_averages

def main():
    team_ids = get_nba_team_ids()
    season = '2023-24'
    all_team_data = []

    for team_id, team_name in team_ids.items():
        print(f"Calculating for {team_name}...")
        averages = calculate_position_averages(team_id, season)
        averages['Team'] = team_name
        all_team_data.append(averages)

    # Convert results to a DataFrame
    df = pd.DataFrame(all_team_data)
    print(df)

    # Save results to a CSV file
    df.to_csv('nba_team_position_averages.csv', index=False)

if __name__ == "__main__":
    main()
