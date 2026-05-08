import tkinter as tk
from tkinter import *
from tkinter import scrolledtext
from tkinter import PhotoImage

from matplotlib.pyplot import pie
from sympy import false
class ChessUI:
    def __init__(self,root):
        root.title("Blind Chess");
        root.geometry("600x800");
        # chess_board.set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR");
        # Not sure how to map the chess pieces yet.
        body = tk.Frame(root);
        body.grid(column=0, row=0, sticky=(N,S,E,W));

        # Chess Board Portion of the screen.
        self.chess_board = tk.Frame(body, relief="sunken");
        self.chess_board.grid(column=0,columnspan=2, row=0, sticky=(N,S,E,W));
        for row in range(8):
            for col in range(8):
                space = tk.Label(self.chess_board, wraplength=40, height=5, width=6, text="", borderwidth=1, relief="solid");
                space.grid(column=col, row=row, sticky=(N,S,E,W));
        self.screen = tk.Label(self.chess_board, relief="solid",background="black");

        # Console Frame Portion of the screen.
        console_frame = tk.Frame(body, relief="solid");
        console_frame.grid(column=0, row=1, sticky=(N,S,E,W));

        console_label = tk.Label(console_frame, text= "Console")
        console_label.grid(column=0, row=0,sticky=(N,W));

        self.console = scrolledtext.ScrolledText(console_frame, height=10, width=40);
        self.console.grid(column=0, row=1, sticky=(N,S,E,W));

        # Button Portion of the screen
        button_panel = tk.Frame(body, relief="solid");
        button_panel.grid(column=1, row=1, sticky=(N,S,E,W));

        button_panel_label = tk.Label(button_panel, text= "Push To Talk")
        button_panel_label.grid(column=0, row=0, sticky=(N,W));

        button = tk.Button(button_panel,width=4,height=4,command=lambda: self.update_console("User", "PC"))
        button.place(anchor='center', relx=.5, rely=.5);


    # Method to update Console.
    def update_console(self,user_input,game_response):
        self.console.config(state=NORMAL);
        self.console.insert(END, f">: {user_input}\n"); # Plug in here.
        self.console.insert(END, f"$: {game_response}\n"); #And here.
        self.console.config(state=DISABLED);
        self.console.see(END); # Keep last line visible

    #update chessboard labels.
    def update_chessboard(self,arg):
        for row in range(8):
            for col in range(8):
                place = self.chess_board.grid_slaves(column=col, row=row)
                place[0].config(text=arg[row][col]);
    # Methods to hide and reveal the chess board.
    def hide_board(self):
        self.screen.grid(rowspan=8,columnspan=8, row=0,column=0, sticky=(N,S,E,W));
    def reveal_board(self):
        self.screen.grid_remove();
 
#root=tk.Tk()
#app = ChessUI(root)
#root.mainloop()