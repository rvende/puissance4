#TODO import numpy
from math import inf as infinity
import copy
import numpy as np
import time
import itertools as it
import random
import sys
import ast
from math import isnan 

#PUISSANCE 5 Grille 12*8

COMP = 1
HUMAN = -1

DEPTH = 4
HEIGHT = 8
WIDTH = 12
# Number of aligned coins to win
CONNECT = 5 

def children_states(state, player):
    turn = player
    children = []
    lastMoves = []
    for i in range(0, WIDTH):
        if hasSpace(state,i) != 0:
            lastMoves.append(i)
    return lastMoves


tH, tV, tD, tC = 0, 0, 0, 0
def eval_win(state, player):

    global tH, tV, tD, tC

    t1 = time.time()
    #Victoire Horizontale
    for i in range(HEIGHT):
        wins = getLineWin(state[i])
        if wins != 0:
            return wins
    tH += time.time() - t1
    

    t1 = time.time()
    #Victoire Verticale
    for i in range(WIDTH):
        wins = getLineWin(state[:, i])
        if wins != 0:
            return wins
    tV += time.time() - t1


    t1 = time.time()
    #Victoire Diagonale
    stateT = verticalMirror(state)
    for i in range(-3,8):
        d = np.diag(state,i)
        wins = getLineWin(d)
        if wins != 0:
            return wins

        #diag inversé
        d = np.diag(stateT,i)
        wins = getLineWin(d)
        if wins != 0:
            return wins
    tD += time.time() - t1


    t1 = time.time()
    for i in range(0,WIDTH):
        if (hasSpace(state,i) != 0):
            tmp = children_states(state, player)
            tC += time.time() - t1
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
    return tab, ([1]*10 + [3]*10 + [5]*5 + [infinity])

def find(line, subline):
    if np.all( [subline == line] ):
        return True
    else :
        return False


def eval_line(line):
    global CONNECT
    tabC, tabC_score = generateCenterCheck(COMP)
    accu = 0

    for idx in range(len(tabC)): 
        if find(line, tabC[idx]):
            accu += tabC_score[idx]

    for idx in range(len(tabC)): 
        if find(-line, tabC[idx]):
            accu -= tabC_score[idx]


    return accu


def getLineWin(line):
    linesC = np.split(line, np.asarray(line == HUMAN).nonzero()[0])
    for l in linesC:
        if len(l) != 0 and l[0] == HUMAN:
            l = l[1:]
        if len(l) >= CONNECT:
            if find(l, [COMP]*CONNECT):
                return COMP

    linesH = np.split(line, np.asarray(line == COMP).nonzero()[0])
    for l in linesH:
        if len(l) != 0 and l[0] == COMP:
            l = l[1:]
        if len(l) >= CONNECT:
            if find(l, [HUMAN]*CONNECT):
                return HUMAN
    return 0


def eval_global_score(state, score, lastMove, player):

    height = HEIGHT
    line = HEIGHT - hasSpace(state, lastMove)
    col = lastMove
    firstcol = col-(CONNECT-1) if col-(CONNECT-1) > 0 else 0
    lastcol = col + CONNECT if col + CONNECT < WIDTH else WIDTH
        
    previousScore = 0
    previousScore += dictScore[tuple(state[line, firstcol:lastcol])]
    previousScore += dictScore[tuple(state[:,col])]

    d = np.diag(state, col - line)
    if (len(d) > CONNECT):
        previousScore += dictScore[tuple(d)]

    d = np.diag(np.fliplr(state),(WIDTH -1 - col) - line)
    if (len(d) > CONNECT):
        previousScore += dictScore[tuple(d)]

    addMove(state,lastMove,player)

    newScore = 0
    newScore += dictScore[tuple(state[line, firstcol:lastcol])]
    newScore += dictScore[tuple(state[:,col])]

    d = np.diag(state, col - line)
    if (len(d) > CONNECT):
        newScore += dictScore[tuple(d)]

    d = np.diag(np.fliplr(state),(WIDTH -1 - col) - line)
    if (len(d) > CONNECT):
        newScore += dictScore[tuple(d)]

    removeMove(state,lastMove)

    return score + (newScore -previousScore)



Start = np.zeros((HEIGHT,WIDTH))
Tree = {}
Scores = {}

def hasSpace(state, col):
    return (state[:,col] == 0).sum()


def addMove(state, col, player):
    global HEIGHT
    for i in range(HEIGHT - 1,-1,-1):
        if state[i,col] != 0:
            state[i+1, col] = player
            return
    state[0,col] = player

def removeMove(state, col):
    global HEIGHT
    for i in range(HEIGHT - 1,-1,-1):
        if state[i,col] != 0:
            state[i, col] = 0
            return


def human_turn():
    global Start, currentScore
    move = -1
    print(f'Human turn ["O"]')
    print_board(Start)

    while move < 1 or move > WIDTH:
        try:
            move = int(input('Choose column (1-{}): '.format(WIDTH)))
            can_move = (hasSpace(Start,move-1) != 0)

            if not can_move or move > WIDTH or move < 1:
                print('Bad move')
                move = -1
            else:
                currentScore = eval_global_score(Start, currentScore, move-1, HUMAN)
                addMove(Start,move-1, HUMAN)
        except (EOFError, KeyboardInterrupt):
            print('error')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')


def choose_move(tupleList, movelist):
    global Start, currentScore
    best = -infinity
    best_Move = []

    for i in range(len(tupleList)):

        print(Scores[tupleList[i]])

        if Scores[tupleList[i]] > best:
            best = Scores[tupleList[i]]
            best_Move = [movelist[i]]

        if Scores[tupleList[i]] == best:
            best_Move.append(movelist[i])

    if len(best_Move) > 1:
        choice = random.randint(0, len(best_Move)-1)
        best_Move = [best_Move[choice]]

    if len(best_Move) == 0:
        for i in range(WIDTH):
            if hasSpace(Start,i):
                best_Move = [i]
                break

    currentScore = eval_global_score(Start, currentScore, best_Move[0], COMP)
    addMove(Start,best_Move[0], COMP)
    print("******AI played column ", best_Move[0]+1, "******");

def ai_turn(): 
    global Start, Scores, currentScore, tScore,tDraw
    print(f'AI turn ["X"]')
    print_board(Start)
    Scores = {}
    tScore = 0
    tDraw = 0
    #t0 = time.time()
    tmp = Start.copy()
    outList, movelist = minimax(tmp, COMP, DEPTH, currentScore, -infinity, infinity)
    print(">>>timer minimax {}".format(time.time()-t0))
    #print(" --->>> total time  eval_global_score {}".format(tScore))
    #print(" --->>> total time  draw {}".format(tDraw))
    #t1 = time.time()
    choose_move(outList,movelist)
    #print(">>>>timer choose_move {}".format(time.time()-t1))
    #print(len(Scores))

def verticalMirror(state):
    return state[:,::-1]

def npToTuple(state):
    return tuple(map(tuple, state))

def tupleToNp(tuple_):
   return np.asarray(tuple_)

def drawCheck(state, player):
    global tC
    t1 = time.time()
    for i in range(0,WIDTH):
        if (hasSpace(state,i) != 0):
            tmp = children_states(state, player)
            tC += time.time() - t1
            return tmp
    tC += time.time() - t1
    return 0

compteurMinimax = 0
tScore = 0
tWin = 0
currentScore = 0
tDraw = 0

def minimax(current_state, player, depth, score, alpha, beta):
    global Scores, compteurMinimax, tScore, tWin, currentScore, tDraw
    compteurMinimax += 1
    outList = []
    movelist = []
    if npToTuple(current_state) not in Scores:
        if not (score == infinity or score == -infinity):
            
            t2 = time.time()
            lastMoves = drawCheck(current_state, player)
            tDraw += time.time() - t2
            
            if type(lastMoves) != int and depth !=0:
                for el in lastMoves:
                    
                    t2 = time.time()
                    childscore = eval_global_score(current_state, score, el, player)
                    tScore += time.time() - t2
                    
                    addMove(current_state, el, player)
                    if depth == DEPTH:
                        outList.append(npToTuple(current_state))
                        movelist.append(el)
                    minimax(current_state, -player, depth-1, childscore, alpha, beta)
                    scoreChild = Scores[npToTuple(current_state)]
                    removeMove(current_state,el)
                    score = max(score,scoreChild) if player == COMP else min(score,scoreChild)
        
                    if (player == COMP):
                        alpha = max(alpha, scoreChild)
                    else :
                        beta = min(beta, scoreChild)
                    if beta <= alpha:
                        break;

        Scores[npToTuple(current_state)] = score
        return outList,movelist

            


def print_board(state):
    print("_________________________________________________")
    for x in range(HEIGHT-1,-1,-1):
        s = "|"
        for y in range(0,WIDTH):
            if state[x,y] == 0:
                s+="   "
            elif state[x,y] == COMP :
                s+=" X "
            else:
                s+=" O "
            s+="|"
        print(s)
        print("_________________________________________________")
    print("| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12|\n")


def setDictScore():
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
                val = int(val)

            dictScore[tuple(map(int, key.split(', ')))] = val

    except FileNotFoundError:
        print("File not Found, creating dictScore.txt")
        preCalcul()
    except :
        print("Unexpected error:", sys.exc_info()[0])
    finally:
        if file is not None:
            file.close()


dictScore = {}

def combiPossible(i):
    result = []
    if i == 1:
        result.append([1])
        result.append([-1])
        result.append([0])
    else :
        tmp = combiPossible(i-1)
        for e in tmp: 
            result.append( [1] + e )
            result.append( [0] + e )
            result.append( [-1] + e )
    if (i == 5):
        for el in result:
            dictScore[tuple(el)] = eval_line(np.asarray(el))
    elif i > 5:
        for el in result:
            dictScore[tuple(el)] = dictScore[tuple(el[:len(el)-1])] + eval_line(np.asarray(el[len(el)-CONNECT:len(el)]))
    return result


def preCalcul():
    
    combiPossible(CONNECT*2 -1)

    f = open("dictScore.txt", "w")
    for key in dictScore:
        f.write('{}:{}\n'.format(key, dictScore[key]))
    f.close()
    print("dictScore.txt created")

def main():
    global Start,currentScore


    t1 = time.time()
    setDictScore()
    print(" preCalcul {}\n".format(time.time() - t1))

    firstPlayer=2
    firstPlayer = int(input('Press 0 to go first, 1 to go second : '))
    while (firstPlayer!= 0 and firstPlayer!=1):
        print("Please press 0 or 1")
        firstPlayer = int(input('Press 0 to go first, 1 to go second : '))

    print("********************")

    if (firstPlayer == 1):
        ai_turn()
    while (type(eval_win(Start, COMP)) != int):
        human_turn()
        print("Calculated Score : ",currentScore)
        if(type(eval_win(Start, HUMAN)) == int):
            break
        ai_turn()
        print("Calculated Score : ",currentScore)


    print("\n Final board :")
    print_board(Start);
    score = eval_win(Start, COMP)
    if score == 1:
        print("AI win")
    elif score == -1:
        print("Human win")
    else:
        print("draw")

if __name__ == '__main__':
    main()

# TODO : heuristique 2 : random ??