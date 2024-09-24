import itertools
import subprocess

def generate_matches(teams):
    # Generates all possible matches where each team plays against each other
    # both as red and blue.
    for team1, team2 in itertools.permutations(teams, 2):
        yield team1, team2

def main():
    teams = [
    "MCTSPacmanAgent_offensiveAgent",
    "MCTSPacmanAgent_defensiveAgent",
    "MCTSPacmanAgent_OffensiveReflexAgent",
    "MCTSPacmanAgent_DefensiveReflexAgent",
    "offensiveAgent_defensiveAgent",
    "offensiveAgent_OffensiveReflexAgent",
    "offensiveAgent_DefensiveReflexAgent",
    "defensiveAgent_OffensiveReflexAgent",
    "defensiveAgent_DefensiveReflexAgent",
    "OffensiveReflexAgent_DefensiveReflexAgent",
    "MCTSPacmanAgent_MCTSPacmanAgent2",
    ]
    matches = list(generate_matches(teams))

    for red_team, blue_team in matches:
        command = f"python capture.py -r {red_team} -b {blue_team}"
        subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()