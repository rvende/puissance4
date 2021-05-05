#TODO import numpy
from math import inf as infinity
import copy
import numpy as np


#PUISSANCE 5 Grille 12*8

COMP = 1
HUMAN = -1

DEPTH = 3
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
    for i in range(0,HEIGHT):
        countSame = 0
        previous = 0
        for j in range(0,WIDTH):
            if state[i,j] == previous and previous != 0:
                countSame+=1
                if countSame == CONNECT-1:
                    return previous
            else :
                countSame = 0
                previous = state[i,j]

    #Victoire Verticale
    for j in range(0,WIDTH):
        countSame = 0
        previous = 0
        for i in range(0,HEIGHT):
            if state[i,j] == previous and previous != 0:
                countSame+=1
                if countSame == CONNECT-1:
                    return previous
            else :
                countSame = 0
                previous = state[i,j]

    #Victoire Diagonale
    #diagonale droite
    for i in range(-4,9):
        d = np.diag(state,i)
        countSame = 0
        previous = 0
        for j in range(0, len(d)):
            if d[j] == previous and previous != 0:
                countSame+=1
                if countSame == CONNECT-1:
                    return previous
            else :
                countSame = 0
                previous = d[j]

    # diagonale gauche
    stateT = verticalMirror(state)
    for i in range(-4,9):
        d = np.diag(stateT,i)
        countSame = 0
        previous = 0
        for j in range(0, len(d)):
            if d[j] == previous and previous != 0:
                countSame+=1
                if countSame == CONNECT-1:
                    return previous
            else :
                countSame = 0
                previous = d[j]


    for i in range(0,WIDTH):
        if (hasSpace(state,i) != 0):
            return None
    return 0


def generateLeftCheck(player):
    tab = [
        [ player, player, player, player, 0],
        [ player, player, player, 0, 0]
    ]
    return tab

def generateCenterCheck(player):
    - OOOO -
    X OOOO -
    - OOOO X


    - OOO-
    X OOO - - 
    - - 000 X

    tab = [
        [ 0, player, player, player, player, 0],
        [ -player, player, player, player, player, 0],
        [ 0, player, player, player, player, -player],
        [ 0, player, player, player, 0],
        [ -player, player, player, player, 0, 0],
        [ 0, 0, player, player, player, -player]
    ]


def generateRightCheck(player):
    tab = [
        [ 0, player, player, player, player],
        [ 0, 0, player, player, player]
    ]
    return tab


def eval_score(state):
    # Find the longest coin chain 
    accu = 0

    # Horizontale 
    for i in range(0,HEIGHT):
        countSame = 0
        previous = 0
        openLeft = False
        for j in range(0,WIDTH):
            print(i, j, previous, countSame)
            if state[i,j] == previous and previous != 0:
                countSame+=1
            elif state[i,j]==0 and countSame != 0:
                accu += countSame + 1
                countSame = 0
            else :
                countSame = 0

            previous = state[i,j]
    return accu

Start = np.zeros((HEIGHT,WIDTH))
Tree = {}
Scores = {}

def hasSpace(state, col):
    return (state[:,col] == 0).sum()


def addMove(state,col, player):
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
    global Start,Scores
    children = eval_win(Start, COMP)
    best = -infinity
    best_index = None
    for c in children:
        result = symmetryInTree(c)
        if Scores[result] > best:
            best = Scores.get(result)
            best_index = c
    Start = best_index;


def ai_turn(): 
    global Start
    print(f'AI turn ["X"]')
    print_board(Start)
    choose_move()

def verticalMirror(state):
    return state[:,::-1]

def symmetryInTree(state):
    if state in Tree:
        return state
    if verticalMirror(state) in Tree:
        return verticalMirror(state)
    return False


def minimax(current_state, player, depth):
    global Scores
    children = eval_win(current_state, player)
    if depth == 0:
        return
    if type(children) == int:
        score = children
    else:
        turn = player
        score = -turn
        for child_state in children:
            result = symmetryInTree(child_state)
            if type(result) == bool:
                minimax(child_state, -player, depth-1)
                score = max(score,Scores[child_state]) if turn == COMP else min(score,Scores[child_state])
            else :
                score = max(score,Scores[result]) if turn == COMP else min(score,Scores[result])
    Tree[current_state] = children
    Scores[current_state] = score


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
    print_board(Start)
    human_turn()
    human_turn()
    human_turn()
    human_turn()
    human_turn()
    print_board(Start)
    print(">>>>", eval_score(Start))

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