"""Model file. This file contains all of the functions that work with board management, and AI management"""

import pickle as pk
import random as rd
from copy import deepcopy
import controller
import math as ma

class Board:
    """Board class"""
    def __init__(self):
        """Constructor"""
        # 0. Empty Space
        # 1. P1 Piece
        # 2. P2 Piece
        self.grid = [[0 for _ in range(7)] for _ in range(6)]
        self.currentplayer = 1
        self.previouspos = 0
        # For AI purposes, shows what y pos the previous token was placed in
        self.gameType = 0
        # AI purposes
    
    def addPiece(self, pos: int, toRemember: bool):
        """Drops a piece in the selected column to the lowest available free space"""
        dropped = False
        ypos = 5
        while not dropped:
            if self.grid[ypos][pos] == 0:
                self.grid[ypos][pos] = self.currentplayer
                dropped = True
            else:
                ypos -= 1
            if ypos < 0:
                raise Exception("Column full; no error checking for full columns")
        if self.currentplayer == 1:
            self.currentplayer = 2
        else:
            self.currentplayer = 1
        self.previouspos = pos
        if toRemember:
            for x in range(len(AILIST)):
                AILIST[x].rememberCurrentBoard(self.clone())
    
    def winCheck(self):
        """Checks the board for any four adjacent identical pieces"""
        # Returns:
        # 0. None
        # 1. Player 1
        # 2. Player 2
        # 3. Draw
        draw = True
        for checkdraw in range(7):
            if not self.colFullCheck(checkdraw):
                draw = False
        if draw:
            return 3
        for y in range(6):
            for x in range(7):
                if self.grid[y][x] != 0:
                    # Horz victory
                    try:
                        if self.grid[y][x+1] == self.grid[y][x] and self.grid[y][x+2] == self.grid[y][x]\
                        and self.grid[y][x+3] == self.grid[y][x]:
                            return self.grid[y][x]
                    except:
                        pass
                    # Vert victory
                    try:
                        if self.grid[y+1][x] == self.grid[y][x] and self.grid[y+2][x] == self.grid[y][x]\
                        and self.grid[y+3][x] == self.grid[y][x]:
                            return self.grid[y][x]
                    except:
                        pass
                    # \ Diag victory
                    try:
                        if self.grid[y+1][x+1] == self.grid[y][x] and self.grid[y+2][x+2] == self.grid[y][x]\
                        and self.grid[y+3][x+3] == self.grid[y][x]:
                            return self.grid[y][x]
                    except:
                        pass
                    # / Diag victory
                    try:
                        if self.grid[nonNegative(y-1)][x+1] == self.grid[y][x]\
                        and self.grid[nonNegative(y-2)][x+2] == self.grid[y][x]\
                        and self.grid[nonNegative(y-3)][x+3] == self.grid[y][x]:
                            return self.grid[y][x]
                    except:
                        pass
        return 0

    def colFullCheck(self, pos):
        """Checks if any column is full. Returns false if not full, returns true if full."""
        if self.grid[0][pos] == 0:
            return False
        else:
            return True

    def clone(self):
        """Clones the current state of the game."""
        new = Board()
        new.grid = deepcopy(self.grid)
        new.currentplayer = deepcopy(self.currentplayer)
        new.previouspos = deepcopy(self.previouspos)
        return new

    def __repr__(self):
        """repr function"""
        ret = ''
        for y in range(6):
            for x in range(7):
                ret += str(self.grid[y][x]) + ' '
            ret += '\n'
        ret += "WIN: " + str(self.winCheck())
        return ret

# noinspection PyTypeChecker
class Node:
    """Node class which will be used in the brain"""
    def __init__(self, parent=None, state: Board=Board()):
        """Constructor"""
        # where state must be the Board class and referenced when theBoard clones itself
        self.state = state
        self.children = [None for _ in range(7)]
        self.parent = parent
        self.visits = 0
        self.wins = 0
        self.payoff = 10 + rd.uniform(0, 0.15)

    def backprop(self, win=False):
        """Updates node and parents with new information"""
        self.visits += 1
        if win:
            self.wins += 1
        # This backpropagation is ignored if the node has no parent. Used for the root node
        if self.parent is not None:
            self.parent.backprop(win)
        self.updatePayoff()

    def updatePayoff(self):
        """Updates the payoff attribute of a single node"""
        if self.visits == 0:
            self.payoff = 10
        elif self.parent is not None:
            self.payoff = (self.wins / self.visits) + (ma.sqrt(2) * ma.sqrt(ma.log(self.parent.visits)/self.visits))
        if self.state.winCheck() == 3:
            self.payoff = 0

    def expand(self, pos: int, toRemember: bool):
        """Adds a child node"""
        temp = self.state.clone()
        temp.addPiece(pos, toRemember)
        self.children[pos] = Node(parent=self, state=deepcopy(temp))

    def getChild(self, pos):
        """Returns the child node found in a specific position"""
        try:
            return self.children[pos]
        except:
            return None

    def __repr__(self):
        return "V: " + str(self.visits) + " W: " + str(self.wins) + " P: " + str(self.payoff)

# noinspection PyTypeChecker
class Brain:
    """AI Brain class"""
    def __init__(self, name):
        """Constructor"""
        self.root = Node()
        self.playinstance = [] # for recording the current play instance history to aid the tree search.
                               # each input is a dropped token position.
        self.name = name

    def selection(self, anynode: Node, route):
        """Selects a route to take within the tree to reach a leaf"""
        # Going through a known route
        # checking for wins
        if anynode.state.winCheck() == 1:
            if controller.getAIPlayerPos(self.name) == 1:
                self.backpropagation(anynode, True)
            else:
                self.backpropagation(anynode, False)
        elif anynode.state.winCheck() == 2:
            if controller.getAIPlayerPos(self.name) == 2:
                self.backpropagation(anynode, True)
            else:
                self.backpropagation(anynode, False)
        elif anynode.state.winCheck() == 3:
            self.backpropagation(anynode, False)
        else:
            if len(route) != 0:
                if anynode.getChild(head(route)) is not None:
                    self.selection(anynode.getChild(head(route)), tail(route))
                else:
                    anynode.expand(head(route), False)
                    self.selection(anynode.getChild(head(route)), tail(route))
            # Going through an unknown route until a None is hit
            else:
                childsuccessrates = [None for _ in range(7)]
                for x in range(7):
                    try:
                        if anynode.state.colFullCheck(x):
                            childsuccessrates[x] = -1
                        else: # where t is an instance of a child
                            t = anynode.getChild(x)
                            t.updatePayoff()
                            childsuccessrates[x] = t.payoff
                    except:
                        childsuccessrates[x] = 10 + rd.uniform(0, 0.15)
                complete = False
                while not complete:
                    goto = highestPosInArray(childsuccessrates)
                    if anynode.getChild(goto) is not None:
                        if goto == -1:
                            raise Exception
                        self.selection(anynode.getChild(goto), [])
                        complete = True
                    else:
                        self.expansion(anynode, goto)
                        complete = True

    def expansion(self, currentnode: Node, pos: int):
        """Add a new child node for either a new learned state or a potential state and leads to simulation"""
        currentnode.expand(pos, False)
        self.simulation(currentnode.getChild(pos))

    def simulation(self, anynode: Node):
        """Runs simulations of a hypothetical occurance and backpropagates results"""
        playerID = controller.getAIPlayerPos(self.name)
        nodestateclone = anynode.state.clone()
        complete = False
        # Random playout
        if playerID is not None:
            while not complete:
                if nodestateclone.winCheck() != 0:
                    if nodestateclone.winCheck() == playerID:
                        # Win
                        complete = True
                        self.backpropagation(anynode, True)
                    else:
                        # Lose
                        complete = True
                        self.backpropagation(anynode, False)
                else:
                    try:
                        nodestateclone.addPiece(rd.randint(0, 6), False)
                    except:
                        pass
        else:
            raise Exception("playerID is None")

    @staticmethod
    def backpropagation(anynode: Node, victory):
        """Backpropagates the reults of one simulation to all the parent nodes where anynode is a leaf"""
        if anynode is not None:
            anynode.backprop(victory)
        else:
            return None

    def getStatePossibilities(self, anynode: Node, route):
        """Gets the current state's known children and their status"""
        if route:
            return self.getStatePossibilities(anynode.getChild(head(route)), tail(route))
        else:
            childsuccessrates = [10 for _ in range(7)]
            for x in range(7):
                if anynode.getChild(x) is not None:
                    t = anynode.getChild(x)
                    t.updatePayoff()
                    childsuccessrates[x] = t.payoff
            return childsuccessrates

    def MCTS(self):
        """Runs a lot of instances of the MCTS algorithm"""
        scalar = rd.uniform(0.7, 1)
        for run in range(rd.randint(420, ma.floor(720 * scalar))):
            self.selection(self.root, deepcopy(self.playinstance))

    def addHistory(self, instance):
        """Adds history"""
        self.playinstance.append(instance.previouspos)

    def resetHistory(self):
        """Resets history"""
        self.playinstance = []

class AI:
    """AI index class"""
    def __init__(self, name: str):
        """Constructor"""
        self.name = name
        self.brain = Brain(name)

    def forgetboard(self):
        """Forgets the board history"""
        self.brain.resetHistory()

    # def randomDropPos(self):
    #     """Randomly picks a dropping position"""
    #     drop = rd.randint(0, 6)
    #     self.brain.playinstance.append(drop)
    #     return drop

    def chooseDropPos(self):
        """Returns where the AI wishes to drop a piece."""
        self.brain.MCTS()
        childsuccessrates = self.brain.getStatePossibilities(self.brain.root, self.brain.playinstance)
        a = False
        while not a:
            if not theBoard.colFullCheck(highestPosInArray(childsuccessrates)):
                drop = highestPosInArray(childsuccessrates)
                return drop
            else:
                childsuccessrates[highestPosInArray(childsuccessrates)] = -1

    def rememberCurrentBoard(self, state: Board):
        """Adds any state's recently dropped piece to the brain's playinstance"""
        self.brain.playinstance.append(state.previouspos)

    def saveToFile(self, filename):
        """Saves the AI to an external file"""
        saver = open(str("ai/" + filename + ".c4ai"), "wb")
        pk.dump(self, saver)

def loadFromFile(filename):
    """Loads an AI from an external file"""
    loader = open(str("ai/" + filename + ".c4ai"), "rb")
    toreturn = pk.load(loader)
    return toreturn

def nonNegative(check):
    """Prevents negative indexing"""
    if check >= 0:
        return check
    else:
        raise Exception

def head(anything):
    """Returns the head of something"""
    if anything:
        return anything[0]
    else:
        return None

def tail(anything):
    """Returns the tail of something"""
    if len(anything) > 1:
        return anything[1:]
    else:
        return []

def highestPosInArray(anything):
    """Returns the respective position of the highest thing in an array"""
    if len(anything) == 1:
        return [0]
    elif not anything:
        raise Exception("Empty array inputted in the highestInArray() function.")
    else:
        highest = -1
        pos = 0
        for x in range(len(anything)):
            if anything[x] > highest:
                highest = anything[x]
                pos = x
        if highest == -1:
            return 0
        return pos

def posInArray(anything, tofind):
    """Returns the position of something in an array if applicable"""
    for x in range(len(anything)):
        if anything[x] == tofind:
            return x

theBoard = Board()
AILIST = []
gameAIPos = []

try:
    AILIST.append(loadFromFile("Miyagi"))
except:
    AILIST.append(AI("Miyagi"))

try:
    AILIST.append(loadFromFile("Chizuru"))
except:
    AILIST.append(AI("Chizuru"))

if __name__ == "__main__":
    print("Please run view.py to play")
