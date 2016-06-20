# view.py
'''
The visual interface for open Accordian solitaire.
The view knows about the model, but not vice versa
The canvas widget is used for both view and controller.
'''
import sys, os, itertools
import tkinter as tk
import tkinter.messagebox as tkmb
from model import SUITNAMES, RANKNAMES, ALLRANKS, Card

# Constants determining the size and layout of cards piles.
# Adjacent cards are separated by MARGIN pixels

CARDWIDTH = 75
CARDHEIGHT = 112
MARGIN = 10

BACKGROUND = '#070'
OUTLINE = 'orange'        # outline color of piles
CELEBRATE = 'yellow'     # Color of "you won" message
BUTTON = 'Forest Green'

MOVE1 = 'white'             # indicator colors for playable cards
MOVE3 = 'white'
MOVE13 ='yellow'

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

STATUS_FONT = ('Helvetica', '14', 'normal')

imageDict = {}   # hang on to images, or they may disappear!

class View: 
    '''
    Cards are represented as canvas image items,  displaying either the face
    or the back as appropriate.  Each card has the tag "card".  This is 
    crucial, since only canvas items tagged "card" will respond to mouse
    clicks.
    '''
    def __init__(self, parent, deck, **kwargs):
        # kwargs passed to Canvas
        # deck is directory with card images
        self.parent = parent          # parent is the Accordian application
        self.model =  parent.model
        self.root = root = tk.Tk()
        self.deck = tk.StringVar(value=deck)
        root.resizable(height=False, width=False)
        width = kwargs['width']
        height = kwargs['height']
        self.root.wm_geometry('%dx%d-10+10'%(width,height))
        root.title("Open Accordian Solitaire")                       
        canvas = self.canvas = tk.Canvas(root, bg=BACKGROUND, 
                                         cursor=DEFAULT_CURSOR, **kwargs)
        canvas.pack()
        self.loadImages()
        self.createCards()      
        self.pileCoords = []
        self.makePiles()
        self.makeMessages(width, height)
        canvas.tag_bind("card", '<ButtonPress-1>', self.onClick)
        canvas.bind('<B1-Motion>', self.drag)
        canvas.bind('<ButtonRelease-1>', self.onDrop)
        self.makeButtons()
        self.hideMessages()
        self.show()
        
    def makeButton(self, x, y, text, tag, callback):
        canvas = self.canvas
        canvas.create_oval(x,y,x+6*MARGIN, y+3*MARGIN,
                fill = BUTTON, outline=BUTTON,tag=tag)
        canvas.create_text(x+3*MARGIN, y + 3*MARGIN/2, text = text, 
                                   fill = CELEBRATE, tag=tag, anchor=tk.CENTER)        
        canvas.tag_bind(tag, '<ButtonRelease-1>', callback)
        
    def makeButtons(self):
        make = self.makeButton
        x = MARGIN
        y = MARGIN
        make(x, y, 'New Deal', 'newDeal', self.newDeal)                
        x= 9*MARGIN
        make(x, y, 'Undo', 'undo', self.undo)
        x = 17*MARGIN
        make(x, y, 'Redo', 'redo', self.redo)
        x = 25*MARGIN
        make(x,y, 'Help', 'help',  self.parent.showHelp)
                 
    def start(self):
        self.root.mainloop()
                        
    def newDeal(self, event):
        if not self.model.gameOver():
            answer = tkmb.askokcancel(title='Abandon Game?', 
                                              message= 'Game is not over.  You still have moves.',
                                              icon = tkmb.QUESTION, 
                                              default = tkmb.CANCEL )
            if not answer: return   # user chose 'Cancel'
        canvas = self.canvas
        self.hideMessages()
        self.model.deal()
        self.show()
        
    def makeMessages(self, width, height):
        canvas = self.canvas
        canvas.create_text(width//2, height//2, text = "YOU WIN",
                           fill = BACKGROUND, font=("Helvetica", "64", "bold"), 
                           tag = 'winText', anchor=tk.CENTER)      
        canvas.create_text(width//2 , height//4,
                           text = 'No More Moves.  Game Over.',
                           fill = BACKGROUND, font = ('Helvetica', '32', 'bold'),
                           tag = 'gameOver', anchor = tk.CENTER)        
        
    def hideMessages(self):
        canvas =self.canvas
        for tag in ('winText','gameOver'):
            canvas.itemconfigure(tag, fill = BACKGROUND)
            canvas.tag_lower(tag, 'all')
    
    def showMessage(self, tag):
        canvas = self.canvas
        canvas.itemconfigure(tag, fill=CELEBRATE)
        canvas.tag_raise(tag, 'all')        
        
    def loadImages(self):
        PhotoImage = tk.PhotoImage
        deck = self.deck.get()
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            face = PhotoImage(file = os.path.join(deck, suit+RANKNAMES[rank]+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas   
        for card in model.deck:
            foto = imageDict[card.rank, card.suit]
            c = canvas.create_image(-200, -200, image = foto, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%d'%card.code, c)
            
    def makePiles(self):
        canvas = self.canvas
        coords = self.pileCoords           # NW corners of the  piles
        y = 7* MARGIN
        idx = 0
        for row in range(0,52,13):
            x = MARGIN
            for column in range(13):
                c = canvas.create_rectangle(x,y,x+CARDWIDTH+2,y+CARDHEIGHT+2,
                                    outline=BACKGROUND, tag='pile')
                canvas.addtag_withtag('rect%d'%idx, c)
                coords.append((x+1,y+1))
                x += CARDWIDTH+2+MARGIN
                idx += 1
            y += CARDHEIGHT+2+MARGIN
            
    def showPiles(self):
        canvas = self.canvas
        model = self.model
        coords = self.pileCoords
        for card in model.deck:
            tag = 'code%d'%card.code
            canvas.coords(tag, -200, -200)
        for idx, card in enumerate(model.piles):
            tag = 'code%d'%card.code
            x, y = coords[idx]
            canvas.coords(tag, x+1, y)
            canvas.tag_raise(tag)
        move1, move3, move13 = model.playable()
        canvas.itemconfigure('pile', fill=BACKGROUND)
        for idx in move1:
            canvas.itemconfigure('rect%d'%idx, outline=MOVE1)
        for idx in move3:
            canvas.itemconfigure('rect%d'%idx, outline=MOVE3)
        for idx in move13:
            canvas.itemconfigure('rect%d'%idx, outline=MOVE13)        
                    
    def show(self):
        model = self.model
        canvas = self.canvas
        self.showPiles()
        if model.win():
            self.showMessage('winText')
        elif model.gameOver():
            self.showMessage('gameOver')
        if model.canUndo():
            self.enableUndo()
        else:
            self.disableUndo()
        if model.canRedo():
            self.enableRedo()
        else:
            self.disableRedo()
        
    def grab(self, tag, pile, mouseX, mouseY):
        '''
        Grab the selected card.
        '''
        canvas = self.canvas
        self.mouseX, self.mouseY = mouseX, mouseY
        canvas.tag_raise(tag)
        canvas.addtag_withtag("floating", tag)
        canvas.configure(cursor=SELECT_CURSOR)
        west = self.pileCoords[pile][0]
        dx = 5 if mouseX - west > 10 else -5
        canvas.move('floating', dx, 5)

    def drag(self, event):
        try:
            x, y = event.x, event.y
            dx, dy = x - self.mouseX, y - self.mouseY
            self.mouseX, self.mouseY = x, y
            self.canvas.move('floating', dx, dy)
        except AttributeError:
            pass

    def onClick(self, event):
        '''
        Respond to click on a pile.  
        '''
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = int(tag[4:])             # code of the card clicked
        pile = model.grab(code)
        if pile:
            self.grab('code%d'%code, pile, event.x, event.y)  

    def onDrop(self, event):
        '''
        Drop the selected pile.  In order to recognize the destination pile,
        the card being dragged must overlap the pile, and it must be
        a legal drop target.
        '''
        model = self.model
        if not model.moving():
            return
        canvas = self.canvas
        canvas.configure(cursor=DEFAULT_CURSOR)

        try:    
            west, north, east, south = canvas.bbox('floating')
        except TypeError:
            self.abortMove()
            return        
        for pile, (left, top) in enumerate(self.pileCoords[:len(model.piles)]):
            right = left +  CARDWIDTH - 1
            bottom = top + CARDHEIGHT - 1               
            if not (left <= west <= right or left <= east <= right ):
                continue
            if not (top <= north <= bottom or top <= south <= bottom):
                continue
            if model.canDrop(pile):
                model.completeMove(pile)
                self.completeMove()
                break    
        else:           # loop else
            self.abortMove()
        self.show()

    def abortMove(self):
        self.model.abortMove()
        self.show()
        self.canvas.dtag('floating', 'floating')
        
    def completeMove(self):
        self.show()
        self.canvas.dtag('floating', 'floating')
        
    def undo(self, event):
        self.model.undo()
        self.show()
        
    def redo(self, event):
        self.model.redo()
        self.show()
        
    def disableRedo(self):
        self.canvas.itemconfigure('redo', state=tk.HIDDEN)

    def disableUndo(self):
        self.canvas.itemconfigure('undo', state=tk.HIDDEN)

    def enableRedo(self):
        self.canvas.itemconfigure('redo', state=tk.NORMAL)

    def enableUndo(self):
        self.canvas.itemconfigure('undo', state=tk.NORMAL)    
        