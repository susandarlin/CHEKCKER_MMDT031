# Project 6 Report: Myanmar Checkers AI Visualizer

> [!IMPORTANT]
> **AUTOGRADER COMPLIANCE INSTRUCTIONS:**
> This report is parsed automatically by the autograder. To ensure you receive full credit for your work:
> 1. **Do not modify** the section headers (`## ...`) or bold field keys (e.g., `**Name:**`, `**Primary AI Algorithm:**`, `**Live Deployment URL:**`, etc.).
> 2. **Write your answers directly after** the colon `:` of each field, replacing the placeholder text completely (including the outer brackets `[` and `]`).
> 3. **Maintain the file structure**. Changing headers, bold titles, or deleting lines can cause the autograder to miss your responses and award 0 marks.

---

## Student Information
- **Name:** Su Sandar Lin
- **MMDT ID:** MMDT031

---

## Section 1: AI Agent Configuration
- **Primary AI Algorithm:** Depth-limited Minimax with Alpha-Beta Pruning and iterative deepening (searches depth 1 up to 6 with a 2-second time limit per move, falling back to the best move of the last fully completed depth). Baseline agents: a uniform Random agent (Easy) and a greedy one-ply Heuristic agent (Medium).
- **Pruning Technique:** Alpha-Beta Pruning (a branch is cut off as soon as alpha >= beta), made more effective by move ordering: captures with the most pieces taken and promotions are searched first, and the best move from the previous iteration is searched first at the next depth.
- **Evaluation Heuristic Strategy:** Weighted sum from the AI's point of view: material advantage (man = 100, king = 300), advancement of men toward promotion, back-row defence, central control, safe edge squares, and a threat/mobility term (credit for pending mandatory captures, otherwise number of legal moves); terminal positions score +/-100000, adjusted so faster wins are preferred.

---

## Section 2: Complexity & Evaluation Function Analysis
- **Board Configuration:** 8x8 board stored as a 2D list of integers, with play only on the 32 dark squares ((row + col) % 2 == 1). Each player starts with 12 men on the dark squares of their three nearest rows: Red (Player 1, value +1) at the bottom moves first and advances upward, Black (Player 2, value -1) at the top advances downward. Cells hold 0 = empty, +1/-1 = man, +2/-2 = king, so the sign gives the owner. The game state also tracks the side to move, a no-progress move counter, repetition counts of positions and an undo stack, so make_move/undo_move let the search explore the tree in place. Measured over 300 random games, the average branching factor is about 5-6 legal moves (7 at the opening; mandatory captures often reduce it to 1-2), but it rises to 13+ in the top 10% of positions with flying kings and peaked at 27, so a full game tree is far too large to search and depth-limited search with pruning is needed.
- **Piece Valuation & Rules:** Man = 100 points, King = 300 points (kings are flying, so they are worth about three men). Rules: men move one square diagonally forward and capture forward only; captures are mandatory and multi-jumps must be completed, with captured pieces removed at the end of the sequence and never jumped twice; a man reaching the far row is promoted to king and its turn ends; kings move and capture any distance along a diagonal and may land on any empty square beyond the captured piece. A player with no pieces or no legal moves loses; 50 moves without a capture or man move, or a position repeated 3 times, is a draw. Terminal positions are scored +/-100000 minus the search ply.
- **Heuristic Features Used:** (1) Material balance using the piece values above; (2) Advancement: +4 per row a man has moved toward promotion; (3) Back-row defence: +8 for men still on their own back row, which blocks enemy promotion; (4) Centre control: +6 for pieces on the 8 central squares; (5) Edge safety: +3 for pieces on the side edges, where they cannot be jumped; (6) Threat/mobility: if the side to move has a mandatory capture, it is credited with 80% of the best capture's material (so pieces left hanging are seen even at the search horizon), otherwise +2 per legal move. All features are summed for the AI and subtracted for the opponent, giving a zero-sum score.

---

## Section 3: Local Verification & Feature Checklist
*Check the algorithms, agents, and features you successfully ran and verified on your local development server by placing an `x` in the brackets (e.g., `[x]`):*
- [x] Myanmar Checkers Game Engine & Board State Representation
- [x] Legal Move Generation and Capture Mechanics
- [x] Minimax Search Algorithm with Alpha-Beta Pruning
- [x] Rule-Based / Heuristic AI Agent
- [x] Uniform Random Baseline Agent
- [x] Interactive Web Visualizer with Playable Board & Game Feedback

---

## Section 4: Deployed and Presentation Information
- **Deployment Platform:** Render
- **Live Deployment URL:** [Provide your live deployment site URL here]
- **Video Presentation Link:** [Provide an accessible link to your 5–7 minute video presentation]

---

## Section 5: Discussion
*Provide your written analysis for each point by replacing the bracket placeholders below:*
- **Explain how Alpha-Beta pruning optimizes decision-making in large-branching board games like Checkers without sacrificing tactical depth.**
    Plain Minimax explores about b^d positions. Alpha-Beta keeps two bounds: alpha (the best score the AI is already guaranteed) and beta (the best the opponent is guaranteed). When alpha >= beta, the remaining moves at that node are skipped because neither player would let the game reach that branch. The result is exactly the same move as full Minimax, so no tactical depth is lost; only irrelevant lines are ignored. With good move ordering (captures and promotions first, previous best move first) it visits about b^(d/2) nodes, letting the AI search roughly twice as deep. In my game, a depth-6 search from the opening took 0.66 s with about 6,200 nodes and 1,350 cutoffs, deep enough to see multi-jump and flying-king tactics.
- **Compare classical Adversarial Search & Heuristic Evaluation in Checkers with modern Generative AI / Deep Reinforcement Learning game agents (e.g., AlphaZero, MCTS, Value Networks, Process Reward Models).**
    My agent is classical: Minimax with Alpha-Beta searches the full game tree to a fixed depth, and a hand-crafted evaluation (material, advancement, back row, centre, safety, threats) scores the leaves. It is transparent, needs no training, and is tactically strong, but limited by its hand-tuned heuristic and search horizon. AlphaZero instead learns a value network (who is winning) and a policy network (which moves are promising) through self-play, and uses MCTS to search selectively deep along promising lines. This finds strategies humans never encoded, but needs huge compute and is harder to interpret. Generative AI reasoning follows the same pattern: a Process Reward Model scores intermediate reasoning steps like a value network, and tree search over steps plays the role of Minimax or MCTS. For a small game like Myanmar Checkers, Alpha-Beta with a good heuristic is efficient and practical; learned networks with MCTS scale better to much more complex problems.
