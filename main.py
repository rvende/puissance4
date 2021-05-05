#TODO import numpy
from math import inf as infinity
import copy
import numpy as np


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
        [player, player, 0, 0, 0]
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
        [player, player, 0, player, player],
        [player, player, 0, 0, player],
        [player, 0, 0, player, player],
        [player, 0, player, 0, player],
        [player, 0, player, player, player],
        [ player, player, player, 0, player],
        [0, 0, player, player, 0],
        [0, player, player, 0, 0],
        [-player, player, player, 0, 0, 0],
        [0, 0, 0, player, player, -player]
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
    return eval_score(state, COMP) - eval_score(state, HUMAN)

def eval_score(state, player):
    # Find the longest coin chain 
    accu = 0

    # Horizontale
    tabC, tabC_score = generateCenterCheck(player)
    tabL, tabL_score = generateLeftCheck(player)
    tabR, tabR_score = generateRightCheck(player)

    for i in range(HEIGHT):
        #Center
        for idx in range(len(tabC)): 
            if find(state[i], tabC[idx]):
                accu += tabC_score[idx]
                #print("Center")

        #Left
        for idx in range(len(tabL)):
            if np.all( [ tabL[idx] == state[i,0:CONNECT] ] ):
                accu += tabL_score[idx]
                #print("Left")

        #Right
        for idx in range(len(tabR)):
            if np.all( [ tabR[idx] == state[i,WIDTH-CONNECT:WIDTH] ] ):
                accu += tabR_score[idx]
                #print("Right")

    #Vertical
    for i in range(WIDTH):
        for idx in range(len(tabC)): 
            if find(state[:, i], tabC[idx]):
                accu += tabC_score[idx]
                #print("V Center")

        #Bottom
        for idx in range(len(tabL)):
            if np.all( [ tabL[idx] == state[0:CONNECT, i] ] ):
                accu += tabL_score[idx]
                #print("V Bottom")

        #Up
        for idx in range(len(tabR)):
            if np.all( [ tabR[idx] == state[HEIGHT-CONNECT:HEIGHT, i] ] ):
                accu += tabR_score[idx]
                #print("V Up")

    #Diagonal
    for i in range(-3,8):
        d = np.diag(state,i)
        for idx in range(len(tabC)): 
            if find(d, tabC[idx]):
                accu += tabC_score[idx]
                #print("D Center")

        #Bottom
        for idx in range(len(tabL)):
            if np.all( [ tabL[idx] == d[0:CONNECT] ] ):
                accu += tabL_score[idx]
                #print("D Bottom")

        #Up
        for idx in range(len(tabR)):
            if np.all( [ tabR[idx] == d[len(d)-CONNECT:len(d)] ] ):
                accu += tabR_score[idx]
                #print("D Up")


    stateT = verticalMirror(state)
    for i in range(-3, 8):
        d = np.diag(stateT,i)
        for idx in range(len(tabC)): 
            if find(d, tabC[idx]):
                accu += tabC_score[idx]
                #print("DG Center")

        #Bottom
        for idx in range(len(tabL)):
            if np.all( [ tabL[idx] == d[0:CONNECT] ] ):
                accu += tabL_score[idx]
                #print("DG Bottom")

        #Up
        for idx in range(len(tabR)):
            if np.all( [ tabR[idx] == d[len(d)-CONNECT:len(d)] ] ):
                accu += tabR_score[idx]
                #print("DG Up")

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
    minimax(Start, COMP, DEPTH)
    choose_move()
    print(len(Scores))

def verticalMirror(state):
    return state[:,::-1]

# def symmetryInTree(state):
#     if state in Tree:
#         return state
#     if verticalMirror(state) in Tree:
#         return verticalMirror(state)
#     return False

def npToTuple(state):
    return tuple(map(tuple, state))

def tupleToNp(tuple_):
    return np.asarray(tuple_)

def minimax(current_state, player, depth):
    global Scores

    children = eval_win(current_state, player)

    if type(children) == int:
        score = children*infinity
    elif depth == 0:
        score = eval_global_score(current_state)
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
    print("")


def main():
    global Start
    # Tree[Start] = 0
    # print(Tree)
    #print_board(Start)
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # human_turn()
    # #addMove(Start, 10, COMP)
    # print_board(Start)
    # print(eval_score(Start))

    # clist = children_states(Start,COMP)
    # print("children")
    # for c in clist:
    #     print_board(c)



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