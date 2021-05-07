#TODO import numpy
from math import inf as infinity
import copy
import numpy as np
import time
import itertools as it

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
            tmp = state.copy()
            tmp = addMove(tmp,i, player)
            children.append(tmp)
            lastMoves.append(i)
    return children, lastMoves


tH, tV, tD, tC = 0, 0, 0, 0
#TODO verification sur le dernier mouvement
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
    for i in range(len(line)-len(subline) + 1):
        if np.all( [subline == line[i:i+len(subline)]] ):
            return True
    return False


def eval_line(line):
    global CONNECT
    tabC, tabC_score = generateCenterCheck(COMP)
    accu = 0

    for idx in range(len(tabC)): 
        if find(line, tabC[idx]):
            accu += tabC_score[idx]

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


def getLineScore(line):
    score = 0
    linesC = np.split(line, np.asarray(line == HUMAN).nonzero()[0])
    for l in linesC:
        if len(l) != 0 and l[0] == HUMAN:
            l = l[1:]
        if len(l) >= CONNECT:
            score += dictScore[tuple(l)]

    linesH = np.split(line, np.asarray(line == COMP).nonzero()[0])
    for l in linesH:
        if len(l) != 0 and l[0] == COMP:
            l = l[1:]
        if len(l) >= CONNECT:
            score -= dictScore[tuple(-l)]

    return score


def eval_global_score(stateRef, score, lastMove, player):
    state = stateRef.copy()

    previousScore = 0
    height = HEIGHT

    line = HEIGHT - hasSpace(state, lastMove)
    col = lastMove

    previousScore += getLineScore(state[line])
    previousScore += getLineScore(state[:,col])
    d = np.diag(state, col - line)
    previousScore += getLineScore(d)
    d = np.diag(np.fliplr(state),(WIDTH -1 - col) - line)
    previousScore += getLineScore(d)

    state = addMove(state,lastMove,player)
    newScore = 0
    newScore += getLineScore(state[line])
    newScore += getLineScore(state[:,col])
    d = np.diag(state, col - line)
    newScore += getLineScore(d)
    d = np.diag(np.fliplr(state),(WIDTH -1 - col) - line)
    newScore += getLineScore(d)

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
            return state
    state[0,col] = player
    return state


def human_turn():
    global Start, currentScore
    move = -1
    print(f'Human turn ["O"]')
    print_board(Start)

    while move < 1 or move > WIDTH:
        try:
            move = int(input('Choose column (1-{}): '.format(WIDTH)))
            can_move = (hasSpace(Start,move-1) != 0)

            if not can_move:
                print('Bad move')
                move = -1
            else:
                currentScore = eval_global_score(Start, currentScore, move-1, HUMAN)
                Start = addMove(Start,move-1, HUMAN)
        except (EOFError, KeyboardInterrupt):
            print('error')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')


def choose_move():
    global Start, currentScore
    #print_board(Start)
    children, lastMoves = eval_win(Start, COMP)
    best = -infinity
    best_index = None
    for i in range(len(children)):
        if Scores[npToTuple(children[i])] >= best:
            best = Scores[npToTuple(children[i])]
            best_Move = lastMoves[i]
    currentScore = eval_global_score(Start, currentScore, best_Move, COMP)
    Start = addMove(Start,best_Move, COMP)
    print("******AI played column ", best_Move+1, "******");

def ai_turn(): 
    global Start, Scores, currentScore, tScore
    print(f'AI turn ["X"]')
    print_board(Start)
    Scores = {}
    tScore = 0
    t0 = time.time()
    minimax(Start, COMP, DEPTH, currentScore)
    print(">>>timer minimax {}".format(time.time()-t0))
    print(" --->>> total time  eval_global_score {}".format(tScore))
    t1 = time.time()
    choose_move()
    print(">>>>timer choose_move {}".format(time.time()-t1))
    print(len(Scores))

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
            tmp, tmp2 = children_states(state, player)
            tC += time.time() - t1
            return tmp, tmp2
    tC += time.time() - t1
    return 0 , 0

compteurMinimax = 0
tScore = 0
tWin = 0
currentScore = 0

def minimax(current_state, player, depth, score):
    global Scores, compteurMinimax, tScore, tWin, currentScore
    compteurMinimax += 1

    if not (score == infinity or score == -infinity):
        children, lastMoves = drawCheck(current_state, player)
        
        if type(children) != int and depth !=0:
            for i in range(len(children)):
                #print(children)
                if npToTuple(children[i]) not in Scores.keys():  
                    t2 = time.time()
                    childscore = eval_global_score(current_state, score, lastMoves[i], player)
                    tScore += time.time() - t2
                    minimax(children[i], -player, depth-1, childscore)
                score = max(score,Scores[npToTuple(children[i])]) if player == COMP else min(score,Scores[npToTuple(children[i])])
    Scores[npToTuple(current_state)] = score
            


def print_board(state):
    print("*************************************************")
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
        print("*************************************************")
    print("| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12|\n")


dictScore = {}

def combiPossible(i):
    result = []
    if i == 1:
        result.append([1])
        result.append([0])
    else : 
        tmp = combiPossible(i-1)
        for e in tmp: 
            result.append( [1]  + e )
            result.append( [0]  + e )
    return result


def preCalcul():
    for i in range(CONNECT, WIDTH + 1):
        for p in combiPossible(i):
            dictScore[tuple(p)] = eval_line(p)


def main():
    global Start,currentScore

    t1 = time.time()
    preCalcul()

    print(" preCalcul {}".format(time.time() - t1))

    print(len(dictScore))
    # addMove(Start, 5, COMP)

    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # print_board(Start)
    # print(eval_global_score(Start))
    


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

# TODO : Optimisation evalWin
# TODO : eval_win avec dernier move 
# TODO : heuristique 2 : random ?? 
# TODO : alpha beta 