from fastapi import FastAPI
from rl_env import MinesweeperEnv
from pydantic import BaseModel
from typing import List
import json
import random
import numpy as np

app = FastAPI()
Q = {}

class BoardData(BaseModel):
    board: List[List[int]]

@app.get("/api/ping")
def root():
    return "Pong!"

@app.post("/api/get_move_basic")
async def get_move_basic(grid: list[list[int]]):
    rows = len(grid)
    cols = len(grid[0])

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]

    for r in range(rows):
        for c in range(cols):
            neighbor_count = 0
            mine_count = 0
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if grid[nr][nc] == 9:
                        mine_count +=1
                    elif grid[nr][nc] >= 0:
                        neighbor_count += 1

            if neighbor_count >= (8 - grid[r][c]) and grid[r][c] != 9 and grid[r][c] != 0 and grid[r][c] != -1:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == -1:
                        return {"move": [nr, nc], "flag": True}

            if mine_count == grid[r][c] and neighbor_count + mine_count < 8:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == -1:
                        return {"move": [nr, nc], "flag": False}
    return {"move": [0, 0], "flag": False}

@app.post("/api/get_move_guess")
async def get_move_guess(grid: list[list[int]]):
    rows, cols = len(grid), len(grid[0])
    probs = [[0.0 for _ in range(cols)] for _ in range(rows)]
    counts = [[0 for _ in range(cols)] for _ in range(rows)]

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val < 0 or val == 9:
                continue

            covered_neighbors = []
            flagged = 0
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    nval = grid[nr][nc]
                    if nval == -1:
                        covered_neighbors.append((nr, nc))
                    elif nval == 9:
                        flagged += 1

            if covered_neighbors:
                remaining = val - flagged
                if remaining < 0:
                    continue
                p = remaining / len(covered_neighbors)
                for (nr, nc) in covered_neighbors:
                    probs[nr][nc] += p
                    counts[nr][nc] += 1

    best_move = None
    best_p = 1.0
    for r in range(rows):
        for c in range(cols):
            if counts[r][c] > 0:
                probs[r][c] /= counts[r][c]
            elif grid[r][c] == -1:
                probs[r][c] = 0.5
            else:
                probs[r][c] = -1.0
            if grid[r][c] == -1 and probs[r][c] >= 0 and probs[r][c] < best_p:
                best_p = probs[r][c]
                best_move = [r, c]

    return {"move": best_move, "flag": False}

def local_state(grid, r, c):
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),  (0, 0),  (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    state = []
    rows, cols = len(grid), len(grid[0])
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            state.append(grid[nr][nc])
        else:
            state.append(-2)
    return tuple(state)

@app.post("/api/train_rl")
def train_rl(episodes: int = 10000, alpha: float = 0.1, gamma: float = 0.9):
    global Q
    env = MinesweeperEnv(size=5, bombs=3)
    for ep in range(episodes):
        state = env.reset()
        done = False
        while not done:
            actions = [(r, c) for r in range(env.size) for c in range(env.size) if not env.revealed[r, c]]
            action = random.choice(actions)
            r, c = action
            next_state, reward, done = env.step(r, c)
            key = local_state(state, r, c)
            next_key = local_state(next_state, r, c)
            Q[(key, action)] = Q.get((key, action), 0) + alpha * (
                reward + gamma * max([Q.get((next_key, a), 0) for a in actions], default=0)
                - Q.get((key, action), 0)
            )
            state = next_state

    with open("q_table.json", "w") as f:
        json.dump({str(k): v for k, v in Q.items()}, f)
    return {"message": f"Trained for {episodes} episodes!"}

@app.post("/api/get_move_rl")
async def get_move_rl(grid: list[list[int]]):
    global Q
    actions = [(r, c) for r in range(len(grid)) for c in range(len(grid)) if grid[r][c] == -1]
    best_action = max(actions, key=lambda a: Q.get((local_state(grid, *a), a), 0), default=random.choice(actions))
    return {"move": best_action, "flag": False}