import pygame
import os
import datetime

pygame.init()

TILE=22
SIZE=TILE*8

screen=pygame.display.set_mode((SIZE,SIZE))
font=pygame.font.SysFont(None,24)

start_board=[
["bR","bH","bB","bQ","bK","bB","bH","bR"],
["bP","bP","bP","bP","bP","bP","bP","bP"],
["","","","","","","",""],
["","","","","","","",""],
["","","","","","","",""],
["","","","","","","",""],
["wP","wP","wP","wP","wP","wP","wP","wP"],
["wR","wH","wB","wQ","wK","wB","wH","wR"]
]

board=[row[:] for row in start_board]

pieces={}
names=["wB","wH","wK","wP","wQ","wR","bB","bH","bK","bP","bQ","bR"]

for n in names:
    pieces[n]=pygame.image.load("graphics/"+n+".gif")

wTile=pygame.image.load("graphics/wTile.png")
bTile=pygame.image.load("graphics/bTile.png")
sTile=pygame.image.load("graphics/sTile.png")

selected=None
moves=[]
turn="w"
winner=None

history=[]
letters="abcdefgh"

def square(r,c):
    return letters[c]+str(8-r)

def inside(r,c):
    return 0<=r<8 and 0<=c<8

def line_moves(r,c,dirs):
    m=[]
    for dr,dc in dirs:
        nr=r+dr
        nc=c+dc
        while inside(nr,nc):
            if board[nr][nc]=="":
                m.append((nr,nc))
            else:
                if board[nr][nc][0]!=board[r][c][0]:
                    m.append((nr,nc))
                break
            nr+=dr
            nc+=dc
    return m

def pawn_moves(r,c,color):

    m=[]

    d=-1 if color=="w" else 1
    start=6 if color=="w" else 1

    if inside(r+d,c) and board[r+d][c]=="":
        m.append((r+d,c))

        if r==start and board[r+2*d][c]=="":
            m.append((r+2*d,c))

    for dc in [-1,1]:

        nr=r+d
        nc=c+dc

        if inside(nr,nc):

            if board[nr][nc]!="" and board[nr][nc][0]!=color:
                m.append((nr,nc))

    return m

def get_moves(r,c):

    piece=board[r][c]
    if piece=="":
        return []

    color=piece[0]
    t=piece[1]

    m=[]

    if t=="P":
        m+=pawn_moves(r,c,color)

    if t=="H":
        for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr=r+dr
            nc=c+dc
            if inside(nr,nc):
                if board[nr][nc]=="" or board[nr][nc][0]!=color:
                    m.append((nr,nc))

    if t=="B":
        m+=line_moves(r,c,[(1,1),(1,-1),(-1,1),(-1,-1)])

    if t=="R":
        m+=line_moves(r,c,[(1,0),(-1,0),(0,1),(0,-1)])

    if t=="Q":
        m+=line_moves(r,c,[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)])

    if t=="K":
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr!=0 or dc!=0:
                    nr=r+dr
                    nc=c+dc
                    if inside(nr,nc):
                        if board[nr][nc]=="" or board[nr][nc][0]!=color:
                            m.append((nr,nc))

    return m

def find_king(color):
    for r in range(8):
        for c in range(8):
            if board[r][c]==color+"K":
                return (r,c)

def in_check(color):

    kr,kc=find_king(color)
    enemy="b" if color=="w" else "w"

    for r in range(8):
        for c in range(8):

            if board[r][c]!="" and board[r][c][0]==enemy:

                if (kr,kc) in get_moves(r,c):
                    return True

    return False

def legal_moves(r,c):

    color=board[r][c][0]
    m=get_moves(r,c)

    good=[]

    for nr,nc in m:

        saved=board[nr][nc]

        board[nr][nc]=board[r][c]
        board[r][c]=""

        if not in_check(color):
            good.append((nr,nc))

        board[r][c]=board[nr][nc]
        board[nr][nc]=saved

    return good

def has_moves(color):

    for r in range(8):
        for c in range(8):

            if board[r][c]!="" and board[r][c][0]==color:

                if legal_moves(r,c):
                    return True

    return False

def pgn_piece(piece):

    table={
    "P":"",
    "R":"R",
    "H":"N",
    "B":"B",
    "Q":"Q",
    "K":"K"
    }

    return table[piece[1]]

def save_pgn():

    if not os.path.exists("games"):
        os.makedirs("games")

    i=0
    while os.path.exists(f"games/game{i}.pgn"):
        i+=1

    path=f"games/game{i}.pgn"

    result="1-0" if winner=="white wins" else "0-1"

    header=f'''[Event "Local Game"]
[Site "Local"]
[Date "{datetime.date.today()}"]
[White "White"]
[Black "Black"]
[Result "{result}"]

'''

    moves=""
    n=1

    for i in range(0,len(history),2):

        moves+=str(n)+". "+history[i]+" "

        if i+1<len(history):
            moves+=history[i+1]+" "

        n+=1

    moves+=result

    with open(path,"w") as f:
        f.write(header+moves)

running=True

while running:

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.MOUSEBUTTONDOWN and winner is None:

            x,y=pygame.mouse.get_pos()

            col=x//TILE
            row=y//TILE

            if selected is None:

                piece=board[row][col]

                if piece!="" and piece[0]==turn:
                    selected=(row,col)
                    moves=legal_moves(row,col)

            else:

                if (row,col) in moves:

                    r,c=selected

                    piece=board[r][c]
                    target=board[row][col]

                    board[row][col]=piece
                    board[r][c]=""

                    move=pgn_piece(piece)

                    if target!="":
                        move+= "x"

                    move+=square(row,col)

                    history.append(move)

                    turn="b" if turn=="w" else "w"

                    if in_check(turn) and not has_moves(turn):

                        history[-1]+="#"

                        winner="white wins" if turn=="b" else "black wins"
                        save_pgn()

                    elif in_check(turn):

                        history[-1]+="+"

                selected=None
                moves=[]

    for r in range(8):
        for c in range(8):

            if (r,c) in moves:
                screen.blit(sTile,(c*TILE,r*TILE))
            else:
                if (r+c)%2==0:
                    screen.blit(wTile,(c*TILE,r*TILE))
                else:
                    screen.blit(bTile,(c*TILE,r*TILE))

            p=board[r][c]

            if p!="":
                screen.blit(pieces[p],(c*TILE+1,r*TILE+1))

    if winner:

        text=font.render(winner,True,(255,0,0))
        rect=text.get_rect(center=(SIZE//2,SIZE//2))
        screen.blit(text,rect)

    pygame.display.flip()

pygame.quit()
