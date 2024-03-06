"""
NOTES:
- I wonder if there is some kind of way to "watch" spaces, such that an object is affiliated with a space if it is watching it and we can return a list of watchers
- In the check_board() function, "if king.possible_moves" might need to be removed in order to run in_check()
- Need to develop end_screen()
- In ply(), need to restrict moves that expose king to check
- Implement pawn promotion
- Need to restrict the king from walking into a check
- Need to develop test cases
- In pieces, the equality function may be changed to check address's instead
- When calculating possible moves, maybe keep all the spaces and then in ply() we just don't accept the spaces that 
    hold pieces of the same colour, this way we can determine if a king can't capture a piece, easily
    Or maybe it'll be faster to save the game state, calculate possible moves and see if king is capturable by a piece
"""

from typing import Union

class Board:
    def __init__(self, white_pieces=[], black_pieces=[]):
        
        # 2D array representing the chess board at move 0, default
        self.chess_board = [["-" for x in range(8)] for y in range(8)]
        self.black_pieces = black_pieces
        self.white_pieces = white_pieces
        self.black_king = None
        self.white_king = None

        # Instantiate player pieces
        if not black_pieces:
            pieces = [Rook, Bishop, Knight, Queen, King, Knight, Bishop, Rook]
            self.black_pieces = [x(False, (0, y)) for x,y in zip(pieces, [x for x in range(8)])] + [Pawn(False, (1, x)) for x in range(8)] if not black_pieces else black_pieces
            self.white_pieces = [x(True, (7, y)) for x,y in zip(pieces, [x for x in range(8)])] + [Pawn(True, (6, x)) for x in range(8)] if not white_pieces else white_pieces
            self.black_king = self.black_pieces[4]
            self.white_king = self.white_pieces[4]

            self.chess_board[0] = self.black_pieces[:8]
            self.chess_board[1] = self.black_pieces[8:]
            self.chess_board[6] = self.white_pieces[8:]
            self.chess_board[7] = self.white_pieces[:8]
        else:
            for piece in black_pieces + white_pieces:
                self.chess_board[piece.space[0]][piece.space[1]] = piece

                if type(piece) == King:
                    if piece.colour:
                        self.white_king = piece
                    else:
                        self.black_king = piece

        # List containing the moves taken during the game, format is '[Initial space: tuple][Piece: Piece][Captured: str][Terminal space: tuple]'
        self.moves = []
        # True for white, False for black
        self.turn = True

    def check_board(self) -> None:
        # IF king has no moves AND
        # An opponents piece can capture on the next turn AND
        # Player has no pieces that can block that move, 
        # THEN Player loses

        # If the king has no moves AND is not in check, 
        # If every other piece has no moves, 
        # THEN it is a stalemate

        king = self.white_king if self.turn else self.black_king
        pieces = self.black_pieces if self.turn else self.white_pieces
        targeting_pieces = []
        self.update_all_possible_moves()

        # King has a possible move
        if king.possible_moves:
            return
        
        # Return False if no pieces can capture the king
        for piece in pieces:
            if king in piece.possible_moves.values():
                targeting_pieces.append(piece)

        # Stalemate condition
        if not targeting_pieces:
            self.check_end(False)

        # Double check without any king moves is a checkmate
        if len(targeting_pieces) != 1:
            self.end_screen("checkmate")
        else:
            self.in_check(king, targeting_pieces[0])
        
    def in_check(self, king: object, targetting_piece: object) -> bool:
        """"
        Remove moves from player such that the only moves that can be made are ones that get out of check
        """
        # The pieces of the player that is in check
        pieces = self.white_pieces if king.colour else self.black_pieces

        # Establish which direction the targetting piece is relative to the king.
        direction = [targetting_piece.space[0]-king.space[0], targetting_piece.space[1]-king.space[1]]
        sign_x = -1 if direction[0] < 0 else 1
        sign_y = -1 if direction[1] < 0 else 1
        direction[0] = sign_x if direction[0] else 0
        direction[1] = sign_y if direction[1] else 0

        # Find the spaces that pieces can land on to get out of check
        spaces = {targetting_piece.space}
        if type(targetting_piece) != Knight:
            while (self.get_space(direction[0], direction[1]) == '-'):
                spaces.add((king.space[0]+direction[0], king.space[1]+direction[1]))
                direction[0] += sign_x
                direction[1] += sign_y

        # Remove moves from all pieces that don't get out of check
        for piece in pieces:
            intersect = spaces.intersection(piece.possible_moves)
            for space in piece.possible_moves:
                if space not in intersect:
                    piece.possible_moves.pop(space)

        # Check for checkmate
        self.check_end(True)


    def check_end(self, state: bool) -> None:
        """
        Check the moves of the current player, if they have no moves then it's either a stalemate or checkmate
        
        state: True for checkmate, False for stalemate
        """

        pieces = self.white_pieces if self.turn else self.black_pieces
        for piece in pieces:
            if piece.possible_moves:
                return
        
        if state:
            return self.end_screen("checkmate")
        return self.end_screen("stalemate")
    
    def convert_space_to_array_index(self, move):
        def char_range(c1, c2):
            """Generates the characters from `c1` to `c2`, inclusive."""
            for c in range(ord(c1), ord(c2)+1):
                yield chr(c)
                
        # ['a'-'h'][1-8] -> [0-7][0-7]
        row = {x:y for x,y in zip([a for a in range(8, -1, -1)], [b for b in range(8)])}
        column = {x:y for x,y in zip([a for a in char_range('a','h')], [b for b in range(9)])}
        return row[int(move[1])], column[move[0]]

    def display_board(self) -> None:
        for x in self.chess_board:
            for y in x:
                print(y, end=" ")
            print()

    def end_screen(self, condition: str) -> None:
        """
        condition: "checkmate" / "stalemate"

        If "checkmate":
            then display that the current player turn has lost / next player turn has won (!self.turn)
        else:
            display stalemate
        """
    
    def get_space(self, x: int, y: int) -> Union[object, str]:
        # return the chess piece at space xy if space is valid, else return '-'  
        if not self.space_in_bounds((x, y)):
            return ""
        
        return self.chess_board[x][y]
    
    def ply(self) -> None:
        """
        string: "[initial space][terminal space]"
        """
        initial_space = ""
        terminal_space = ""
        user_piece = None

        # Player has to input a valid move, ie move one of their pieces to a valid space
        while True:
        # Player has to input a string of a valid format
            while True:
                string = input("Enter your move: ")
                if len(string) != 4:
                    continue
                for i in range(4):
                    if i%2:
                        if int(string[i]) not in range(1, 9):
                            break
                    else:
                        if ord(string[i]) not in range(97, 105):
                            break
                else:
                    break

            initial_space = self.convert_space_to_array_index(string[0:2])
            terminal_space = self.convert_space_to_array_index(string[2:])
            user_piece = self.get_space(initial_space[0], initial_space[1])

            # Initial space has to hold a piece
            if user_piece == '-':
                continue

            # Player can only move their pieces
            if user_piece.colour != self.turn:
                continue
            
            # Player has to move to a valid space
            if terminal_space not in user_piece.possible_moves:
                continue

            user_piece.move(self, terminal_space)
            self.turn = not self.turn
            break

    def space_in_bounds(self, space: tuple) -> bool:
        if 0 <= space[0] <= 7 and 0 <= space[1] <= 7:
            return True
        return False

    def update_all_possible_moves(self) -> None:
        if self.turn:
            for piece in self.white_pieces:
                piece.calculate_possible_moves(self)
        else:
            for piece in self.black_pieces:
                piece.calculate_possible_moves(self)
                

class Piece:
    def __init__(self, colour, space):
        # True for white, False for black
        self.colour = colour
        # tuple
        self.space = space
        self.possible_moves = {}
    
    def move(self, board: Board, terminal_space: tuple) -> None:
        # move/capture to space on board
        captured = ''
            
        if self.possible_moves[terminal_space] != '-':
            captured = 'x'
            if board.turn:
                board.black_pieces.remove(board.chess_board[terminal_space[0]][terminal_space[1]])
            else:
                board.white_pieces.remove(board.chess_board[terminal_space[0]][terminal_space[1]])
        board.moves.append((self.space, self, captured, terminal_space))
        
        board.chess_board[terminal_space[0]][terminal_space[1]] = self
        board.chess_board[self.space[0]][self.space[1]] = '-'
        self.space = terminal_space
    
    # Comparing Piece objects, only other comparison is '-' return false in this case
    def __eq__(self, __value: Union[object, str]) -> Union[object, bool]:
        if type(__value) == str:
            return False
        else:
            if type(self) == type(__value) and self.space == __value.space and self.colour == __value.colour:
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
                initial_space = board.convert_space_to_array_index(board.moves[-1][0])
                terminal_space = board.convert_space_to_array_index(board.moves[-1][3])
                # Check if pawn moved two spaces
                if abs(initial_space[0]-terminal_space[0]) == 2:

                    # NEED TO CHECK IF THIS WORKS
                    if board.get_space(terminal_space[0], terminal_space[1]-1) is self:
                        self.possible_moves[terminal_space[0]+direction, terminal_space[1]-1] = board.get_space(terminal_space)
                    elif board.get_space(terminal_space[0], terminal_space[1]+1) is self:
                        self.possible_moves[terminal_space[0]+direction, terminal_space[1]+1] = board.get_space(terminal_space)

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
        opponent_pieces = board.black_pieces if board.turn else board.white_pieces
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


def main():
    white_pieces = [Queen(True, (6,1)), King(True, (7,1)), Rook(True, (1,1)), Bishop(True, (7,5)), Pawn(True, (5,5)), Pawn(True, (5,6)), Pawn(True, (6,7))]
    black_pieces = [Queen(False, (4,2)), King(False, (7,3)), Rook(False, (6,3)), Rook(False, (0,7)), Pawn(False, (3,1)), Pawn(False, (1,5)), Pawn(False, (2,6)), Pawn(False, (1, 7))]
    board = Board(white_pieces, black_pieces)
    board.update_all_possible_moves()
    board.turn = not board.turn
    board.update_all_possible_moves()

    board.display_board()

    while True:
        board.ply()
        board.display_board()

if __name__ == "__main__":
    main()