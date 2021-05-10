#TODO import numpy
from PyQt5 import QtCore, QtWidgets
from math import inf as infinity
import copy
import numpy as np
import time
import itertools as it
import random
import sys
import ast
from math import isnan 

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


class ConfWorker(QtCore.QObject):
    
    request_signal = QtCore.pyqtSignal(str)
    turn_signal = QtCore.pyqtSignal(int)
    start_chrono_signal = QtCore.pyqtSignal()
    stop_chrono_signal = QtCore.pyqtSignal()
    QUIT = False
    #PUISSANCE 5 Grille 12*8

    COMP = 1
    HUMAN = -1

    DEPTH = 4
    HEIGHT = 8
    WIDTH = 12
    # Number of aligned coins to win
    CONNECT = 5 
    tH, tV, tD, tC = 0, 0, 0, 0
    ##########
    Start = np.zeros((HEIGHT,WIDTH))
    Tree = {}
    Scores = {}
    ##########
    compteurMinimax = 0
    tScore = 0
    tWin = 0
    currentScore = 0
    tDraw = 0
    ##########
    dictScore = {}
    #####
    signal_reived = False
    human_choice = None
    buttonTab = None

    def __init__(self, tab_button,parent=None):
        super(ConfWorker, self).__init__(parent)
        self.buttonTab = tab_button

    def addToken(self,col):
        self.human_choice = col
        self.signal_reived = True
    
    def reset(self):
        self.Start = np.zeros((self.HEIGHT,self.WIDTH))
        self.Tree = {}
        self.Scores = {}

    def children_states(self,state, player):
        turn = player
        children = []
        lastMoves = []
        for i in range(0, self.WIDTH):
            if self.hasSpace(state,i) != 0:
                lastMoves.append(i)
        return lastMoves


    def eval_win(self, state, player):

        t1 = time.time()
        #Victoire Horizontale
        for i in range(self.HEIGHT):
            wins = self.getLineWin(state[i])
            if wins != 0:
                return wins
        self.tH += time.time() - t1
        

        t1 = time.time()
        #Victoire Verticale
        for i in range(self.WIDTH):
            wins = self.getLineWin(state[:, i])
            if wins != 0:
                return wins
        self.tV += time.time() - t1


        t1 = time.time()
        #Victoire Diagonale
        stateT = self.verticalMirror(state)
        for i in range(-3,8):
            d = np.diag(state,i)
            wins = self.getLineWin(d)
            if wins != 0:
                return wins

            #diag inversé
            d = np.diag(stateT,i)
            wins = self.getLineWin(d)
            if wins != 0:
                return wins
        self.tD += time.time() - t1


        t1 = time.time()
        for i in range(0,self.WIDTH):
            if (self.hasSpace(state,i) != 0):
                tmp = self.children_states(state, player)
                self.tC += time.time() - t1
                return tmp
        return 0


    def generateCenterCheck(player):
        tab = [
            [ 0, 0, 0, player, player],
            [ 0, 0, player, 0, player],
            [ 0, 0, player, player, 0],
            [ 0, player, 0, 0, player],
            [ 0, player, 0, player, 0],
            [ 0, player, player, 0, 0],
            [ player, 0, 0, 0, player],
            [ player, 0, 0, player, 0],
            [ player, 0, player, 0, 0],
            [ player, player, 0, 0, 0],

            [ 0, 0, player, player, player],
            [ 0, player, 0, player, player],
            [ 0, player, player, 0, player],
            [ 0, player, player, player, 0],
            [ player, 0, 0, player, player],
            [ player, 0, player, 0, player],
            [ player, 0, player, player, 0],
            [ player, player, 0, 0, player],
            [ player, player, 0, player, 0],
            [ player, player, player, 0, 0],

            [ 0, player, player, player, player],
            [ player, 0, player, player, player],
            [ player, player, 0, player, player],
            [ player, player, player, 0, player],
            [ player, player, player, player, 0],

            [player, player, player, player, player]
        ]
        return tab, ([1]*10 + [5]*10 + [10]*5 + [100])

    def equal(self, line, subline):
        if np.array_equal(subline, line):
            return True
        else :
            return False

    def find(self, line, subline):
        for i in range(len(line)-len(subline) + 1):
            if np.all( [subline == line[i:i+len(subline)]] ):
                return True
        return False


    def eval_line(self, line):
        tabC, tabC_score = self.generateCenterCheck(self.COMP)
        accu = 0

        for idx in range(len(tabC)): 
            if self.equal(line, tabC[idx]):
                accu += tabC_score[idx]

        for idx in range(len(tabC)): 
            if self.equal(-line, tabC[idx]):
                accu -= tabC_score[idx]

        return accu


    def getLineWin(self, line):
        linesC = np.split(line, np.asarray(line == self.HUMAN).nonzero()[0])
        for l in linesC:
            if len(l) != 0 and l[0] == self.HUMAN:
                l = l[1:]
            if len(l) >= self.CONNECT:
                if self.find(l, [self.COMP]*self.CONNECT):
                    return self.COMP

        linesH = np.split(line, np.asarray(line == self.COMP).nonzero()[0])
        for l in linesH:
            if len(l) != 0 and l[0] == self.COMP:
                l = l[1:]
            if len(l) >= self.CONNECT:
                if self.find(l, [self.HUMAN]*self.CONNECT):
                    return self.HUMAN
        return 0


    def eval_global_score(self, state, score, lastMove, player):

        height = self.HEIGHT
        line = self.HEIGHT - self.hasSpace(state, lastMove)
        col = lastMove
        firstcol = col-(self.CONNECT-1) if col-(self.CONNECT-1) > 0 else 0
        lastcol = col + self.CONNECT if col + self.CONNECT < self.WIDTH else self.WIDTH
            
        previousScore = 0
        previousScore += self.dictScore[tuple(state[line, firstcol:lastcol])]
        previousScore += self.dictScore[tuple(state[:,col])]

        d = np.diag(state, col - line)
        if (len(d) > self.CONNECT):
            previousScore += self.dictScore[tuple(d)]

        d = np.diag(np.fliplr(state),(self.WIDTH -1 - col) - line)
        if (len(d) > self.CONNECT):
            previousScore += self.dictScore[tuple(d)]

        self.addMove(state,lastMove,player)

        newScore = 0
        newScore += self.dictScore[tuple(state[line, firstcol:lastcol])]
        newScore += self.dictScore[tuple(state[:,col])]

        d = np.diag(state, col - line)
        if (len(d) > self.CONNECT):
            newScore += self.dictScore[tuple(d)]

        d = np.diag(np.fliplr(state),(self.WIDTH -1 - col) - line)
        if (len(d) > self.CONNECT):
            newScore += self.dictScore[tuple(d)]

        self.removeMove(state,lastMove)

        return score + (newScore -previousScore)


    def hasSpace(self, state, col):
        return (state[:,col] == 0).sum()


    def addMove(self, state, col, player):
        for i in range(self.HEIGHT - 1,-1,-1):
            if state[i,col] != 0:
                state[i+1, col] = player
                return
        state[0,col] = player

    def removeMove(self, state, col):
        for i in range(self.HEIGHT - 1,-1,-1):
            if state[i,col] != 0:
                state[i, col] = 0
                return


    def human_turn(self):
        move = -1
        print(f'Human turn ["O"]')
        self.print_board(self.Start)

        while move < 1 or move > self.WIDTH:
            try:
                while not self.signal_reived:
                    pass
                move = int(self.human_choice)
                #move = int(input('Choose column (1-{}): '.format(self.WIDTH)))
                if move <= self.WIDTH and move >= 1:
                    can_move = (self.hasSpace(self.Start,move-1) != 0)

                    if not can_move :
                        print('Bad move')
                        move = -1
                    else:
                        self.currentScore = self.eval_global_score(self.Start, self.currentScore, move-1, self.HUMAN)
                        self.addMove(self.Start,move-1, self.HUMAN)
                else :
                    print('Bad move')
                    move = -1
            except (EOFError, KeyboardInterrupt):
                print('error')
                exit()
            except (KeyError, ValueError):
                print('Bad choice')
        self.signal_reived = False


    def choose_move(self, tupleList, movelist):
        best = -infinity
        best_Move = []

        for i in range(len(tupleList)):

            #print(Scores[tupleList[i]])

            if self.Scores[tupleList[i]] > best:
                best = self.Scores[tupleList[i]]
                best_Move = [movelist[i]]

            if self.Scores[tupleList[i]] == best:
                best_Move.append(movelist[i])

        if len(best_Move) > 1:
            choice = random.randint(0, len(best_Move)-1)
            best_Move = [best_Move[choice]]

        if len(best_Move) == 0:
            for i in range(self.WIDTH):
                if self.hasSpace(self.Start,i):
                    best_Move = [i]
                    break

        currentScore = self.eval_global_score(self.Start, self.currentScore, best_Move[0], self.COMP)
        self.addMove(self.Start,best_Move[0], self.COMP)
        print("******AI played column ", best_Move[0]+1, "******")

    def ai_turn(self): 
        print(f'AI turn ["X"]')
        self.turn_signal.emit(self.COMP)

        self.print_board(self.Start)
        self.Scores = {}
        tScore = 0
        tDraw = 0
        #t0 = time.time()
        tmp = self.Start.copy()
        outList, movelist = self.minimax(tmp, self.COMP, self.DEPTH, self.currentScore, -infinity, infinity)
        #print(">>>timer minimax {}".format(time.time()-t0))
        #print(" --->>> total time  eval_global_score {}".format(tScore))
        #print(" --->>> total time  draw {}".format(tDraw))
        #t1 = time.time()
        self.choose_move(outList,movelist)
        #print(">>>>timer choose_move {}".format(time.time()-t1))
        #print(len(Scores))

    def verticalMirror(self, state):
        return state[:,::-1]

    def npToTuple(self, state):
        return tuple(map(tuple, state))

    def tupleToNp(self, tuple_):
        return np.asarray(tuple_)

    def drawCheck(self, state, player):
        t1 = time.time()
        for i in range(0,self.WIDTH):
            if (self.hasSpace(state,i) != 0):
                tmp = self.children_states(state, player)
                self.tC += time.time() - t1
                return tmp
        self.tC += time.time() - t1
        return 0

    def minimax(self, current_state, player, depth, score, alpha, beta):
        #global Scores, compteurMinimax, tScore, tWin, currentScore, tDraw
        self.compteurMinimax += 1
        outList = []
        movelist = []
        if self.npToTuple(current_state) not in self.Scores:
            if not (score == infinity or score == -infinity):
                
                t2 = time.time()
                lastMoves = self.drawCheck(current_state, player)
                self.tDraw += time.time() - t2
                
                if type(lastMoves) != int and depth !=0:
                    for el in lastMoves:
                        
                        t2 = time.time()
                        childscore = self.eval_global_score(current_state, score, el, player)
                        self.tScore += time.time() - t2
                        
                        self.addMove(current_state, el, player)

                        tupleTmp = self.npToTuple(current_state)

                        if depth == self.DEPTH:
                            outList.append(tupleTmp)
                            movelist.append(el)
                        
                        self.minimax(current_state, -player, depth-1, childscore, alpha, beta)

                        scoreChild = self.Scores[tupleTmp]
                        self.removeMove(current_state,el)
                        score = max(score,scoreChild) if player == self.COMP else min(score,scoreChild)
            
                        if (player == self.COMP):
                            alpha = max(alpha, scoreChild)
                        else :
                            beta = min(beta, scoreChild)
                        if beta <= alpha:
                            pass

            self.Scores[self.npToTuple(current_state)] = score
            return outList,movelist

    def print_board(self, state):
        print("_________________________________________________")
        for x in range(self.HEIGHT-1,-1,-1):
            s = "|"
            for y in range(0,self.WIDTH):
                if state[x,y] == 0:
                    s+="   "
                elif state[x,y] == self.COMP :
                    s+=" X "
                    self.buttonTab[x,y].setIcon(QIcon("red85.png"))
                    self.buttonTab[x,y].setIconSize(QSize(80, 80))
                else:
                    s+=" O "
                    self.buttonTab[x,y].setIcon(QIcon("yellow85.png"))
                    self.buttonTab[x,y].setIconSize(QSize(80, 80))
                s+="|"
            print(s)
            print("_________________________________________________")
        print("| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12|\n")


    def setDictScore(self):
        file = None

        try:
            file = open('dictScore.txt')
            for line in file:
                (key, val) = line[1:len(line)-1].split(':')
                key = key[:len(key)-1]

                if val == "-inf":
                    val = -infinity
                elif val == "inf":
                    val = infinity
                else:
                    val = float(val)

                self.dictScore[tuple(map(int, key.split(', ')))] = val

        except FileNotFoundError:
            print("File not Found, creating dictScore.txt")
            self.preCalcul()
        except :
            print("Unexpected error:", sys.exc_info()[0])
        finally:
            if file is not None:
                file.close()

    def combiPossible(self, i):
        result = []
        if i == 1:
            result.append([1])
            result.append([-1])
            result.append([0])
        else :
            tmp = self.combiPossible(i-1)
            for e in tmp: 
                result.append( [1] + e )
                result.append( [0] + e )
                result.append( [-1] + e )
        if (i == 5):
            for el in result:
                self.dictScore[tuple(el)] = self.eval_line(np.asarray(el))
        elif i > 5:
            for el in result:
                self.dictScore[tuple(el)] = self.dictScore[tuple(el[:len(el)-1])] + self.eval_line(np.asarray(el[len(el)-self.CONNECT:len(el)]))
        return result


    def preCalcul(self):
        
        self.combiPossible(self.CONNECT*2 -1)

        f = open("dictScore.txt", "w")
        for key in self.dictScore:
            f.write('{}:{}\n'.format(key, self.dictScore[key]))
        f.close()
        print("dictScore.txt created")

    def main(self):


        t1 = time.time()
        self.setDictScore()
        print(" preCalcul {}\n".format(time.time() - t1))
        
        while not self.QUIT:
            firstPlayer=2
            firstPlayer = int(input('Press 0 to go first, 1 to go second : '))
            while (firstPlayer!= 0 and firstPlayer!=1):
                print("Please press 0 or 1")
                firstPlayer = int(input('Press 0 to go first, 1 to go second : '))

            print("********************")

            if (firstPlayer == 1):
                t3 = time.time()
                self.ai_turn()
                print("AI played in {} sec".format(time.time()-t3))
            self.start_chrono_signal.emit()
            while (type(self.eval_win(self.Start, self.COMP)) != int):
                self.human_turn()
                print("Calculated Score : ",self.currentScore)
                if(type(self.eval_win(self.Start, self.HUMAN)) == int):
                    break
                t3 = time.time()
                self.ai_turn()
                print("AI played in {} sec".format(time.time()-t3))
                print("Calculated Score : ",self.currentScore)


            print("\n Final board :")
            self.print_board(self.Start)
            score = self.eval_win(self.Start, self.COMP)
            if score == 1:
                #print("AI win")
                self.stop_chrono_signal.emit()
                self.request_signal.emit("AI WIN !!!")
            elif score == -1:
                #print("Human win")
                self.stop_chrono_signal.emit()
                self.request_signal.emit("Human WIN !!!")
            else:
                #print("draw")
                self.stop_chrono_signal.emit()
                self.request_signal.emit("Human WIN !!!")





