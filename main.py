from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

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

            #First rule: if there is a 1 with 7 surrounded reveals and none of which are mines, then flag the 8th tile 
            if neighbor_count >= (8 - grid[r][c]) and grid[r][c] != 9 and  grid[r][c] != 0 and grid[r][c] != -1:

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
    async def get_move_basic(grid: list[list[int]]):
    #This method finds the probabilities of a tile being safe and picks the tile most likely to be safe
