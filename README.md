# Mambo Puzzle Solver

Mambo Puzzle Solver is a desktop application, built with Pygame, that lets a user design a puzzle grid by hand and then hands it to a solver. The solver models the grid as a Constraint Satisfaction Problem (CSP) and resolves it through pure logical deduction, with no guessing or backtracking involved.

The puzzle itself is traditionally known as **Takuzu** or **Binairo**, and is marketed as **Tango** on LinkedIn. I first encountered it inside [Almanac](https://play.google.com/store/apps/details?id=com.voodoo.almanac&hl=en), where it is called **Mambo**, and that is the name this project has kept.

## Table of Contents

- [Game Rules](#game-rules)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [The CSP Solver](#the-csp-solver)
- [Graphics and Interface](#graphics-and-interface)
- [Known Limitations](#known-limitations)

## Game Rules

The player fills a square grid with two symbols, referred to here as a cross and a circle, subject to the following rules:

- **No Three in a Row:** No symbol may appear three times consecutively in a row or column.
- **Balance:** Each row and each column must contain an equal number of crosses and circles. On an 8x8 board, this means exactly four of each per line.
- **Connector Clues:** Certain adjacent cell pairs are linked by a marker placed between them. An equals marker requires both cells to hold the same symbol. A cross marker requires them to hold opposite symbols.

The solver's task is to take a partially filled grid, respect any symbols and connectors already placed, and determine the rest.

## Tech Stack

- **Language:** Python 3
- **Library:** [Pygame](https://www.pygame.org/) for windowing, rendering, and input handling
- **Standard library:** `enum` for screen state management

No external assets, image files, or third-party solver libraries are used. All shapes are drawn programmatically, and the CSP logic is implemented from scratch.

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip

### Installation

```bash
git clone https://github.com/abdul-haseeb-dot/Mambo-Puzzle-Solver
cd Mambo-Puzzle-Solver
pip install pygame
```

### Running the application

```bash
python main.py
```

## Usage

1. Launch the application and select a grid size, either 6x6 or 8x8, from the main menu.
2. In the design screen, click on a tile to cycle it through empty, cross, and circle. Click on a connector marker between two tiles to cycle it through none, equals, and cross.
3. Click **Solve** to send the current grid to the CSP solver.
4. The result screen displays either the completed grid or a message explaining why the puzzle could not be solved.
5. Click **Next** to return to the main menu and start over.

## Project Structure

```
mambo/
├── main.py         # Game loop, screen state management, UI
├── tile.py         # Tile class
├── button.py       # Button class
├── connector.py    # Connector class
├── solver.py       # CSPSolver class and solve_mambo() function
└── .gitignore
```

The visual components are self-contained in `tile.py`, `button.py`, and `connector.py`. `main.py` coordinates these into a state machine. `solver.py` has no dependency on Pygame; it reads and writes plain integer `state` attributes on the tile and connector objects it is given.

## The Constraint Satisfaction Problem Solver

### Framing the puzzle as a CSP

A Constraint Satisfaction Problem is defined by a set of variables, a domain of possible values for each variable, and a set of constraints relating those variables. The mapping from Mambo onto this structure is as follows:

**Variables:** Every cell in the grid is a variable, identified by its `(row, col)` coordinate.

**Domains:** Each variable's domain begins as `{1, 2}`, where `1` represents a cross and `2` represents a circle. If a symbol has already been placed on a tile during the design phase, that variable's domain is immediately collapsed to a singleton, `{1}` or `{2}`.

**Constraints:** Three categories of constraints govern the puzzle:

1. The no-three-in-a-row rule, checked across every sliding window of three cells in each row and column.
2. The balance rule, which limits how many times a symbol can appear in a row or column to exactly half the grid size.
3. The connector rule, which links any two adjacent cells that carry a marker, enforcing equality or inequality according to the connector's state.

This logic is implemented in the `CSPSolver` class in `solver.py`, with `self.domains` representing the current state of the problem as it is progressively narrowed.

### Constraint propagation over backtracking

Many CSP solvers rely on backtracking search: select a variable, assign a tentative value, recurse, and unwind on contradiction. This approach is complete, in that it will find a solution if one exists, but it depends on trial and error.

This solver takes a different approach. `CSPSolver.solve()` contains no recursion and makes no tentative assignments. It narrows domains exclusively through logical inference, applying a fixed set of deduction rules repeatedly until no further change occurs. This is closer to arc consistency propagation than to a search procedure, and it mirrors how an experienced player would reason through the puzzle: by deducing each move from the current board state rather than guessing and revising.

The tradeoff is that constraint propagation alone is not guaranteed to be complete. There exist solvable grids where every deduction rule below reaches a standstill while some cells remain ambiguous, and resolving them would require a speculative assignment followed by verification. This solver does not attempt that step. If propagation cannot reduce every domain to a single value, the puzzle is reported as unsolvable, even in cases where a solution could in principle be found through trial and error. This behavior is intentional: every conclusion the solver reaches can be traced back to an explicit rule.

### Initial validity check

Before propagation begins, `is_valid_grid()` inspects the grid exactly as designed by the user. It checks for existing three-in-a-row violations among locked cells, compares the count of crosses and circles already placed in each row and column against the half-size limit, and evaluates any connector whose two endpoints are already fixed. If any check fails, the solver halts immediately and returns a specific, descriptive reason, which is also what populates the failure message on the result screen.

### Propagation rules

Once the grid passes the validity check, `solve()` repeatedly runs three propagation functions until a full pass produces no change (a fixpoint). Each function returns a boolean indicating whether it altered any domain, which the main loop uses to determine when to stop.

**`propagate_connectors()`** processes every marked pair of tiles. For an equals connector, it intersects the two domains and narrows both to the shared set, since a valid assignment for one must also be valid for the other. For a cross connector, once either endpoint collapses to a single value, the other is immediately forced to the opposite value. This function also performs a limited lookahead: if an equals-linked pair sits adjacent to a third, already-fixed tile, and completing the pair with that tile's symbol would create a three-in-a-row, both linked tiles are forced to the opposite symbol.

**`propagate_balance()`** evaluates each row and column as a unit. Once a line reaches its quota for one symbol, every remaining undecided cell in that line is forced to the other symbol. It additionally performs a one-step lookahead: when a line sits exactly one cell short of its quota, the function checks, for each undecided cell, whether assigning it the symbol that would exceed the quota's complement could still avoid a three-in-a-row given the rest of the line. If it could not, that cell is safely constrained away from that symbol.

**`propagate_no_three_in_a_row()`** re-examines every sliding window of three cells, this time from the adjacency constraint directly. If two cells within a window are already fixed to the same symbol, the third is forced to the opposite one, since allowing it to match would create a forbidden run.

These three functions interact: a deduction made by the connector rule can create an opening for the balance rule, which can in turn trigger the row rule. This interaction is precisely why `solve()` continues looping until an entire pass makes no further change.

### Reaching a verdict

Once the fixpoint is reached, the solver performs a final pass over every variable. If any domain still holds two possible values, the grid is reported as unsolvable and `solve()` returns `None`. If every domain has collapsed to a single value, that assignment constitutes the solution, and `solve_mambo()` writes the resolved states back onto the `Tile` objects so the interface can render the completed grid.

<img width="701" height="697" alt="image" src="https://github.com/user-attachments/assets/f2560e6f-3d64-4fb8-bde7-b58e7fd31649" />

## Graphics and Interface

All visual elements are rendered directly through Pygame's drawing primitives. No sprite sheets or external image assets are used; every shape on screen, including the cross, the circle, and the connector symbols, is drawn programmatically with lines, circles, and rounded rectangles.

### Screen flow

`main.py` implements a state machine built on Python's `Enum`, cycling through three states: `MENU`, `DESIGN`, and `SOLVE`. The main menu allows the user to select a 6x6 or an 8x8 board. Selecting a size calls `create_grid()`, which constructs the corresponding `Tile` and `Connector` objects and transitions the application into the design state. From there, selecting Solve passes the grid to `solve_mambo()` and transitions into the solve state, which displays either the completed board or the failure explanation, with a Next button returning to the main menu.

<img width="700" height="697" alt="image-1" src="https://github.com/user-attachments/assets/74b9b9ab-9aa8-47cd-baaa-201cba6f1d80" />

### Grid layout

The layout logic in `create_grid()` is computed rather than fixed per grid size. It reserves a constant 440 pixel band for the grid regardless of dimensions, subtracts the spacing between tiles, and divides the remainder evenly to determine individual tile size. The grid is then centered horizontally relative to the window, and each connector is positioned at the exact midpoint between the two tiles it links, whether the link is horizontal or vertical. As a result, both the 6x6 and 8x8 boards occupy a comparable visual footprint, differing mainly in individual tile size.

### Tiles

Each `Tile` cycles through three states on click: empty, cross, and circle, each rendered with a distinct fill color. Hovering changes the border to a lighter shade to provide a clear visual cue for cursor position. The cross is drawn as two diagonal lines, and the circle as a ringed outline, both inset from the tile edge by a padding value calculated as a percentage of tile width, allowing the symbols to scale consistently across both grid sizes.

<img width="700" height="698" alt="image-3" src="https://github.com/user-attachments/assets/8a3946cf-4ec7-4660-9596-09419273ce14" />

### Connectors

The `Connector` class is positioned precisely between two tiles while remaining large enough to interact with comfortably. Its radius is derived from the tile size but clamped between 6 and 16 pixels, keeping it proportionate across grid sizes. Clicking a connector cycles it through none, equals, and cross, following the same three-state pattern as the tiles. The equals symbol is drawn as two short parallel lines oriented perpendicular to the connector's own direction, horizontal for a vertical connector and vertical for a horizontal one, so its orientation reads clearly. The cross symbol consists of two diagonal strokes. Hovering brightens the border and adds a translucent halo behind the marker, rendered on a separate `SRCALPHA` surface so the highlight does not interfere with the symbol drawn on top of it.

### Buttons

The `Button` class draws a rounded rectangle with a border color derived by darkening its fill color by a fixed amount, producing a consistent outline for every button without requiring a separately chosen border color. A semi-transparent white overlay is applied on hover for visual feedback, and text is centered within the rectangle using the font's own bounding rect, keeping labels aligned regardless of their length.

<img width="699" height="698" alt="image-4" src="https://github.com/user-attachments/assets/6af68ec7-7320-4b1a-a159-47f8bf404de6" />

### Color palette

Taking inspiration from [Almanac](https://play.google.com/store/apps/details?id=com.voodoo.almanac&hl=en), the interface uses a dark theme throughout: a near-black blue background, off-white text, and a small set of accent colors, amber for crosses, lavender for circles, green for the solve action, and blue for the next action, applied consistently across buttons, tiles, and state indicators. Failure messages are rendered in a muted red, distinguishing them from the rest of the interface without being visually jarring.

<img width="701" height="697" alt="image-5" src="https://github.com/user-attachments/assets/7176cc1b-e51e-49c1-87f7-ecaa78f0644d" />

<img width="699" height="696" alt="image-6" src="https://github.com/user-attachments/assets/92288fb1-5150-4098-904f-de55decd9b75" />

## Known Limitations

- The solver relies entirely on constraint propagation and does not implement backtracking search. As a result, it may report a puzzle as unsolvable even when a solution exists but requires a speculative assignment beyond the scope of the implemented deduction rules.
- Grid size is currently limited to 6x6 and 8x8; other dimensions would require adjustments to the layout constants in `create_grid()`.
