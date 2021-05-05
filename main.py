#TODO import numpy
from math import inf as infinity
import copy
import numpy as np


#PUISSANCE 5 Grille 12*8

COMP = 1
HUMAN = -1

def children_states(state, player):
    turn = player
    children = []
    for i in range(0,7):
        if hasSpace(state,i) != 0:
            tmp = state.copy()
            addMove(tmp,i, player)
            children.append(tmp)
    return children


#TODO verification sur le dernier mouvement
def eval_win(state, player):
    #Victoire Horizontale
    for i in range(0,6):
        countSame = 0
        previous = 0
        for j in range(0,7):
            if state[i,j] == previous and previous != 0:
                countSame+=1
                if countSame == 3:
                    return previous
            else :
                countSame = 0
                previous = state[i,j]

    #Victoire Verticale
    for j in range(0,7):
        countSame = 0
        previous = 0
        for i in range(0,6):
            if state[i,j] == previous and previous != 0:
                countSame+=1
                if countSame == 3:
                    return previous
            else :
                countSame = 0
                previous = state[i,j]

    #Victoire Diagonale
    #diagonale qui part de (2,0), (1,0), (0,0)
    for i in range(-2,6):
        d = np.diag(state,i)
        countSame = 0
        previous = 0
        for j in range(0,len(d)):
            if d[j] == previous and previous != 0:
                countSame+=1
                if countSame == 3:
                    return previous
            else :
                countSame = 0
                previous = d[j]

    for i in range(0,7):
        if (hasSpace(state,i) != 0):
            return None
    return 0


Start = np.zeros((6,7))
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

    while move < 1 or move > 7:
        try:
            move = int(input('Choose column (1-7): '))
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


def minimax(current_state, player):
    global Scores
    children = eval_win(current_state, player)
    if type(children) == int:
        score = children
    else:
        turn = player
        score = -turn
        for child_state in children:
            result = symmetryInTree(child_state)
            if type(result) == bool:
                minimax(child_state, -player)
                score = max(score,Scores[child_state]) if turn == COMP else min(score,Scores[child_state])
            else :
                score = max(score,Scores[result]) if turn == COMP else min(score,Scores[result])
    Tree[current_state] = children
    Scores[current_state] = score


def print_board(state):
    print("*****************************")
    for x in range(5,-1,-1):
        s = "|"
        for y in range(0,7):
            if state[x,y] == 0:
                s+="   "
            elif state[x,y] == COMP :
                s+=" X "
            else:
                s+=" O "
            s+="|"
        print(s)
        print("*****************************")
    print("")


def main():
    global Start
    Tree[Start] = 0
    print(Tree)
    print_board(Start)
    addMove(Start,0,HUMAN)
    addMove(Start,0,HUMAN)
    addMove(Start,0,HUMAN)
    addMove(Start,0,HUMAN)
    addMove(Start,0,HUMAN)
    addMove(Start,0,HUMAN)
    print_board(Start)
    clist = children_states(Start,COMP)
    print("children")
    for c in clist:
        print_board(c)



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