import tkinter as tk
import random

# Settings
ROWS = 10
COLS = 10
MINES = 15
CELL_SIZE = 35

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        
        self.buttons = {}
        self.board = []
        self.revealed = set()
        self.flags = set()
        
        self.create_board()

    def create_board(self):
        # Create empty board
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # Place mines
        mines = random.sample(
            [(r, c) for r in range(ROWS) for c in range(COLS)],
            MINES
        )

        for r, c in mines:
            self.board[r][c] = -1

        # Calculate numbers
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == -1:
                    continue

                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS:
                            if self.board[nr][nc] == -1:
                                count += 1

                self.board[r][c] = count


        # Make buttons
        for r in range(ROWS):
            for c in range(COLS):
                btn = tk.Button(
                    self.root,
                    width=3,
                    height=1,
                    font=("Arial", 12, "bold")
                )

                btn.grid(row=r, column=c)

                btn.bind(
                    "<Button-1>",
                    lambda e, r=r, c=c: self.click(r, c)
                )

                btn.bind(
                    "<Button-3>",
                    lambda e, r=r, c=c: self.flag(r, c)
                )

                self.buttons[(r, c)] = btn


    def click(self, r, c):
        if (r, c) in self.flags:
            return

        if self.board[r][c] == -1:
            self.game_over()
            return

        self.reveal(r, c)

        if len(self.revealed) == ROWS * COLS - MINES:
            self.win()


    def reveal(self, r, c):
        if (r,c) in self.revealed:
            return

        self.revealed.add((r,c))

        value = self.board[r][c]

        btn = self.buttons[(r,c)]
        btn.config(
            text=str(value) if value else "",
            relief="sunken",
            state="disabled"
        )

        if value == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr = r+dr
                    nc = c+dc

                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        self.reveal(nr,nc)


    def flag(self, r, c):
        if (r,c) in self.revealed:
            return

        btn = self.buttons[(r,c)]

        if (r,c) in self.flags:
            self.flags.remove((r,c))
            btn.config(text="")
        else:
            self.flags.add((r,c))
            btn.config(text="🚩")


    def game_over(self):
        for (r,c), btn in self.buttons.items():
            if self.board[r][c] == -1:
                btn.config(text="💣")

        tk.messagebox.showinfo(
            "Game Over",
            "You hit a mine!"
        )

        self.root.destroy()


    def win(self):
        tk.messagebox.showinfo(
            "You Win!",
            "All mines cleared!"
        )
        self.root.destroy()



root = tk.Tk()

import tkinter.messagebox

game = Minesweeper(root)

root.mainloop()