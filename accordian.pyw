# accordian.pyw

from model import Model
from view import View
import tkinter as tk
import os, sys

helpText = '''
OBJECTIVE

The objective is to place all cards in the 52-card deck in a single pile.
The game is played like standard accordian solitaire, but all the cards
are dealt up at the beginning of the game, whereas in accordian 
solitaire they're dealt one at a time.  Here you "know the future."

SETUP

The cards are dealt in four rows of 13, of 13, but the rows serve no function;
think of them as dealt in a single row of 52.  You may play a ple of cards on
top of the card to its left or the pile 3 to its left (skipping over two intermediate 
piles) if the top card of the card you move matches, in either suit or rank,
the top card of the pile you place it on.  For example, a pile with 5 of Hearts
on top can be moved on top of a pile whose top card is any Heart or any 5,
provided that pile is either one or three piles to the left of the 5 of Hearts pile.

The game ends when no more moves are possible.  If there is only one pile left,
you win.

'''

class Accordian:
    def __init__(self):
        deck = os.path.join(os.path.dirname(sys.argv[0]), 'cards')
        self.model = Model()
        self.view = View(self, deck, width=1145, height=650)
        self.makeHelp()
        self.view.start()      #  start the event loop

    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.resizable(False, True)
        top.title("Accordian")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(f, height=30, width=80, wrap=tk.WORD)
        text['font'] = ('helevetica', 14, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NS')
        f.rowconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(row=1, column=0)
        f.grid(sticky='NS')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT,helpText)

    def showHelp(self, event):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
        
if __name__ == "__main__":
    Accordian()
