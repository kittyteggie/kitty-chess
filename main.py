import pygame
import subprocess
import os
import datetime

pygame.init()

TILE = 22
SIZE = TILE*8

screen = pygame.display.set_mode((SIZE,SIZE))
font = pygame.font.SysFont(None,24)

letters="abcdefgh"

engine = subprocess.Popen(
    ["stockfish"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

def send(cmd):
    engine.stdin.write(cmd+"\n")
    engine.stdin.flush()

def read():
    return engine.stdout.readline().strip()

send("uci")
while True:
    if read()=="uciok":
        break

send("setoption name Skill Level value 0")

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
                return r,c

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

    piece=board[r][c]
    if piece=="":
        return []

    color=piece[0]

    m=get_moves(r,c)
    good=[]

    for nr,nc in m:

        saved=board[nr][nc]

        board[nr][nc]=piece
        board[r][c]=""

        if not in_check(color):
            good.append((nr,nc))

        board[r][c]=piece
        board[nr][nc]=saved

    return good

def has_moves(color):

    for r in range(8):
        for c in range(8):
            if board[r][c]!="" and board[r][c][0]==color:
                if legal_moves(r,c):
                    return True
    return False

def get_stockfish_move():

    moves=" ".join(history)

    if moves=="":
        send("position startpos")
    else:
        send("position startpos moves "+moves)

    send("go movetime 100")

    while True:

        line=read()

        if line.startswith("bestmove"):

            move=line.split()[1]

            if move=="(none)":
                return None

            return move

def move_from_uci(m):

    c1=letters.index(m[0])
    r1=8-int(m[1])

    c2=letters.index(m[2])
    r2=8-int(m[3])

    return r1,c1,r2,c2

running=True

while running:

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.MOUSEBUTTONDOWN and turn=="w" and winner is None:

            x,y=pygame.mouse.get_pos()

            col=x//TILE
            row=y//TILE

            if selected is None:

                piece=board[row][col]

                if piece!="" and piece[0]=="w":
                    selected=(row,col)
                    moves=legal_moves(row,col)

            else:

                if (row,col) in moves:

                    r,c=selected

                    piece=board[r][c]

                    board[row][col]=piece
                    board[r][c]=""

                    move=square(r,c)+square(row,col)

                    history.append(move)

                    if in_check("b") and not has_moves("b"):
                        winner="white wins"

                    elif not has_moves("b"):
                        winner="stalemate"

                    turn="b"

                selected=None
                moves=[]

    if turn=="b" and winner is None:

        pygame.event.pump()

        m=get_stockfish_move()

        if m is None:
            winner="draw"

        else:

            r1,c1,r2,c2=move_from_uci(m)

            piece=board[r1][c1]

            board[r2][c2]=piece
            board[r1][c1]=""

            history.append(m)

            if in_check("w") and not has_moves("w"):
                winner="black wins"

            elif not has_moves("w"):
                winner="stalemate"

            turn="w"

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

send("quit")

pygame.quit()
