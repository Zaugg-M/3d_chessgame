# Overview

For this project I wanted to learn more about game development in Python. I did this by creating a "3D chess game". The goal was to build a user‑interactive 3D board that not only renders three stacked layers but also supports full move logic, highlighting across levels, and both human‑vs‑human and human‑vs‑AI modes. It has helped me learn more about Pygame, object‑oriented design, and simple AI implementation.

The game displays three 8×8 chessboards offset and scaled to simulate depth. I should say that this isn't visually a '3D' game. The boards are shown on a 2D space with the ability to switch between layers. Players select pieces with the mouse, see legal move highlights across levels, and move pieces by clicking destination cells. Captured pieces appear in side panels, and the game ends when a King is taken.

I wanted to explore the challenges of rendering and interacting with a 3D‑like environment and implement complete move logic for all chess pieces in three dimensions, and add a basic random‑move AI for single player.

[Software Demo Video]([http://youtube.link.goes.here](https://youtu.be/NjoI87W9WV4?si=L-p06F4AJIIYodeM)http://youtube.link.goes.here)

# Development Environment

* **Operating System:** Windows/ Linux
* **Code Editor:** Visual Studio Code
* **Programming Language:** Python 3.8+
* **Primary Library:** Pygame for windowing, rendering, and input handling
* **Version Control:** Git (GitHub repository)

# Useful Websites

* [Pygame Documentation](https://www.pygame.org/docs/) — Reference for rendering and event APIs.
* [Python Official Docs](https://docs.python.org/3/) — Language features and standard library.
* [Stack Overflow](https://stackoverflow.com/) — Troubleshooting Pygame and Python bugs.
* [Chess Programming Wiki](https://www.chessprogramming.org/) — Algorithms for move generation and board representation.

# Future Work

* Implement full check and checkmate detection logic.
* Enhance AI using minimax with alpha‑beta pruning for more strategic play.
* Add sound effects and background music for better immersion.
* Improve UI with animations for piece movement and level transitions.
* Support save/load without external files and persistent game states.
