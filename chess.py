"""
Chess brother
"""

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
        self.moves = [None]

    def get_space(self, x, y):
        # return the chess piece at space xy, else return '-'
        return self.chess_board[x][y]
    
    def display_board(self):
        for x in self.chess_board:
            for y in x:
                print(y, end=" ")
            print()

    def convert_space_to_array_index(self, move):
        def char_range(c1, c2):
            """Generates the characters from `c1` to `c2`, inclusive."""
            for c in range(ord(c1), ord(c2)+1):
                yield chr(c)
                
        # ['a'-'h'][1-8] -> [0-7][0-7]
        row = {x:y for x,y in zip([a for a in char_range('a','i')], [b for b in range(7, -1, -1)])}
        column = {x:y for x,y in zip([a for a in range(1, 9)], [b for b in range(8)])}
        return row[move[0]], column[move[1]]
    
class Piece:
    def __init__(self, color, space):
        # True for white, False for black
        self.colour = color
        self.space = space
        self.possible_moves = {}

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

        # check if the space in front of the pawn is empty
        if board.get_space(self.space[0]+direction, self.space[1]) == '-':
            self.possible_moves[self.space[0]+direction, self.space[1]] = '-'
            
            # if at starting position, then check if two spaces in front is empty
            if self.space == start_row and board.get_space(self.space[0]+direction*2, self.space[1]) == '-':
                self.possible_moves[self.space[0]+direction*2, self.space[1]] = '-'
        
        # check if there are capturable pieces
        for x in [-1, 1]:
            if board.get_space(self.space[0]+direction, self.space[1]+x) != '-':
                self.possible_moves[self.space[0]+direction, self.space[1]+x] = board.get_space(self.space[0]+direction, self.space[1]+x)

        # check for en passent
        if type(board.moves[-1][0]) == Pawn:
            initial_space = board.convert_space_to_array_index(board.moves[-1][1])
            terminal_space = board.convert_space_to_array_index(board.moves[-1][2])
            if abs(initial_space[0]-terminal_space[0]) == 2 and initial_space[1] == terminal_space[1]:
                if board.get_space(terminal_space[0], terminal_space[1]-1) is self:
                    self.possible_moves[terminal_space[0]+direction, terminal_space[1]-1] = board.get_space(terminal_space)
                elif board.get_space(terminal_space[0], terminal_space[1]+1) is self:
                    self.possible_moves[terminal_space[0]+direction, terminal_space[1]+1] = board.get_space(terminal_space)

        # define move function
        # promotion
                
        

class Rook(Piece):
    
    def __str__(self):
        return 'r'

    def __repr__(self):
        return 'r'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

class Bishop(Piece):
    
    def __str__(self):
        return 'b'
    
    def __repr__(self):
        return 'b'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

class Knight(Piece):
    
    def __str__(self):
        return 'n'
    
    def __repr__(self):
        return 'n'

    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

class Queen(Piece):
    
    def __str__(self):
        return 'q'
    
    def __repr__(self):
        return 'q'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

class King(Piece):
    
    def __str__(self):
        return 'k'
    
    def __repr__(self):
        return 'k'
    
    def calculate_possible_moves(self, board):
        self.possible_moves.clear()



