from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

class BoardData(BaseModel):
    board: List[List[int]]

@app.get("/api/ping")
def root():
    return "Pong!"

@app.post("/api/get_move")
async def get_move(grid: list[list[Union[int, str]]]):
    return {"move": [1, 2]}

