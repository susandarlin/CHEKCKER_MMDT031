## Project Overview: Myanmar Checkers AI Visualizer

In this project, you will design, implement, test, and deploy a full-stack interactive Game AI web application for **Myanmar Checkers**. The application allows users to play on a web-based board against an intelligent AI opponent powered by **Minimax with Alpha-Beta Pruning** and **Heuristic Evaluation**, alongside baseline agents.

The final outcome of this project is a fully functional web application deployed to a public, live URL.

---

### Learning Objectives

1. **Adversarial Search in Board Games:** Formulate zero-sum game trees for Myanmar Checkers.
2. **Search Optimization:** Implement Alpha-Beta pruning to optimize search depth without exceeding move time constraints.
3. **Heuristic State Evaluation:** Design evaluation functions to assess board positions and piece advantages.
4. **Game Engine Design:** Implement complete game mechanics according to traditional Myanmar Checkers rules.
5. **Interactive Full-Stack Web Development:** Build and deploy a responsive Flask web application allowing human-versus-AI gameplay.

---

## Submission Guidelines

To submit your project, please ensure you complete all required tasks and follow these instructions carefully.

### 1. Preparation Checklist
Before pushing your final submission, verify that:
* [ ] You have implemented the checkers game engine and rules in `checkers.py`.
* [ ] You have implemented all three AI search agents in `agent.py` (`RandomAgent`, `HeuristicAgent`, `MinimaxAgent` with Alpha-Beta pruning).
* [ ] You have built the Flask web backend in `app.py` and the interactive frontend in `templates/index.html`.
* [ ] You have completed the AI Student Declaration on [PETRA AI](https://www.petraai.org/student) and saved it as `AI_declaration.png` in the repository root.
* [ ] You have completed all sections in `report.md` (with your Name, MMDT ID, live deployment URL, video presentation link, and technical discussion). Do not alter the structure of `report.md`.
* [ ] You have deployed your application live (e.g., Render) and recorded a 5–7 minute video presentation (.mp4, face visible) demonstrating human vs AI gameplay, and uploaded it to YouTube, Google Drive, or Dropbox (with public view access).

### 2. How to Submit
Once everything is ready, commit and push your code to your GitHub repository's `main` or `master` branch:
```bash
git add .
git commit -m "Submit Project 6: Myanmar Checkers AI Visualizer"
git push origin main
```
The automated autograding system will automatically run tests upon pushing to the `main` or `master` branch.

---

## Checking Grades

You can check your project grades both locally and online via GitHub Actions.

### 1. Locally (Before Submitting)
You can run the autograding tests on your local machine:
1. Make sure you have installed all dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. Run `pytest` inside the project root:
   ```bash
   pytest tests/
   ```
3. A scorecard summarizing your earned marks will be outputted directly in the terminal under the section **"AUTOGRADING SCORECARD"**.

### 2. On GitHub (After Submitting)
Every push to the repository triggers the online autograder.
1. Go to the **Actions** tab of your GitHub repository.
2. Select the latest run (e.g., "Autograder Check" or your commit message).
3. Under the run details, view the **Autograding Scorecard** step summary, which details your score out of 70 marks.

---

## Grading Details & Passing Requirements

* **Autograded Score:** **70 marks** (40 marks for required project files check, 30 marks for `report.md` completion).
* **Manually Graded Score:** **30 marks** (Live deployment verification, gameplay correctness, and video presentation).
* **Total Coursework Marks:** **100 marks**.
* **Deadline:** **October 18, 2026, at 23:59:59**.
* **Late Submission Policy:** A penalty of **-10 marks per day** will be applied for late submissions.
* **Commitment Fee:** Any late, missing, or failed project (score < 70%) will carry a **30,000 MMK commitment fee**, calculated and collected at the end of the 10-week challenge.
