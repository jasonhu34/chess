"""
Chess brother
"""
from typing import Union

class Board:
    def __init__(self):
        # Instantiate player pieces
        pieces = [Rook, Bishop, Knight, Queen, King, Knight, Bishop, Rook]
        self.black_pieces = [x(False, (0, y)) for x,y in zip(pieces, [x for x in range(8)])] + [Pawn(False, (1, x)) for x in range(8)]
        self.white_pieces = [x(True, (7, y)) for x,y in zip(pieces, [x for x in range(8)])] + [Pawn(True, (6, x)) for x in range(8)]

        # 2D array representing the chess board at move 0
        self.chess_board = [["-" for x in range(8)] for y in range(8)]
        self.chess_board[0] = self.black_pieces[:8]
        self.chess_board[1] = self.black_pieces[8:]
        self.chess_board[6] = self.white_pieces[8:]
        self.chess_board[7] = self.white_pieces[:8]
        
        # List containing the moves taken during the game, format is '[Piece: Piece][Initial space: tuple][Terminal space: tuple]'
        self.moves = []
        # True for white, False for black
        self.turn = True
    
    def convert_space_to_array_index(self, move):
        def char_range(c1, c2):
            """Generates the characters from `c1` to `c2`, inclusive."""
            for c in range(ord(c1), ord(c2)+1):
                yield chr(c)
                
        # ['a'-'h'][1-8] -> [0-7][0-7]
        row = {x:y for x,y in zip([a for a in char_range('a','i')], [b for b in range(7, -1, -1)])}
        column = {x:y for x,y in zip([a for a in range(1, 9)], [b for b in range(8)])}
        return row[move[0]], column[move[1]]

    def display_board(self) -> None:
        for x in self.chess_board:
            for y in x:
                print(y, end=" ")
            print()
    
    def get_space(self, x: int, y: int) -> Union[object, str]:
        # return the chess piece at space xy if space is valid, else return '-'  
        if not self.space_in_bounds((x, y)):
            return ""
        
        return self.chess_board[x][y]
    
    def ply(self):
        """
        Set next player to move, perform Piece.move()
        """
        pass

    def space_in_bounds(self, space: tuple) -> bool:
        if 0 <= space[0] <= 7 and 0 <= space[1] <= 7:
            return True
        return False

class Piece:
    def __init__(self, color, space):
        # True for white, False for black
        self.colour = color
        # tuple
        self.space = space
        self.possible_moves = {}
    
    def move(self, board: Board, ply: str) -> None:
        # move/capture to space on board
        # need to implement turns in this functions as well what to do with an invalid ply input

        ply_array = board.convert_space_to_array_index(ply)
        if ply_array in self.possible_moves:
            if self.possible_moves[ply_array] != '-':
                if self.colour:
                    board.black_pieces.remove(self)
                else:
                    board.white_pieces.remove(self)
            self.space = ply_array
            board.chess_board[ply_array[0]][ply_array[1]] = self
        else:
            return None
    
    # Comparing Piece objects, only other comparison is '-' return false in this case
    def __eq__(self, __value: Union[object, str]) -> Union[object, bool]:
        if type(__value) == str:
            return False
        else:
            if self.space == __value.space and self.colour == __value.colour:
                return True
            return False    

class Pawn(Piece):

    def __str__(self):
        return 'p'
    
    def __repr__(self):
        return 'p'

    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

        # Consider a1 to be the bottom left, then white moves towards list row 0 and black moves towards list row 7
        direction = None
        start_row = None
        if self.colour == True:
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1

        # Check if the space in front of the pawn is empty
        if board.get_space(self.space[0]+direction, self.space[1]) == '-':
            self.possible_moves[self.space[0]+direction, self.space[1]] = '-'
            
            # If at starting position, then check if two spaces in front is empty
            if self.space[0] == start_row:
                if board.get_space(self.space[0]+direction*2, self.space[1]) == '-':
                    self.possible_moves[self.space[0]+direction*2, self.space[1]] = '-'
        
        # Capturable pieces
        for y in [-1, 1]:
            # Validate space
            if board.get_space(self.space[0]+direction, self.space[1]+y):
                # Check if the opponent's piece is on the space
                if board.get_space(self.space[0]+direction, self.space[1]+y) != '-' and board.get_space(self.space[0]+direction, self.space[1]+y).colour != self.colour:
                    self.possible_moves[self.space[0]+direction, self.space[1]+y] = board.get_space(self.space[0]+direction, self.space[1]+y)

        # En passent
        # Check if board moves is non-empty (subscriptable)
        if board.moves:
            if type(board.moves[-1][0]) == Pawn:
                initial_space = board.convert_space_to_array_index(board.moves[-1][1])
                terminal_space = board.convert_space_to_array_index(board.moves[-1][2])
                # Check if pawn moved two spaces
                if abs(initial_space[0]-terminal_space[0]) == 2:

                    # NEED TO CHECK IF THIS WORKS
                    if board.get_space(terminal_space[0], terminal_space[1]-1) is self:
                        self.possible_moves[terminal_space[0]+direction, terminal_space[1]-1] = board.get_space(terminal_space)
                    elif board.get_space(terminal_space[0], terminal_space[1]+1) is self:
                        self.possible_moves[terminal_space[0]+direction, terminal_space[1]+1] = board.get_space(terminal_space)

        # need to implement pawn promotion

class Rook(Piece):
    
    def __str__(self):
        return 'r'

    def __repr__(self):
        return 'r'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        directions = [(0,1), (0,-1), (1,0), (-1,0)]

        # check empty spaces in the cardinal directions
        for direction in directions:
            x = self.space[0] + direction[0]
            y = self.space[1] + direction[1]

            # Stop checking a direction if a piece is hit or out-of-bounds
            while(board.get_space(x, y) == '-'):
                self.possible_moves[(x, y)] = board.get_space(x, y)
                x += direction[0]
                y += direction[1]
            
            # Hit an opponents piece
            if board.get_space(x, y):
                if board.get_space(x, y).colour != self.colour:
                    self.possible_moves[(x, y)] = board.get_space(x, y)

class Bishop(Piece):
    
    def __str__(self):
        return 'b'
    
    def __repr__(self):
        return 'b'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        directions = [(1,1), (1,-1), (-1,-1), (-1,1)]

        # check empty spaces in the cardinal directions
        for direction in directions:
            x = self.space[0] + direction[0]
            y = self.space[1] + direction[1]

            # Stop checking a direction if a piece is hit or out-of-bounds
            while(board.get_space(x, y) == '-'):
                self.possible_moves[(x, y)] = board.get_space(x, y)
                x += direction[0]
                y += direction[1]
            
            # Hit an opponents piece
            if board.get_space(x, y):
                if board.get_space(x, y).colour != self.colour:
                    self.possible_moves[(x, y)] = board.get_space(x, y)

class Knight(Piece):
    
    def __str__(self):
        return 'n'
    
    def __repr__(self):
        return 'n'

    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                      (2, 1), (2, -1), (-2, 1), (-2, -1)]

        # check the eight spaces
        for direction in directions:
            x = self.space[0] + direction[0]
            y = self.space[1] + direction[1]

            # Check if space is valid
            if board.get_space(x, y):
                # Check if space is empty
                if board.get_space(x, y) == '-':
                    self.possible_moves[(x, y)] = '-'
                # Check if the piece is the opponent's
                elif board.get_space(x, y).colour != self.colour:
                    self.possible_moves[(x, y)] = board.get_space(x, y)

class Queen(Piece):
    
    def __str__(self):
        return 'q'
    
    def __repr__(self):
        return 'q'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        directions = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1)]

        # check empty spaces in the cardinal directions
        for direction in directions:
            x = self.space[0] + direction[0]
            y = self.space[1] + direction[1]

            # Stop checking a direction if a piece is hit or out-of-bounds
            while(board.get_space(x, y) == '-'):
                self.possible_moves[(x, y)] = board.get_space(x, y)
                x += direction[0]
                y += direction[1]
            
            # Hit an opponents piece
            if board.get_space(x, y):
                if board.get_space(x, y).colour != self.colour:
                    self.possible_moves[(x, y)] = board.get_space(x, y)

class King(Piece):
    
    def __str__(self):
        return 'k'
    
    def __repr__(self):
        return 'k'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        directions = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1)]
        
        for direction in directions:
            x = self.space[0] + direction[0]
            y = self.space[1] + direction[1]

            if board.get_space(x, y):
                # Check if space is empty
                if board.get_space(x, y) == '-':
                    self.possible_moves[(x, y)] = '-'
                # Check if the piece is the opponent's
                elif board.get_space(x, y).colour != self.colour:
                    self.possible_moves[(x, y)] = board.get_space(x, y)

        
board = Board()

x, y = 1, 0

print(board.get_space(x, y))
board.get_space(x, y).calculate_possible_moves(board)
print(board.get_space(x, y).possible_moves)
board.display_board()