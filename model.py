# model.py Model for Accordian solitaire

import random, itertools

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# RANKNAMES is a list that maps a rank to a string.  It contains a
# dummy element at index 0 so it can be indexed directly with the card
# value.

SUITNAMES = ('club', 'diamond', 'heart', 'spade')
RANKNAMES = ["", "Ace"] + list(map(str, range(2, 11))) + ["Jack", "Queen", "King"]

class Card:
    '''
    A card is identified by its rank and suit.
    '''
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.code = 13*SUITNAMES.index(suit)+rank-1
        
    def matches(self, other):
        return self.suit == other.suit or self.rank == other.rank

    def __repr__(self):
        return '%s %s'%(self.suit, RANKNAMES[self.rank])

    def __str__(self):
        return __repr__(self)

class Model:
    '''
    The cards are all in self.deck, and are copied into the piles. 

      '''
    def __init__(self):
        random.seed()
        self.deck = []
        self.selection = None
        self.createCards()
        self.piles = []
        self.undoStack = []
        self.redoStack = []
        self.deal()

    def createCards(self):
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            self.deck.append(Card(rank, suit))
            
    def deal(self):
        '''
        Deal the cards into the initial layout
        '''
        random.shuffle(self.deck)
        self.piles = self.deck[:]
        self.selection   = None
        self.undoStack = []
        self.redoStack = []

    def grab(self, code):
        '''
        Initiate a move.  Find the pile containing the card.
        Return pile index on success or None on failure.
        '''
        codes = [card.code for card in self.piles]
        pile = codes.index(code)
        if pile == -1:
            return None
        self.selection = pile
        return pile

    def abortMove(self):
        self.selection = None

    def moving(self):
        return self.selection != None 
    
    def playable(self):
        # Return list of indices of playable cards as tuple.
        # First element represents cards that can be moved 1 only.
        # Second element represents cards that can be moved 3 only.
        # Third element represents cards that can be moved both 1 and 3.
        
        move1 = []
        move3 = []
        move13 = []
        for idx, card in enumerate(self.piles):
            one = False
            three = False
            if idx >= 1 and card.matches(self.piles[idx-1]):
                one = True
            if idx >= 3 and card.matches(self.piles[idx-3]):
                three = True
            if one and three:
                move13.append(idx)
            elif one:
                move1.append(idx)
            elif three:
                move3.append(idx)
        return move1, move3, move13
    
    def canDrop(self, pile):
        '''
        Can the moving cards be dropped on pile?  
        '''
        if not self.selection:
            return False
        source = self.selection
        if pile not in (source-1, source-3):
            return False
        target = self.piles[pile]
        return target.matches(self.piles[source])
               
    def completeMove(self, dest):
        '''
        Compete a legal move 
        '''
        piles = self.piles
        self.undoStack.append(piles[:])
        self.redoStack = []
        card = piles.pop(self.selection)
        piles[dest] = card
        self.selection = None
                
    def win(self):
        return len(self.piles) == 1
                   
    def gameOver(self):
        if self.win():
            return True
        if self.playable() == ([],[],[]):
            return True
        
    def canUndo(self):
        return self.undoStack != []
    
    def canRedo(self):
        return self.redoStack != []
    
    def undo(self):
        self.redoStack.append(self.piles)
        self.piles = self.undoStack.pop(-1)
        
    def redo(self):
        self.undoStack.append(self.piles)
        self.piles = self.redoStack.pop(-1)
        
        