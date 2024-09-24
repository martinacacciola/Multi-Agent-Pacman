import subprocess
import itertools

def generate_matches(teams):
    # Generates all possible matches where each team plays against each other
    # both as red and blue.
    for team1, team2 in itertools.permutations(teams, 2):
        yield team1, team2

def main():
    teams = [
    "1_iteration",
    "50_iterations",
    "exploration_0.5",
    "exploration_10",
    "depth_3",
    "depth_50",
    "standard",
    ]  # Add all team names here
    matches = list(generate_matches(teams))
    results_file = "mcts_parameters_results.txt"

    with open(results_file, "w") as file:
        for red_team, blue_team in matches:
            command = f"python capture.py -r {red_team} -b {blue_team}"
            # Capture the output
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout

            # Write match details and output to file
            match_details = f"Match: {red_team} (Red) vs {blue_team} (Blue)\n"
            file.write(match_details)
            file.write(output + "\n")

if __name__ == "__main__":
    main()
