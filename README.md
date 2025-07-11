# 🐸 Two-Player Freckers

This is Part B of the COMP30024 Artificial Intelligence project at the University of Melbourne. The goal of this project is to implement an intelligent agent to play the competitive two-player game **Freckers** optimally.

## 🧠 Overview

Freckers is a strategic turn-based board game where two players compete to move their frogs to the opposite side of an 8×8 board. Each player controls six frogs, and the first to move all frogs to the final row wins. The challenge lies in making optimal decisions that consider both your own progress and blocking or delaying the opponent.

Our AI agent is designed to make real-time, optimal decisions using a hybrid of **A\*** search and **Minimax with Alpha-Beta Pruning**, tailored for a competitive two-player setting.

---

## 🚀 Strategy

### 🔎 Search Algorithms Used

We combined two search paradigms:

- **Minimax with Alpha-Beta Pruning**  
  For adversarial decision-making, we used Minimax to evaluate and choose the best frog to move, while considering potential opponent responses. Alpha-Beta Pruning was added to efficiently cut off non-promising branches and reduce computation.

- **A\* Search**  
  To find the best path for an individual frog to reach its goal row, we applied the A* algorithm with a custom heuristic. This significantly improved performance compared to generating all possible jump sequences.

### 🧮 Heuristic Function

- We used **Euclidean distance** from a frog to the goal row to estimate cost in A*. This heuristic is both **admissible** and **consistent**.
- For board evaluation in Minimax, we designed a **multi-dimensional scoring function** that accounts for:
  - Movable frogs
  - Distance to goal
  - Frogs already at the goal
  - Opponent progress

 ## 👥 Team Contributions

- **[Yurim CHO]** implemented the core search algorithms (A*, Alpha-Beta Minimax), heuristic functions, path validation, and game state evaluation system.
- **[Chuanmaio YU]** contributed to planning the agent's strategy, evaluating alternative approaches, writing the project report, and testing the agent's performance across multiple scenarios.
