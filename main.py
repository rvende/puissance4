#TODO import numpy
from math import inf as infinity
import copy
import numpy as np

COMP = 1
HUMAN = -1

def children_states(state, player):
    pass

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
        d = np.diag(Start,i)
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
        if (hasSpace(i) != 0):
            return None
    return 0


Start = np.zeros((6,7))
Tree = {}
Scores = {}

def score(state):
    if wins(state, COMP):
        score = +1
        #print("Computer win")
    elif wins(state, HUMAN):
        score = -1
        #print("Human win")
    else:
        score = 0
        #print("NULL")

    return score

def hasSpace(col):
    global Start
    return (Start[:,col] == 0).sum()


def addMove(col, player):
    global Start
    for i in range(5,-1,-1):
        if Start[i,col] != 0:
            Start[i+1, col] = player
            return
    Start[0,col] = player


def human_turn():
    global Start
    move = -1
    print(f'Human turn ["O"]')
    print_board()

    while move < 1 or move > 7:
        try:
            move = int(input('Choose column (1-7): '))
            can_move = (hasSpace(move-1) != 0)

            if not can_move:
                print('Bad move')
                move = -1
            else:
                addMove(move-1, HUMAN)
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
    global board
    print(f'AI turn ["X"]')
    print_board()
    choose_move()

def verticalMirror(state):
    return (state[2],state[1],state[0],state[5],state[4],state[3],state[8],state[7],state[6])

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


def print_board():
    global Start
    print("*****************************")
    for x in range(5,-1,-1):
        s = "|"
        for y in range(0,7):
            if Start[x,y] == 0:
                s+="   "
            elif Start[x,y] == COMP :
                s+=" X "
            else:
                s+=" O "
            s+="|"
        print(s)
        print("*****************************")
    print("")


def main():
    print_board()
    human_turn()
    addMove(0,HUMAN)
    addMove(1,COMP)
    addMove(1,HUMAN)
    addMove(2,COMP)
    addMove(2,COMP)
    addMove(2,HUMAN)
    addMove(3,COMP)
    addMove(3,COMP)
    addMove(3,COMP)
    addMove(3,HUMAN)
    print_board()
    print("result : ", eval_win(Start,HUMAN))
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
    print_board();
    score = eval_win(Start, COMP)
    if score == 1:
        print("AI win")
    elif score == -1:
        print("Human win")
    else:
        print("draw")

if __name__ == '__main__':
    main()