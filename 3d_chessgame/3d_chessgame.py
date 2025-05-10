import pygame
import sys
import random
from itertools import permutations, product

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800    # Window width and height
BOARD_SIZE = 8                            # Number of cells per row/column
CELL_SIZE = 80                            # Base pixel size of each cell
LEVEL_COUNT = 3                           # Number of stacked board levels (3D)

# Color definitions
BG_COLOR     = (18, 18, 18)
DARK1        = (40, 40, 40)              
DARK2        = (60, 60, 60)              
HIGHLIGHT    = (50, 200, 50, 120)         
SELECTED     = (200, 50, 50, 180)        
WHITE        = (230, 230, 230)           
BLACK        = (10, 10, 10)              
RED          = (255, 0, 0)                
BORDER_COLOR = (255, 255, 0)              
CAPTURED_BG  = (30, 30, 30)               

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Chess – Dark Mode")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 24)     


# Symbol mapping:
PIECE_SYMBOLS = {
    'Rook':   '[#]',
    'Knight': '/\\',
    'Bishop': '<^>',
    'Queen':  '(Q)',
    'King':   '<K>',
    'Pawn':   ' o ',
}

# Vector3: Represents x,y,z coordinates on the 3D board
class Vector3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def __add__(self, other):
        return Vector3(self.x + other.x,
                       self.y + other.y,
                       self.z + other.z)
    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)
    def in_bounds(self):
        return (0 <= self.x < BOARD_SIZE and
                0 <= self.y < BOARD_SIZE and
                0 <= self.z < LEVEL_COUNT)


# Piece base class with ASCII symbol property
class Piece:
    def __init__(self, color, pos):
        self.color = color    # 'white' or 'black'
        self.pos = pos        # Instance of Vector3
    @property
    def symbol(self):
        return PIECE_SYMBOLS[self.__class__.__name__]
    def get_moves(self, board):
        return []


# Rook: Straight-line moves along axes
class Rook(Piece):
    def get_moves(self, board):
        moves = []
        for d in [Vector3(1,0,0), Vector3(-1,0,0), Vector3(0,1,0), Vector3(0,-1,0), Vector3(0,0,1), Vector3(0,0,-1)]:
            p = Vector3(self.pos.x, self.pos.y, self.pos.z)
            while True:
                p += d
                if not p.in_bounds(): break
                t = board.get_piece(p)
                if t is None:
                    moves.append(Vector3(p.x,p.y,p.z))
                else:
                    if t.color != self.color: moves.append(Vector3(p.x,p.y,p.z))
                    break
        return moves


# Bishop: Diagonal moves
class Bishop(Piece):
    def get_moves(self, board):
        moves, dirs = [], []
        for dx in (-1,1):
            for dy in (-1,1): dirs.append(Vector3(dx,dy,0))
            for dz in (-1,1): dirs.extend([Vector3(dx,0,dz), Vector3(0,dx,dz)])
        for d in dirs:
            p = Vector3(self.pos.x, self.pos.y, self.pos.z)
            while True:
                p += d
                if not p.in_bounds(): break
                t = board.get_piece(p)
                if t is None:
                    moves.append(Vector3(p.x,p.y,p.z))
                else:
                    if t.color != self.color: moves.append(Vector3(p.x,p.y,p.z))
                    break
        return moves


# Queen: Combines Rook & Bishop
class Queen(Piece):
    def get_moves(self, board):
        return Rook(self.color,self.pos).get_moves(board) + Bishop(self.color,self.pos).get_moves(board)


# Knight: L-shaped moves
class Knight(Piece):
    def get_moves(self, board):
        moves=[]; steps=[2,1,0]
        for dx,dy,dz in set(permutations(steps)):
            if (dx==dy==0) or (dx==dz==0) or (dy==dz==0): continue
            for sx,sy,sz in product((1,-1),repeat=3):
                p=Vector3(self.pos.x+sx*dx, self.pos.y+sy*dy, self.pos.z+sz*dz)
                if p.in_bounds():
                    t=board.get_piece(p)
                    if t is None or t.color!=self.color: moves.append(p)
        return moves


# King: One-step all directions
class King(Piece):
    def get_moves(self, board):
        moves=[]
        for dx,dy,dz in product((-1,0,1),repeat=3):
            if dx==dy==dz==0: continue
            p=Vector3(self.pos.x+dx, self.pos.y+dy, self.pos.z+dz)
            if p.in_bounds():
                t=board.get_piece(p)
                if t is None or t.color!=self.color: moves.append(p)
        return moves


# Pawn: Forward & diagonal captures
class Pawn(Piece):
    def get_moves(self, board):
        moves=[]; d=-1 if self.color=='white' else 1
        f=Vector3(self.pos.x, self.pos.y+d, self.pos.z)
        if f.in_bounds() and board.get_piece(f) is None: moves.append(f)
        for dx in(-1,1):
            p=Vector3(self.pos.x+dx, self.pos.y+d, self.pos.z)
            if p.in_bounds():
                t=board.get_piece(p)
                if t and t.color!=self.color: moves.append(p)
        return moves


# Board: Manages grid, setup, and rendering 3D layers
class Board:
    def __init__(self):
        # Initialize empty 3D grid
        self.grid = [[[None]*BOARD_SIZE for _ in range(BOARD_SIZE)] for __ in range(LEVEL_COUNT)]
        self.setup_pieces()  # Populate with starting pieces

    def setup_pieces(self):
        # Place back rank and pawns for white and black
        back=[Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
        for i,cls in enumerate(back):
            self.grid[0][7][i] = cls('white', Vector3(i,7,0))  # White back row
            self.grid[2][0][i] = cls('black', Vector3(i,0,2))  # Black back row
        for i in range(BOARD_SIZE):
            self.grid[0][6][i] = Pawn('white', Vector3(i,6,0))  # White pawns
            self.grid[2][1][i] = Pawn('black', Vector3(i,1,2))  # Black pawns

    def get_piece(self, pos):
        # Return piece at given 3D coordinate or None
        return self.grid[pos.z][pos.y][pos.x]

    def move_piece(self, p, d):
        # Move piece p to destination d, return any captured piece
        self.grid[p.pos.z][p.pos.y][p.pos.x] = None
        cap = self.grid[d.z][d.y][d.x]
        self.grid[d.z][d.y][d.x] = p
        p.pos = d
        return cap

    def draw_3d(self, surf, view, sel=None, high=None):
        # Draw visible levels of the board in perspective
        high = high or []
        scales = [1.0,0.8,0.6]  # Scale factor per level
        offs   = [0,-60,-120]   # Vertical offset per level
        cx     = SCREEN_WIDTH//2

        for z in range(view):
            size  = CELL_SIZE * scales[z]
            board_px = BOARD_SIZE * size
            ox, oy   = cx-board_px/2, SCREEN_HEIGHT//2-board_px/2+offs[z]

            # Draw level label
            surf.blit(FONT.render(f"Level {z}", True, WHITE), (ox, oy-30))

            # Draw each square, highlight, and piece
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    r = pygame.Rect(ox+x*size, oy+y*size, size, size)
                    pygame.draw.rect(surf, DARK1 if (x+y)%2==0 else DARK2, r)

                    # Highlight selected square
                    if sel and sel.pos == Vector3(x,y,z):
                        sfc = pygame.Surface((size,size),pygame.SRCALPHA)
                        sfc.fill(SELECTED)
                        surf.blit(sfc, r.topleft)

                    # Highlight legal moves
                    if Vector3(x,y,z) in high:
                        sfc = pygame.Surface((size,size),pygame.SRCALPHA)
                        sfc.fill(HIGHLIGHT)
                        surf.blit(sfc, r.topleft)

                    # Draw piece symbol if present
                    p = self.grid[z][y][x]
                    if p:
                        col = WHITE if p.color=='white' else BLACK
                        surf.blit(FONT.render(p.symbol, True, col), (r.x+size*0.3, r.y+size*0.3))

            # Draw border
            pygame.draw.rect(surf, BORDER_COLOR, pygame.Rect(ox,oy,board_px,board_px), 3)


# Game: Handles input, AI, rendering, and main loop
class Game:
    def __init__(self):
        # Initialize game state
        self.board    = Board()
        self.turn     = 'white'            # Current player
        self.sel      = None               # Selected piece
        self.high     = []                 # Highlighted moves
        self.view     = LEVEL_COUNT        # Number of visible levels
        self.cap      = {'white': [], 'black': []}  # Captured pieces
        self.mode     = 'PVP'              # 'PVP' or 'AI'

    def switch_mode(self, key):
        # Toggle between AI and PVP or change layer view
        if key == pygame.K_0:
            self.mode = 'AI'
            print("Mode: Single Player (AI)")
            if self.turn == 'black': self.ai_move()
        elif key == pygame.K_9:
            self.mode = 'PVP'
            print("Mode: Two Player")
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.view = key - pygame.K_1 + 1
            print(f"Visible levels: 0 to {self.view-1}")

    def handle_click(self, pos):
        # Process piece selection and movement
        if self.mode == 'AI' and self.turn == 'black': return
        coord = self.screen_to_board(*pos)
        if not coord: return
        p = self.board.get_piece(Vector3(*coord))

        if self.sel:
            # Attempt move to highlighted square
            if Vector3(*coord) in self.high:
                cap = self.board.move_piece(self.sel, Vector3(*coord))
                if cap: self.cap[cap.color].append(cap)
                if isinstance(cap, King):
                    print(f"Game Over! {self.sel.color.capitalize()} wins.")
                    pygame.quit(); sys.exit()
                self.turn = 'black' if self.turn=='white' else 'white'
                if self.mode=='AI' and self.turn=='black': self.ai_move()
            # Clear selection
            self.sel, self.high = None, []
        elif p and p.color == self.turn:
            # Select piece and calculate its moves
            self.sel  = p
            self.high = p.get_moves(self.board)

    def ai_move(self):
        # Random-move AI logic for black
        moves = []
        for z in range(LEVEL_COUNT):
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    p = self.board.get_piece(Vector3(x,y,z))
                    if p and p.color=='black':
                        for m in p.get_moves(self.board): moves.append((p,m))
        if not moves: return
        piece, move = random.choice(moves)
        cap = self.board.move_piece(piece, move)
        if cap: self.cap[cap.color].append(cap)
        if isinstance(cap, King): pygame.quit(); sys.exit()
        self.turn = 'white'

    def screen_to_board(self, mx, my):
        # Convert mouse coords to board cell + level
        scales = [1.0,0.8,0.6]; offs=[0,-60,-120]; cx=SCREEN_WIDTH//2
        for z in range(self.view-1, -1, -1):
            size = CELL_SIZE * scales[z]
            bp   = BOARD_SIZE * size
            ox, oy = cx - bp/2, SCREEN_HEIGHT//2 - bp/2 + offs[z]
            if ox <= mx < ox+bp and oy <= my < oy+bp:
                return (int((mx-ox)//size), int((my-oy)//size), z)
        return None

    def draw_captured(self):
        # Draw side panels for captured pieces
        screen.fill(CAPTURED_BG, (0,0,100,SCREEN_HEIGHT))
        screen.blit(FONT.render("White Captured", True, WHITE), (10,10))
        for i,p in enumerate(self.cap['white']):
            screen.blit(FONT.render(p.symbol, True, WHITE), (10,40+i*20))
        x1 = SCREEN_WIDTH - 100
        screen.fill(CAPTURED_BG, (x1,0,100,SCREEN_HEIGHT))
        screen.blit(FONT.render("Black Captured", True, RED), (x1+10,10))
        for i,p in enumerate(self.cap['black']):
            screen.blit(FONT.render(p.symbol, True, RED), (x1+10,40+i*20))

    def draw(self):
        # Full render cycle: background, mode, board, captures, controls
        screen.fill(BG_COLOR)
        mode_text = f"Mode: {'Single Player (AI)' if self.mode=='AI' else 'Two Player'}"
        mode_surf = FONT.render(mode_text, True, WHITE)
        screen.blit(mode_surf, ((SCREEN_WIDTH-mode_surf.get_width())//2, 10))
        self.board.draw_3d(screen, self.view, self.sel, self.high)
        self.draw_captured()
        ctrl_surf = FONT.render("Layers:1,2,3 | 0=AI,9=2P", True, WHITE)
        screen.blit(ctrl_surf, ((SCREEN_WIDTH-ctrl_surf.get_width())//2, SCREEN_HEIGHT-30))
        pygame.display.flip()

    def run(self):
        # Main game loop: event handling and drawing
        print("Controls: Click to move. 1–3 change layers. 0=AI, 9=2P.")
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(), sys.exit()
                elif e.type == pygame.KEYDOWN: self.switch_mode(e.key)
                elif e.type == pygame.MOUSEBUTTONDOWN: self.handle_click(e.pos)
            self.draw()
            clock.tick(30)

if __name__ == "__main__":
    Game().run()
