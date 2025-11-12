import numpy as np
import random

class MinesweeperEnv:
    def __init__(self, size=9, bombs=10):
        self.size = size
        self.bombs = bombs
        self.reset()

    def reset(self):
        self.board = self._generate_board()
        self.revealed = np.zeros((self.size, self.size), dtype=bool)
        self.done = False
        return self._get_observation()

    def _generate_board(self):
        board = np.zeros((self.size, self.size), dtype=int)
        bombs = set()
        while len(bombs) < self.bombs:
            r, c = random.randrange(self.size), random.randrange(self.size)
            bombs.add((r, c))
        for r, c in bombs:
            board[r, c] = 9
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and board[nr, nc] != 9:
                        board[nr, nc] += 1
        return board

    def _get_observation(self):
        obs = np.full((self.size, self.size), -1)
        obs[self.revealed] = self.board[self.revealed]
        return obs

    def step(self, r, c):
        if self.revealed[r, c]:
            return self._get_observation(), -0.1, False  # penalty for redundant move
        self.revealed[r, c] = True
        if self.board[r, c] == 9:
            return self._get_observation(), -10, True    # hit a mine
        reward = 1
        done = np.all((self.board == 9) | self.revealed)
        if done:
            reward += 50
        return self._get_observation(), reward, done