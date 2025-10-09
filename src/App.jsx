import { useState, useEffect } from "react";
import { produce } from "immer";
import "./App.css";

const bombNum = 20;
const size = 9;

function App() {
  const [grid, setGrid] = useState(Array.from({ length: size }, () => Array(size).fill("")));
  const [revealed, setRevealed] = useState([]);
  const [flagged, setFlagged] = useState([]);
  const [gameStarted, setGameStarted] = useState(false);

  function initialise(r, c) {
    setGameStarted(true);

    const newGrid = generateBoard(size, bombNum, r, c);
    setGrid(newGrid);
    setRevealed(Array.from({ length: size }, () => Array(size).fill(false)));
    setFlagged(Array.from({ length: size }, () => Array(size).fill(false)));

    revealTile(r, c, newGrid);
  }

  function revealTile(r, c, gridToUse = grid) {
    if (gridToUse[r][c] === 9) {
      setRevealed(
        produce(draft => {
          draft[r][c] = true;
        })
      );

      setTimeout(() => {
        resetBoard();
      }, 1000);

      return;
    }

    setRevealed(
      produce(draft => {
        function floodFill(row, col) {
          if (row < 0 || row >= size || col < 0 || col >= size) return;
          if (draft[row][col]) return;

          draft[row][col] = true;

          if (gridToUse[row][col] === 0) {
            for (let dr = -1; dr <= 1; dr++) {
              for (let dc = -1; dc <= 1; dc++) {
                if (dr !== 0 || dc !== 0) {
                  floodFill(row + dr, col + dc);
                }
              }
            }
          }
        }

        floodFill(r, c);
      })
    );
  }

  function flagTile(r, c) {
    setFlagged(
      produce(draft => {
        if (!revealed[r][c]) {
          draft[r][c] = !draft[r][c];
        }
      })
    );
  }

  function resetBoard() {
    setRevealed(Array.from({ length: size }, () => Array(size).fill(false)));
    setFlagged(Array.from({ length: size }, () => Array(size).fill(false)));
    setGrid(Array.from({ length: size }, () => Array(size).fill("")));
    setGameStarted(false);
  }

  async function AIMove() {
    try {
      const response = await fetch("/api/get_move", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(grid.map((row, y) => row.map((cell, x) => (revealed[y][x] ? cell : "")))),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Move from backend:", data);
      return data;
    } catch (error) {
      console.error("Error fetching move:", error);
      return null;
    }
  }

  return (
    <>
      <div className="board">
        {grid.map((row, r) =>
          row.map((cell, c) => (
            <Tile
              key={`${r}-${c}`}
              value={cell}
              isRevealed={revealed[r]?.[c]}
              onClick={() => (gameStarted ? revealTile(r, c) : initialise(r, c))}
              isFlagged={flagged[r]?.[c]}
              onContextMenu={() => flagTile(r, c)}
            />
          ))
        )}
      </div>
      <button className="button" onClick={resetBoard}>
        Reset
      </button>
      <button className="button" onClick={AIMove}>
        AI Move
      </button>
    </>
  );
}

function Tile({ value, isRevealed, onClick, isFlagged, onContextMenu }) {
  return (
    <button
      className="tile rounded-0"
      onClick={onClick}
      onContextMenu={e => {
        e.preventDefault();
        onContextMenu();
      }}
    >
      {isFlagged
        ? "🚩"
        : isRevealed
        ? value === 9
          ? "X"
          : value > 0
          ? value
          : ""
        : ""}
    </button>
  );
}

function generateBoard(size, bombNum, safeR, safeC) {
  const grid = Array.from({ length: size }, () => Array(size).fill(0));

  function isSafe(r, c) {
    return Math.abs(r - safeR) <= 1 && Math.abs(c - safeC) <= 1;
  }

  let placed = 0;
  while (placed < bombNum) {
    let r = Math.floor(Math.random() * size);
    let c = Math.floor(Math.random() * size);

    if (grid[r][c] === 9 || isSafe(r, c)) continue;

    grid[r][c] = 9;
    placed++;
  }

  const directions = [
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [0, -1],
    [0, 1],
    [1, -1],
    [1, 0],
    [1, 1],
  ];

  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (grid[r][c] === 9) continue;

      let count = 0;
      for (const [dr, dc] of directions) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
          if (grid[nr][nc] === 9) count++;
        }
      }
      grid[r][c] = count;
    }
  }

  return grid;
}

export default App;