# Jay's NBA Script with GUI
import tkinter as tk
from tkinter import messagebox, filedialog
from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv2
from nba_api.stats.static import teams
import pandas as pd
from tqdm import tqdm
import threading


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


def fetch_and_save_data(season, output_file):
    """Fetch data for all teams and save it."""
    team_ids = get_nba_team_ids()
    all_team_data = []

    for team_id, team_name in team_ids.items():
        print(f"Calculating for {team_name}...")
        averages = calculate_position_averages(team_id, season)
        averages['Team'] = team_name
        all_team_data.append(averages)

    # Convert results to a DataFrame
    df = pd.DataFrame(all_team_data)
    df.to_csv(output_file, index=False)
    return df


def run_analysis():
    """Run the analysis based on user inputs."""
    season = season_entry.get()
    output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    if not season or not output_file:
        messagebox.showerror("Error", "Please enter a valid season and output file path!")
        return

    def process():
        try:
            messagebox.showinfo("Processing", "Fetching data. This may take a while...")
            fetch_and_save_data(season, output_file)
            messagebox.showinfo("Success", f"Data saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=process).start()


# GUI Setup
root = tk.Tk()
root.title("Jay's NBA Data Analyzer")

# Instructions Label
instruction_label = tk.Label(root, text="Welcome to Jay's NBA Data Analyzer!", font=("Arial", 16))
instruction_label.pack(pady=10)

# Season Entry
season_label = tk.Label(root, text="Enter the NBA season (e.g., 2023-24):")
season_label.pack()
season_entry = tk.Entry(root, width=30)
season_entry.pack(pady=5)

# Run Button
run_button = tk.Button(root, text="Run Analysis", command=run_analysis, bg="blue", fg="white", font=("Arial", 12))
run_button.pack(pady=20)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.quit, bg="red", fg="white", font=("Arial", 12))
exit_button.pack(pady=10)

# Start GUI Loop
root.mainloop()
