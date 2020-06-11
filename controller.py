"""Controller file. This file acts as a communication between the Model and the View."""

import model

def getLocStatus(x, y):
    """Fetches the ID of an individual space within the board"""
    if model.theBoard.grid[y][x] == 0:
        return 0
    elif model.theBoard.grid[y][x] == 1:
        return 1
    elif model.theBoard.grid[y][x] == 2:
        return 2
    else:
        raise Exception("Foreign variable found within board")

def getColStatus(x):
    """Returns the availability of a column by checking whether the top space of a column is free"""
    if model.theBoard.grid[0][x] == 0:
        return True
    else:
        return False

def resetBoard():
    """Resets the board to a clean state"""
    for y in range(6):
        for x in range(7):
            model.theBoard.grid[y][x] = 0
            model.theBoard.currentplayer = 1
    for z in range(len(model.AILIST)):
        model.AILIST[z].forgetboard()

def fetchBoard():
    """Fetches the board from the model"""
    return model.theBoard.grid

def winCheck():
    """Returns whether a win has been achieved in the board"""
    return model.theBoard.winCheck()

def dropPiece(pos):
    """Sends a piece to the model for dropping"""
    model.theBoard.addPiece(pos, True)

def getAIDecision(index):
    """Gets the AI's decision for dropping a piece"""
    return model.AILIST[index].chooseDropPos()

def saveAI():
    """Saves the current AI profiles"""
    for x in model.AILIST:
        x.saveToFile(x.name)

def setGameType(gameType):
    """Sets game type"""
    model.theBoard.gameType = gameType

def sendAIpositions(pos1, pos2):
    """Sends the positions of the AI to the Model for use in AI vs AI"""
    model.gameAIPos = [pos1, pos2]

def getAIPlayerPos(name):
    """Returns the position of any AI during game play"""
    # 0: Miyagi
    # 1: Chizuru
    nameindex = 0
    if name == "Chizuru":
        nameindex = 1
    if model.theBoard.gameType == 0:
        return None
    elif model.theBoard.gameType == 1:
        return 2
    else:
        if model.gameAIPos[0] == nameindex:
            return 1
        elif model.gameAIPos[1] == nameindex:
            return 2
        else:
            return None

if __name__ == "__main__":
    print("Please run view.py to play")
