"""View file. This creates a GUI so that the user can interact with the game. It sends instrunctions
to the controller based on what the user inputs and updates based on what it receives from the Controller"""

import tkinter as tk
import tkinter.colorchooser as tkCol
import controller
import atexit

class MainMenu(tk.Frame):
    """Main menu class"""
    def __init__(self, *args, **kwargs):
        """Constructor"""
        tk.Frame.__init__(self, *args, **kwargs)
        lb1 = tk.Label(self, text="Connect Four")
        lb1.grid(row=0, padx=180, sticky='N')
        lb2 = tk.Label(self, text="Please pick an option")
        lb2.grid(row=1, sticky='N')
        # bt1, 2, 3 - gameplay buttons
        # bt4 - options button
        # bt5 - quit button
        bt1 = tk.Button(self, text="Human vs Human", command=lambda: FRAME2.initialiseGame(0)) # Game type HvH
        bt1.grid(row=4, ipadx=10, ipady=10, pady=5, sticky='N')
        bt2 = tk.Button(self, text="Human vs AI", command=lambda: FRAME2.initialiseGame(1)) # Game type HvA
        bt2.grid(row=5, ipadx=10, ipady=10, pady=5, sticky='N')
        bt3 = tk.Button(self, text="AI vs AI", command=lambda: FRAME2.initialiseGame(2)) # Game type AvA
        bt3.grid(row=6, ipadx=10, ipady=10, pady=5, sticky='N')
        bt4 = tk.Button(self, text="Options", command=lambda: FRAME3.show()) # Options menu
        bt4.grid(row=7, ipadx=3, ipady=3, pady=5, sticky='N')
        bt5 = tk.Button(self, text="Quit", command=lambda: MainMenu.quitting()) # Exit game
        bt5.grid(row=8, ipadx=3, ipady=3, pady=5, sticky='N')
    
    def show(self):
        """Lifts the Main Menu to the front"""
        self.lift()

    @staticmethod
    def quitting():
        """Saves all new data of the AI to their respective files then quits the game"""
        controller.saveAI()
        exit()

class GameBoard(tk.Frame):
    """Game Board and interactions class"""
    def __init__(self, *args, **kwargs):
        """Constructor"""
        tk.Frame.__init__(self, *args, **kwargs)
        self.board = []
        self.gameOver = False

        # storing names in a list for easy access
        self.names = [tk.StringVar(), tk.StringVar()]
        # humannames are for replacing AI names in the names array when accesing gametype 0 or 1
        self.humannames = [tk.StringVar(), tk.StringVar()]
        self.humannames[0].set("Human 1")
        self.humannames[1].set("Human 2")
        self.gameType = 0
        self.names[0].set("Human 1")
        self.names[1].set("Human 2")
        self.pl1score = tk.IntVar()
        self.pl1score.set(0)
        self.pl2score = tk.IntVar()
        self.pl2score.set(0)
        self.currentturn = tk.IntVar()
        self.currentturn.set(0)
        self.turnmsg = tk.StringVar()
        self.turnmsg.set("It is now " + self.names[0].get() + "'s turn...")

        # score display player 1
        sc1disp = tk.Label(self, textvariable=self.pl1score, bg='#FFFFFF', borderwidth=2, relief='ridge')
        sc1disp.grid(row=0, column=0, pady=7, ipadx=9, ipady=7)

        # name display player 1
        nam1disp = tk.Label(self, textvariable=self.names[0], bg='#FFFFFF', borderwidth=2,
                            relief='ridge', wraplength=52)
        nam1disp.grid(row=0, column=1, pady=7, ipadx=7, ipady=7, columnspan=2)

        # VS text display
        vs = tk.Label(self, text="VS")
        vs.grid(row=0, column=3)

        #score display player 2
        sc2disp = tk.Label(self, textvariable=self.pl2score, bg='#FFFFFF', borderwidth=2, relief='ridge')
        sc2disp.grid(row=0, column=6, pady=7, ipadx=9, ipady=7)

        # name display player 2
        nam2disp = tk.Label(self, textvariable=self.names[1], bg='#FFFFFF', borderwidth=2,
                            relief='ridge', wraplength=52)
        nam2disp.grid(row=0, column=4, pady=7, ipadx=7, ipady=7, columnspan=2)

        # turn display
        turndisp = tk.Label(self, textvariable=self.turnmsg, wraplength=170)
        turndisp.grid(row=1, ipadx=5, ipady=3, columnspan=7)

        # grid cells
        for y in range(6):
            self.board.append([])
            for x in range(7):
                self.board[y].append(tk.Label(self, text='    ', bg='#FFFFFF', borderwidth=2, relief='ridge'))
                self.board[y][x].grid(row=y+2, column=x, ipadx=10, ipady=10)

        # drop button row
        self.buttonarray = []
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(0)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(1)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(2)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(3)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(4)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(5)))
        self.buttonarray.append(tk.Button(self, text='V', command=lambda: self.sendPieceToDrop(6)))
        for bt in range(7):
            self.buttonarray[bt].grid(row=9, column=bt, ipadx=7, ipady=3)

        # other buttons
        retirebt = tk.Button(self, text="Retire", command=lambda: FRAME1.show())
        self.playagainbt = tk.Button(self, text="Play Again", command=lambda: self.playAgain())
        self.playagainbt.config(state='disabled')
        self.playagainbt.grid(row=10, column=2, columnspan=2, pady=15)
        retirebt.grid(row=10, column=0, columnspan=2, pady=15)

    def show(self):
        """Lifts the Game Board to the front"""
        self.lift()
    
    def initialiseGame(self, gameType):
        """Initialises game, including resetting the board, setting up any AI, etc."""
        # Game Types:
        # 0. Human vs Human
        # 1. Human vs AI
        # 2. AI vs AI
        self.gameOver = False
        self.gameType = gameType
        controller.setGameType(gameType)
        # Name setup
        self.names[0].set(self.humannames[0].get())
        self.names[1].set(self.humannames[1].get())
        if gameType == 1 or gameType == 2:
            self.names[1].set(controller.model.AILIST[AI1].name)
        if gameType == 2:
            self.names[0].set(controller.model.AILIST[AI1].name)
            self.names[1].set(controller.model.AILIST[AI2].name)

        controller.resetBoard()
        self.currentturn.set(0)
        self.pl1score.set(0)
        self.pl2score.set(0)
        self.buttonEnableDisable(0)
        self.playagainbt.config(state='disabled')        
        self.updateBoard()
        self.show()
        if gameType == 2:
            controller.sendAIpositions(AI1, AI2)
            self.buttonEnableDisable(1)
            self.gameOver = True
            self.playagainbt.config(state='active')
            self.turnmsg.set("Press 'Play Again' to start!")
            self.update_idletasks()
            self.AIprocess()
    
    def buttonEnableDisable(self, enabledisable):
        """Enables or disables the dropper buttons for when an AI is playing to prevent player interference"""
        # 0. Enable
        # 1. Disable
        for bt in range(7):
            if enabledisable == 0:
                self.buttonarray[bt].config(state='active')
            else:
                self.buttonarray[bt].config(state='disabled')
    
    def sendPieceToDrop(self, pos):
        """Sends a piece to drop to the Controller"""
        if controller.getColStatus(pos):
            # Column not full
            controller.dropPiece(pos)
            self.switchTurns()
            self.updateBoard()
            return True
        else:
            # Column full
            self.turnmsg.set("Cannot drop a piece there!")
            self.update_idletasks()
            # Runs another AI process if the AI tries to drop at a full column
            if self.gameType == 1:
                if self.currentturn == 1:
                    self.AIprocess()
            elif self.gameType == 2:
                self.AIprocess()
            return False
    
    def switchTurns(self):
        """Switches the player turns from player 1 to player 2 and vice versa and checks for a win"""
        if self.currentturn.get() == 0:
            self.currentturn.set(1)
            if self.gameType == 1 or self.gameType == 2:
                self.buttonEnableDisable(1)
                self.wincheck()
                self.updateBoard()
                self.AIprocess()
            else:
                self.wincheck()
        else:
            self.currentturn.set(0)
            self.buttonEnableDisable(0)
            if self.gameType == 2:
                self.buttonEnableDisable(1)
                self.wincheck()
                self.updateBoard()
                self.AIprocess()
            else:
                self.wincheck()

    def AIprocess(self):
        """The AI process, involving thinking about where to drop pieces"""
        if not self.gameOver:
            dropped = False
            while not dropped:
                dec = -1
                if self.gameType == 1:
                    dec = controller.getAIDecision(AI1)
                elif self.gameType == 2:
                    if self.currentturn.get() == 0:
                        dec = controller.getAIDecision(AI1)
                    elif self.currentturn.get() == 1:
                        dec = controller.getAIDecision(AI2)
                    else:
                        raise Exception("Piece is not dropped")
                else:
                    pass
                if dec != -1:
                    dropped = self.sendPieceToDrop(dec)
                else:
                    raise Exception("dec not reassigned")

    def updateBoard(self):
        """Fetches the board fron the Model via Controller and updates the visible board with the new information"""
        modelboard = controller.fetchBoard()
        for y in range(6):
            for x in range(7):
                if modelboard[y][x] == 0:
                    self.board[y][x].config(bg='#FFFFFF')
                elif modelboard[y][x] == 1:
                    self.board[y][x].config(bg=pl1col)
                elif modelboard[y][x] == 2:
                    self.board[y][x].config(bg=pl2col)
                else:
                    raise Exception("Foreign variable within the modelboard")
                if not self.gameOver:
                    self.turnmsg.set("It is now " + self.names[self.currentturn.get()].get() + "'s turn...")
                self.update_idletasks()
    
    def wincheck(self):
        """Checks for a win from the model board and parses the win procedure if a win is attained"""
        winningplayer = controller.winCheck()
        if winningplayer == 0:
            return False
        elif winningplayer == 3:
            self.draw()
            return True
        else:
            self.win(winningplayer-1)
            return True
    
    def win(self, player):
        """Winning procedure, disabling piece dropping, displaying a win message,
        adding score and enabling the play again button"""
        self.buttonEnableDisable(1)
        self.gameOver = True
        self.turnmsg.set(self.names[player].get() + " has won!")
        if player == 0:
            self.pl1score.set(self.pl1score.get() + 1)
        else:
            self.pl2score.set(self.pl2score.get() + 1)
        self.playagainbt.config(state='active')
        self.update_idletasks()
    
    def draw(self):
        """Draw procedure. Almost identical to the win procedure, except the different message,
        and no player earns score"""
        self.gameOver = True
        self.buttonEnableDisable(1)
        self.turnmsg.set("It's a draw!")
        self.playagainbt.config(state='active')
        self.update_idletasks()
    
    def playAgain(self):
        """Procedure for when the Play Again button is pressed"""
        controller.resetBoard()
        self.gameOver = False
        self.updateBoard()
        if self.gameType != 2:
            self.buttonEnableDisable(0)
        self.playagainbt.config(state='disabled')
        self.currentturn.set(0)
        self.turnmsg.set("It is now " + self.names[0].get() + "'s turn...")
        self.update_idletasks()
        if self.gameType == 2:
            self.AIprocess()

class OptionsMenu(tk.Frame):
    """Options menu class"""
    def __init__(self, *args, **kwargs):
        """Constructor"""
        tk.Frame.__init__(self, *args, **kwargs)
        somelabel = tk.Label(self, text="Options menu")
        somelabel.grid(row=0, padx=5, pady=5, sticky='NW')
        # P1 Name
        # p1setprompt - prompt
        p1setprompt = tk.Label(self, text="Human 1 Name:")
        p1setprompt.grid(row=1, column=0, sticky='W')
        # p1set - text entry
        p1set = tk.Entry(self)
        # p1setbt - button for saving name
        p1setbt = tk.Button(self, text="SET", command=lambda: self.changeName(0, p1set.get()))
        # p1disp - name preview
        self.p1disp = tk.StringVar()
        self.p1disp.set("Current: " + FRAME2.names[0].get())
        p1displab = tk.Label(self, textvariable=self.p1disp)
        p1set.grid(row=2, column=0)
        p1setbt.grid(row=2, column=1, ipadx=5)
        p1displab.grid(row=2, column=2, sticky='W')
        # P2 Name
        # p2setprompt - prompt
        p2setprompt = tk.Label(self, text="Human 2 Name:")
        p2setprompt.grid(row=3, column=0, sticky='W')
        # p2set - text entry
        p2set = tk.Entry(self)
        # p2setbt - button for saving name
        p2setbt = tk.Button(self, text="SET", command=lambda: self.changeName(1, p2set.get()))
        # p2disp - name preview
        self.p2disp = tk.StringVar()
        self.p2disp.set("Current: " + FRAME2.names[1].get())
        p2displab = tk.Label(self, textvariable=self.p2disp)
        p2set.grid(row=4, column=0)
        p2setbt.grid(row=4, column=1, ipadx=5)
        p2displab.grid(row=4, column=2, sticky='W')  
        # Col 1
        # lab3 - prompt
        lab3 = tk.Label(self, text="Player 1 Colour:")
        lab3.grid(row=5, column=0, sticky='W', pady=2)
        # bt1label - text within the button
        self.bt1label = tk.StringVar()
        self.bt1label.set(pl1col)
        # ex1 - example colour
        self.ex1 = tk.Label(self, text='     ', bg=pl1col, borderwidth=2, relief="ridge")
        bt1 = tk.Button(self, textvariable=self.bt1label, command=lambda: self.pickColour(0))
        bt1.grid(row=5, column=1, ipadx=5, sticky='E')
        self.ex1.grid(row=5, column=2, sticky='W')
        bt1.grid_columnconfigure(1, weight=2)
        # Col 2
        # lab4 - prompt
        lab4 = tk.Label(self, text="Player 2 Colour:")
        lab4.grid(row=6, column=0, sticky='W', pady=2)
        # bt2label - text within the button
        self.bt2label = tk.StringVar()
        self.bt2label.set(pl2col)
        # ex2 - example colour
        self.ex2 = tk.Label(self, text='     ', bg=pl2col, borderwidth=2, relief="ridge")
        bt2 = tk.Button(self, textvariable=self.bt2label, command=lambda: self.pickColour(1))
        bt2.grid(row=6, column=1, ipadx=5, sticky='E')
        self.ex2.grid(row=6, column=2, sticky='W')
        bt2.grid_columnconfigure(1, weight=2)
        # AI 1
        # lab1 - prompt
        lab1 = tk.Label(self, text="First AI to use:")
        lab1.grid(row=7, column=0, sticky='W', pady=2)
        # self.disp1 - text in dropdown
        self.disp1 = tk.StringVar(self)
        self.disp1.set("Miyagi")
        # dd1 - dropdown
        dd1 = tk.OptionMenu(self, self.disp1, "Miyagi", "Chizuru")
        dd1.grid(row=7, column=1, sticky='E')
        dd1.grid_columnconfigure(1, weight=2)
        # AI 2
        # lab2 - prompt
        lab2 = tk.Label(self, text="Second AI to use:")
        lab2.grid(row=8, column=0, sticky='W', pady=2)
        # self.disp2 - text in dropdown
        self.disp2 = tk.StringVar(self)
        self.disp2.set("Chizuru")
        # dd2 - dropdown
        dd2 = tk.OptionMenu(self, self.disp2, "Chizuru", "Miyagi")
        dd2.grid(row=8, column=1, sticky='E')
        dd2.grid_columnconfigure(1, weight=2)
        # Dropdown option menus based on a script from http://effbot.org/tkinterbook/optionmenu.htm
        # Go Back button
        btgoback = tk.Button(self, text="Go Back", command=lambda: self.setAI())
        btgoback.grid(row=9, columnspan=2, ipadx=8)
        btgoback.grid_columnconfigure(0, weight=3)
        lab5 = tk.Label(self, text="Changes are automatically saved.")
        lab5.grid(row=10, columnspan=2)
    
    def setAI(self):
        """Sets the AI based on user choice"""
        global AI1
        global AI2
        FRAME1.show()
        AI1 = self.disp1.get()
        if AI1 == 'Miyagi':
            AI1 = 0
        elif AI1 == 'Chizuru':
            AI1 = 1
        AI2 = self.disp2.get()
        if AI2 == 'Miyagi':
            AI2 = 0
        elif AI2 == 'Chizuru':
            AI2 = 1

    def pickColour(self, playerIndex):
        """Lets the user pick a colour via a pop up GUI"""
        colour = tkCol.askcolor()
        if playerIndex == 0:
            global pl1col
            pl1col = colour[1]
            self.bt1label.set(pl1col)
            self.ex1.config(bg=pl1col)
            self.update_idletasks()
        else:
            global pl2col
            pl2col = colour[1]
            self.bt2label.set(pl2col)
            self.ex2.config(bg=pl2col)
            self.update_idletasks()
    
    def changeName(self, nameindex, newname):
        """Changes the name of a human player"""
        FRAME2.names[nameindex].set(newname)
        FRAME2.humannames[nameindex].set(newname)
        self.p1disp.set("Current: " + FRAME2.humannames[0].get())
        self.p2disp.set("Current: " + FRAME2.humannames[1].get())
        self.update_idletasks()
    
    def show(self):
        """Lifts the Options menu to the front"""
        self.lift()

class Window(tk.Frame):
    """Window that keeps all of the pages"""
    def __init__(self, *args, **kwargs):
        """Constructor"""
        tk.Frame.__init__(self, *args, **kwargs)
        global FRAME1
        global FRAME2
        global FRAME3
        FRAME1 = MainMenu(self)
        FRAME2 = GameBoard(self)
        FRAME3 = OptionsMenu(self)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        FRAME1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        FRAME2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        FRAME3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        FRAME1.show()

if __name__ == "__main__":
    pl1col = '#ff0000'
    pl2col = '#ffff00'
    AI1 = 0
    AI2 = 1
    # 0: Miyagi
    # 1: Chizuru
    Root = tk.Tk()
    mainWindow = Window(Root)
    mainWindow.pack(side="top", fill="both", expand=True)
    Root.wm_geometry("450x550")
    Root.title("Connect Four")
    Root.resizable(width=False, height=False)
    # Root.iconbitmap()
    Root.mainloop()
    atexit.register(MainMenu.quitting())

# Tkinter multi-page code structure taken from
# https://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application

