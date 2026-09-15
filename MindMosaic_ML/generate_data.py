import numpy as np
import pandas as pd
import os

np.random.seed(42)

N_PLAYERS = 200
SESSIONS_PER_PLAYER = 10
NOISE = 0.05


def generate_players(n_players):
    skills = np.random.beta(2, 2, n_players)
    return pd.DataFrame({
        "player_id": np.arange(n_players),
        "skill": skills,
    })


def generate_session(player_id, skill, session_id):

    level = np.random.randint(1, 11)
    card_count = np.random.choice([2, 3, 4, 5, 6, 8])
    shuffle_moves = np.random.randint(2, 15)
    memorize_time = np.random.uniform(2.0, 8.0)

    difficulty_load = (
        0.30 * (level / 10) +
        0.35 * (card_count / 8) +
        0.20 * (shuffle_moves / 15) +
        0.15 * (1 - memorize_time / 8)
    )


    pressure = skill - difficulty_load


    accuracy = np.clip(
        0.55 + 0.35 * pressure + np.random.normal(0, NOISE),
        0.05, 1.0
    )

    mistakes = np.random.poisson(max(0.1, 3.0 - 2.5 * pressure))

    reaction_time = np.clip(
        2.5 - 1.2 * pressure + np.random.normal(0, 0.2),
        0.3, 6.0
    )

    completion_time = np.clip(
        25 + 15 * difficulty_load - 5 * skill + np.random.normal(0, 3),
        5, 90
    )

    best_streak = np.random.poisson(max(0.1, 4.0 + 5.0 * pressure))


    actual_perf = (
        0.45 * accuracy
        + 0.15 * np.clip(best_streak / 8, 0, 1)
        + 0.15 * np.clip((5 - reaction_time) / 4.5, 0, 1)
        + 0.15 * np.clip(1 / (1 + mistakes), 0, 1)
        + 0.10 * np.clip((60 - completion_time) / 55, 0, 1)
    )

    expected_accuracy   = np.clip(0.55 + 0.35 * pressure, 0.05, 1.0)
    expected_streak     = max(0.1, 4.0 + 5.0 * pressure)
    expected_reaction   = np.clip(2.5 - 1.2 * pressure, 0.3, 6.0)
    expected_mistakes   = max(0.1, 3.0 - 2.5 * pressure)
    expected_completion = np.clip(
        25 + 15 * difficulty_load - 5 * skill, 5, 90
    )

    expected_perf = (
        0.45 * expected_accuracy
        + 0.15 * np.clip(expected_streak / 8, 0, 1)
        + 0.15 * np.clip((5 - expected_reaction) / 4.5, 0, 1)
        + 0.15 * np.clip(1 / (1 + expected_mistakes), 0, 1)
        + 0.10 * np.clip((60 - expected_completion) / 55, 0, 1)
    )


    target = int(actual_perf > expected_perf)

    return {
        "player_id": player_id,
        "session_id": session_id,
        "level": level,
        "card_count": card_count,
        "shuffle_moves": shuffle_moves,
        "memorize_time": memorize_time,
        "accuracy": accuracy,
        "mistakes": mistakes,
        "reaction_time": reaction_time,
        "completion_time": completion_time,
        "best_streak": best_streak,
        "target": target,
    }


def generate_dataset():
    players = generate_players(N_PLAYERS)
    rows = []
    for _, player in players.iterrows():
        skill = player["skill"]
        pid = player["player_id"]
        for s in range(SESSIONS_PER_PLAYER):
            rows.append(generate_session(pid, skill, s))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs("Data", exist_ok=True)
    df = generate_dataset()
    df.to_csv("Data/game_data.csv", index=False)

    print(f"Generated {len(df)} rows from {N_PLAYERS} players")
    print(f"\nTarget balance:\n{df['target'].value_counts(normalize=True)}")
    print(f"\nPreview:\n{df.head()}")
    print(f"\nCorrelations with target:")
    print(df[['accuracy', 'mistakes', 'reaction_time',
              'completion_time', 'best_streak', 'target']].corr()['target'])