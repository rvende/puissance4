#TODO import numpy
from math import inf as infinity
import copy
import numpy as np
import time

#PUISSANCE 5 Grille 12*8

COMP = 1
HUMAN = -1

DEPTH = 2
HEIGHT = 8
WIDTH = 12
# Number of aligned coins to win
CONNECT = 5 

def children_states(state, player):
    turn = player
    children = []
    for i in range(0, WIDTH):
        if hasSpace(state,i) != 0:
            tmp = state.copy()
            addMove(tmp,i, player)
            children.append(tmp)
    return children


#TODO verification sur le dernier mouvement
def eval_win(state, player):

    #Victoire Horizontale
    for i in range(HEIGHT):
        if find(state[i], [player]*CONNECT):
            return player
        if find(state[i], [-player]*CONNECT):
            return -player


    #Victoire Verticale
    for i in range(WIDTH):
        if find(state[:, i], [player]*CONNECT):
            return player
        if find(state[:, i], [-player]*CONNECT):
            return -player

    #Victoire Diagonale
    #diagonale droite
    for i in range(-3,8):
        d = np.diag(state,i)
        if find(d, [player]*CONNECT):
            return player
        if find(d, [-player]*CONNECT):
            return -player

    # diagonale gauche
    stateT = verticalMirror(state)
    for i in range(-3, 8):
        d = np.diag(stateT,i)
        if find(d, [player]*CONNECT):
            return player
        if find(d, [-player]*CONNECT):
            return -player


    for i in range(0,WIDTH):
        if (hasSpace(state,i) != 0):
            return children_states(state, player)
    
    return 0


def generateLeftCheck(player):
    tab = [
        [ player, player, player, player, 0],
        [ player, player, player, 0, 0],
        [ player, player, 0, 0, 0]
    ]
    return tab, [3,2,1]

def generateCenterCheck(player):
    tab = [
        [ 0, player, player, player, player, 0],
        [ -player, player, player, player, player, 0],
        [ 0, player, player, player, player, -player],
        [ 0, player, player, player, 0],
        [ -player, player, player, player, 0, 0],
        [ 0, 0, player, player, player, -player],
        [ player, player, 0, player, player],
        [ player, player, 0, 0, player],
        [ player, 0, 0, player, player],
        [ player, 0, player, 0, player],
        [ player, 0, player, player, player],
        [ player, player, player, 0, player],
        [ 0, 0, player, player, 0],
        [ 0, player, player, 0, 0],
        [ -player, player, player, 0, 0, 0],
        [ 0, 0, 0, player, player, -player]
    ]
    return tab, [4, 4, 4, 3, 3, 3, 4, 3, 3, 3, 4, 4, 2, 2, 2, 2]

def generateRightCheck(player):
    tab = [
        [ 0, player, player, player, player],
        [ 0, 0, player, player, player],
        [ 0, 0, 0, player, player]
    ]
    return tab, [3, 2, 1]

def find(line, subline):
    for i in range(len(line)-len(subline)):
        if np.all( [subline == line[i:i+len(subline)]] ):
            return True
    return False

def eval_global_score(state):
#     return eval_score(state, COMP) - eval_score(state, HUMAN)

# def eval_score(state, player):
    # Find the longest coin chain 
    accu = 0
    height = HEIGHT

    # Horizontale
    tabC, tabC_score = generateCenterCheck(COMP)
    tabL, tabL_score = generateLeftCheck(COMP)
    tabR, tabR_score = generateRightCheck(COMP)

    countEmptyLines = 0

    for i in range(HEIGHT):
        #Center
        nbElement = (state[i] != 0).sum()
        if nbElement > 1:
            for idx in range(len(tabC)): 
                if find(state[i], [ -1*i for i in tabC[idx] ] ):
                    accu -= tabC_score[idx]
                if find(state[i], tabC[idx]):
                    accu += tabC_score[idx]
                    #print("Center")

            #Left
            for idx in range(len(tabL)):
                if np.all( [ tabL[idx] == state[i,0:CONNECT] ] ):
                    accu += tabL_score[idx]
                if np.all( [ [ -1*i for i in tabL[idx] ] == state[i,0:CONNECT] ] ):
                    accu -= tabL_score[idx]
                    #print("Left")

            #Right
            for idx in range(len(tabR)):
                if np.all( [ tabR[idx] == state[i,WIDTH-CONNECT:WIDTH] ] ):
                    accu += tabR_score[idx]
                if np.all( [ [ -1*i for i in tabR[idx] ] == state[i,WIDTH-CONNECT:WIDTH] ] ):
                    accu -= tabR_score[idx]
                    #print("Right")
        elif nbElement == 0:
            countEmptyLines += 1
            if countEmptyLines == 4:
                height = i 
                break

    #print(">>>\n", state)
    if height != HEIGHT:
        state = state[:height, :]
    #print("<<<\n", state)


    leftCol = 0
    rightCol = WIDTH-1
    countEmptyColumn = 0
    emptyColRight = False


    #Vertical
    for i in range(WIDTH):
        nbElement = (state[:, i] != 0).sum()
        if nbElement > 1:
            countEmptyColumn = 0

            for idx in range(len(tabC)): 
                if find(state[:, i], tabC[idx]):
                    accu += tabC_score[idx]
                if find(state[:, i], [ -1*i for i in tabC[idx] ]):
                    accu -= tabC_score[idx]
                    #print("V Center")

            #Bottom
            for idx in range(len(tabL)):
                if np.all( [ tabL[idx] == state[0:CONNECT, i] ] ):
                    accu += tabL_score[idx]
                if np.all( [ [ -1*i for i in tabL[idx] ] == state[0:CONNECT, i] ] ):
                    accu -= tabL_score[idx]
                    #print("V Bottom")
        elif nbElement == 0:
            countEmptyColumn += 1
            if countEmptyColumn >= 4 and i == countEmptyColumn:
                leftCol = i
                break
            elif i == WIDTH-1 and countEmptyColumn >= 4:
                rightCol = WIDTH -1 - countEmptyColumn + 3
        else: 
            countEmptyColumn = 0

    width = rightCol + 1 - leftCol

    if rightCol != WIDTH-1 or leftCol != 0:
        state = state[:, leftCol: rightCol + 1]
    #print("<<<\n", state)

    #Diagonal
    for i in range(CONNECT - height, width - CONNECT + 1):
        d = np.diag(state,i)
        if (d != 0).sum() > 1:

            for idx in range(len(tabC)): 
                if find(d, tabC[idx]):
                    accu += tabC_score[idx]
                if find(d, [ -1*i for i in tabC[idx] ]):
                    accu -= tabC_score[idx]
                    #print("D Center")

            #Bottom
            for idx in range(len(tabL)):
                if np.all( [ tabL[idx] == d[0:CONNECT] ] ):
                    accu += tabL_score[idx]
                if np.all( [ [ -1*i for i in tabL[idx] ] == d[0:CONNECT] ] ):
                    accu -= tabL_score[idx]
                    #print("D Bottom")


    stateT = verticalMirror(state)
    for i in range(CONNECT - height, width - CONNECT + 1):
        d = np.diag(stateT,i)
        if (d != 0).sum() > 1:
            for idx in range(len(tabC)): 
                if find(d, tabC[idx]):
                    accu += tabC_score[idx]
                if find(d, [ -1*i for i in tabC[idx] ]):
                    accu -= tabC_score[idx]
                    #print("DG Center")

            #Bottom
            for idx in range(len(tabL)):
                if np.all( [ tabL[idx] == d[0:CONNECT] ] ):
                    accu += tabL_score[idx]
                if np.all( [ [ -1*i for i in tabL[idx] ] == d[0:CONNECT] ] ):
                    accu -= tabL_score[idx]
                    #print("DG Bottom")

    return accu

Start = np.zeros((HEIGHT,WIDTH))
Tree = {}
Scores = {}

def hasSpace(state, col):
    return (state[:,col] == 0).sum()


def addMove(state, col, player):
    for i in range(5,-1,-1):
        if state[i,col] != 0:
            state[i+1, col] = player
            return
    state[0,col] = player


def human_turn():
    global Start
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
                addMove(Start,move-1, HUMAN)
        except (EOFError, KeyboardInterrupt):
            print('error')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')


def choose_move():
    global Start
    children = eval_win(Start, COMP)
    best = -infinity
    best_index = None
    for c in children:
        if Scores[npToTuple(c)] >= best:
            best = Scores[npToTuple(c)]
            best_index = c
    Start = best_index;


def ai_turn(): 
    global Start, Scores
    print(f'AI turn ["X"]')
    print_board(Start)
    Scores = {}
    t0 = time.time()
    minimax(Start, COMP, DEPTH)
    t1 = time.time()
    print(">>>timer minimax {}".format(t1-t0))
    choose_move()
    print(">>>>timer choose_move {}".format(time.time()-t1))
    print(len(Scores))

def verticalMirror(state):
    return state[:,::-1]

def npToTuple(state):
    return tuple(map(tuple, state))

def tupleToNp(tuple_):
    return np.asarray(tuple_)

compteurMinimax = 0

def minimax(current_state, player, depth):
    global Scores, compteurMinimax

    compteurMinimax += 1

    # if compteurMinimax == 80:
    #     t2 = time.time()
    #     children = eval_win(current_state, player)
    #     print("timer eval_win Mini {}".format(time.time()-t2))
    # else:
    children = eval_win(current_state, player)


    if type(children) == int:
        score = children*infinity
    elif depth == 0:
        #t0 = time.time()
        score = eval_global_score(current_state)
        #print("timer eval_score Mini {}".format(time.time()-t0))
    


    else:
        turn = player
        score = -turn
        for child_state in children:
            if npToTuple(child_state) not in Scores.keys():
                minimax(child_state, -player, depth-1)
            score = max(score,Scores[npToTuple(child_state)]) if turn == COMP else min(score,Scores[npToTuple(child_state)])
    Scores[npToTuple(current_state)] = score
    #print(">>>>", len(Scores)) 
            


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


def main():
    global Start

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
        if(type(eval_win(Start, HUMAN)) == int):
            break
        ai_turn()

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


# TODO : timer 
# TODO : eval_win avec dernier move 
