## AI Policy: Use & Declaration
- **Limited AI Use:** AI coding assistants (e.g., GitHub Copilot) may be used for syntax suggestions, debugging, coding support, and learning assistance.
- **Prohibited:** Do not paste project prompts, guidelines, problem statements, or substantial portions of project materials into AI systems for code generation, completion, or debugging.
- **Responsibility:** Submitted work must reflect your own understanding, implementation, and problem-solving effort.

### AI Use Declaration

1. Complete the [PETRA AI Student Declaration](https://www.petraai.org/student) based on your actual AI use for this project.
2. Generate and save the declaration image as **`AI_declaration.png`**.
3. Include **`AI_declaration.png`** in your project repository root.

> **Required:** Your declaration must accurately reflect how you used AI tools for this project.

---

## Project Overview: Myanmar Checkers AI Visualizer

In this project, you will design, implement, and deploy a full-stack interactive Game AI web application for **Myanmar Checkers**. The system enables human users to play against intelligent AI opponents powered by classical Adversarial Search strategies (Minimax with Alpha-Beta Pruning and Heuristic Evaluation) alongside baseline agents.

The final outcome of this project is a fully functional web application deployed to a public, live URL.

---

### Learning Objectives

1. **Adversarial Search in Board Games:** Formulate and solve zero-sum game trees for Myanmar Checkers.
2. **Search Optimization with Alpha-Beta Pruning:** Implement efficient $\alpha$-$\beta$ branch cutoffs to optimize search depth within practical move time limits.
3. **Heuristic Evaluation Functions:** Design evaluation heuristics to assess intermediate game state advantage.
4. **Game Engine Implementation:** Build the core game logic, board representation, legal move validation, state transitions, and victory/draw condition evaluations.
5. **Interactive Full-Stack Web Development:** Build a responsive web application (Flask backend and interactive frontend) allowing human-versus-AI gameplay.
6. **Connections to Modern AI Reasoning:** Relate classical adversarial search and heuristic evaluation to modern Reinforcement Learning game architectures (e.g., MCTS, Value Networks, AlphaZero).

---

## Your Job

1. Design and implement the Myanmar Checkers game engine, board representation, legal moves, capture mechanics, and win/draw condition evaluation in `checkers.py`.
2. Implement AI search agents in `agent.py`:
   - `RandomAgent`: Baseline uniform legal move baseline (Easy).
   - `HeuristicAgent`: Fast greedy evaluation agent picking moves that maximize immediate positional score (Medium).
   - `MinimaxAgent`: Minimax search agent with Alpha-Beta pruning and heuristic state evaluation (Hard).
3. Connect the checkers engine and AI search agents to a Flask backend in `app.py`.
4. Build the responsive web frontend in `templates/index.html` allowing the user to play interactively against the AI.
5. Complete `report.md` with your student information, agent configuration, evaluation analysis, and technical discussion.
6. Deploy the completed web application to a live hosting service (e.g., Render) so that it is publicly accessible.
7. Record a 5–7 minute video presentation demonstrating human vs AI gameplay and explaining your implementation.

---

### 📋 Task 1: Myanmar Checkers Game Engine (`checkers.py`)
Implement the game engine in `checkers.py` according to traditional Myanmar Checkers rules:
- Board representation and state tracking for both players.
- Legal move generation, piece movement, and capturing mechanics.
- Move execution, state transitions, and move undo/backtracking.
- Win, loss, and draw condition evaluation.

---

### 📋 Task 2: AI Search Agents & Heuristic Evaluation (`agent.py`)
Implement three distinct AI strategies:
1. **Random Agent (`RandomAgent`):**
   - Uniformly samples from available legal moves.
2. **Heuristic Agent (`HeuristicAgent`):**
   - Evaluates immediate candidate moves using a board evaluation function to make greedy decisions.
3. **Minimax Agent (`MinimaxAgent`):**
   - Implements recursive Minimax search with Alpha-Beta pruning ($\alpha \ge \beta$ cutoffs).
   - Uses a heuristic evaluation function to score non-terminal board positions.
   - Tracks search statistics (e.g., evaluated nodes and candidate move scores).

---

### 📋 Task 3: Interactive Web Visualizer (`app.py` & `templates/index.html`)
Build an interactive web application that provides:
1. **Interactive Playable Board:** Allows a human user to play Myanmar Checkers against the AI on the web interface.
2. **Difficulty Selection:** Lets players select their opponent AI strategy (Easy, Medium, Hard).
3. **Game Visualizer & Status:** Displays game status, turn indicators, move feedback, and game over results.

---

### 📋 Task 4: Complete the Report (`report.md`)
Complete all required sections in [report.md](report.md):
- **Student Information:** Full Name and MMDT ID.
- **AI Agent Configuration:** Document primary algorithm, pruning technique, and evaluation heuristic strategy.
- **Complexity & Evaluation Function Analysis:** Board configuration, piece valuation, and heuristic components used.
- **Local Verification Checklist:** Mark verified algorithms, agents, and features with `[x]`.
- **Deployed and Presentation Information:** Deployment platform, live deployment URL, and video presentation link.
- **Discussion:** Detailed answers explaining Alpha-Beta pruning and comparing classical Adversarial Search with modern AI game architectures.

> [!WARNING]
> Do not modify the section headers, bold titles, or overall formatting of [report.md](report.md). Changes to the structure may cause the autograder tests to fail.
> Replace all bracketed placeholder text with your answers. Do not leave any placeholders in the final report.

---

### 📋 Task 5: Record a Video Presentation

Record a **5–7 minute video presentation** explaining your project implementation:
- **Game Engine & Rules:** Explain your board representation, move mechanics, captures, and victory conditions.
- **Heuristic Evaluation Function:** Explain the components of your evaluation function and how board advantage is assessed.
- **Minimax Search & Alpha-Beta Pruning:** Explain the minimax search algorithm and how Alpha-Beta pruning optimizes decision speed.
- **Demonstration:** Show human vs AI gameplay across different difficulty levels on your deployed web application.

#### Video Requirements
- You may use tools such as Zoom, Loom, or OBS Studio to record your presentation.
- Your face must be visible during the presentation. If you are not comfortable with this requirement, please discuss it with the instructor in advance.
- The recorded video must be in `.mp4` format and must not exceed **7 minutes**.
- Upload the video to a sharing platform such as YouTube, Google Drive, or Dropbox.
- Ensure the video link is publicly accessible to the instructor.
- Add the video link to Section 4 of `report.md`.

---

## Marking Scheme (70 marks Autograde + 30 marks Manual Grade = 100 marks Total)

### 1. Implementation & Required Files (40 marks) - Autograded
- **Required Files Check (40 marks):** `app.py`, `checkers.py`, `agent.py`, `templates/index.html`, `requirements.txt`, `report.md`, and `AI_declaration.png` present in project root.

### 2. Completion of report.md (30 marks) - Autograded
- **Student Information (5 marks):** Full Name and MMDT ID filled in.
- **AI Agent Configuration (5 marks):** Primary AI algorithm, pruning technique, and evaluation heuristic strategy documented.
- **Complexity & Evaluation Function Analysis (5 marks):** Board configuration, piece valuations, and heuristic features documented.
- **Local Verification Checklist (5 marks):** Checklist showing verified algorithms and features marked with `[x]`.
- **Deployment & Presentation Details (5 marks):** Provide valid live deployment platform, live URL, and video presentation link.
- **Discussion & Technical Analysis (5 marks):** Comprehensive answers explaining Alpha-Beta pruning and comparing classical Adversarial Search with modern AI systems.

### 3. Live URL Verification, Correctness & Video Presentation (30 marks)
**Note:** This section is manually graded.
- **Live Deployment (5 marks):** The submitted URL is publicly accessible and the application loads successfully.
- **Application Correctness & Gameplay (15 marks):** The web application correctly renders the Myanmar checkers board, enforces game rules, executes AI moves, and handles game end conditions.
- **Video Presentation (10 marks):** The 5–7 minute presentation clearly demonstrates human vs AI gameplay and effectively explains the game engine, Minimax search, and heuristic evaluation formulation.
