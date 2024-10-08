"""
NOTES:
- I wonder if there is some kind of way to "watch" spaces, such that an object is affiliated with a space if it is watching it and we can return a list of watchers
- Need to develop test cases

- Also change the code appending stuff to board.moves to include the promotion type. Line 398.
    # at some point lmao
    # and castling -_-
    # Basically include notation, but it's not really necessary
"""

from typing import Union
from os import system

class Board:
    def __init__(self, white_pieces=[], black_pieces=[]):
        
        # 2D array representing the chess board at move 0, default
        self.chess_board = [["-" for x in range(8)] for y in range(8)]
        self.black_pieces = black_pieces
        self.white_pieces = white_pieces
        self.black_king = None
        self.white_king = None

        # Instantiate player pieces
        if not white_pieces:
            pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
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

        # List containing the moves taken during the game, format is '[Initial space: tuple][Piece: Piece][Captured: str][Terminal space: tuple][Promotion]'
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

        self.update_all_possible_moves()
        if self.turn:
            king = self.white_king
            self_pieces = self.white_pieces
            pieces = self.black_pieces
        else:
            king = self.black_king
            self_pieces = self.black_pieces
            pieces = self.white_pieces
        targeting_pieces = []
        

        # Check for pieces that are blocking checks, if a piece is found, remove illegal moves
        directions = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1)]
        
        for direction in directions:
            x = king.space[0] + direction[0]
            y = king.space[1] + direction[1]
            blocking_piece = False  # False/Piece object
            current_space = self.get_space(x, y)

            while current_space:
                # Check if space is empty
                if current_space == '-':
                    x += direction[0]
                    y += direction[1]
                    current_space = self.get_space(x, y)
                    continue
            
                # Opposing piece
                if current_space.colour != king.colour:
                    # There is a piece blocking the path
                    if blocking_piece:
                        # Own piece is blocking check
                        if blocking_piece.space in current_space.possible_moves:

                            # Pawn/King are safe pieces
                            if type(current_space) in [Pawn, King]:
                                break

                            # Pawns get their own special little block
                            if type(blocking_piece) == Pawn:
                                # Diagonal
                                if (direction[0]+direction[1]) % 2 == 0:
                                    blocking_piece.possible_moves.clear()
                                    if self.get_space(x-direction[0], y-direction[1]) != '-':
                                        blocking_piece.possible_moves[(x, y)] = current_space
                                    break

                                    # Use this if above doesn't work
                                    #for space in blocking_piece.possible_moves.copy():
                                    #    if blocking_piece[space] != current_space:
                                    #        blocking_piece.pop(space)
                                # Vertical
                                elif direction[0]:
                                    for space in blocking_piece.possible_moves.copy():
                                        if space[1] != y:
                                            blocking_piece.possible_moves.pop(space)
                                # Horizontal
                                else:
                                    blocking_piece.possible_moves.clear()
                                break

                            # If the blocking piece cannot capture the checking piece, then it has no valid moves
                            if current_space.space not in blocking_piece.possible_moves:
                                blocking_piece.possible_moves.clear()
                                break

                            # Blocking piece must be able to capture, so all possible moves should be on the path
                            blocking_piece.possible_moves.clear()
                            while (current_space) != king:
                                blocking_piece.possible_moves[(x, y)] = current_space
                                x -= direction[0]
                                y -= direction[1]
                                current_space = self.get_space(x, y)
                            blocking_piece.possible_moves.pop(blocking_piece.space)
                            break
                        # Case 1: The blocking piece is own piece and opposing piece is not a check threat
                        # Case 2: The blocking piece is a capturable piece, need to check if capturing leads to a check
                        else:
                            if blocking_piece.colour == king.colour:
                                break
                            # Diagonal
                            if (direction[0] + direction[1]) % 2 == 0:
                                if type(current_space) in [Queen, Bishop]:
                                    king.possible_moves.pop(blocking_piece.space)
                                elif type(current_space) in [Pawn, King]:
                                    if self.get_space(x-direction[0], y-direction[1]) == blocking_piece:
                                        king.possible_moves.pop(blocking_piece.space)
                            # Horizontal
                            else:
                                if type(current_space) in [Queen, Rook]:
                                   king.possible_moves.pop(blocking_piece)
                                elif type(current_space) == King:
                                    if self.get_space(x-direction[0], y-direction[1]) == blocking_piece:
                                        king.possible_moves.pop(blocking_piece.space)
                                 
                                
                    # There is no piece blocking the path
                    else:
                        # check threat
                        if king.space in current_space.possible_moves:
                            targeting_pieces.append(current_space)
                        # Need to check if this capture is safe
                        elif current_space.space in king.possible_moves:
                            blocking_piece = current_space
                            continue
                        break
                
                # Own piece scenario
                else:
                    # Not a possible check scenario
                    if blocking_piece:
                        break
                    else:
                        blocking_piece = current_space

                x += direction[0]
                y += direction[1]
                current_space = self.get_space(x, y)
        
        # Check for knight checks
        for piece in pieces:
            if type(piece) != Knight:
                continue
            if king.space in piece.possible_moves:
                targeting_pieces.append(piece)

        # Stalemate condition
        if not targeting_pieces:
            self.check_end(False)
            return

        # Double check without any king moves is a checkmate
        if len(targeting_pieces) != 1:
            for piece in self_pieces:
                    if type(piece) == King:
                        continue
                    piece.possible_moves.clear()
            if not king.possible_moves:
                self.end_screen("checkmate")
        else:
            self.in_check(king, targeting_pieces[0])

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
            self.end_screen("checkmate")
        self.end_screen("stalemate")
    
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

        from sys import exit

        if condition == "checkmate":
            if self.turn:
                print("White has checkmate!")
            else:
                print("Black has checkmate!")
        else:
            print("Stalemate!")
        
        exit()
    
    def get_space(self, x: int, y: int) -> Union[object, str]:
        # return the chess piece at space xy if space is valid, else return '-'  
        if not self.space_in_bounds((x, y)):
            return ""
        
        return self.chess_board[x][y]
    
    # I think that there could be an early exit if the targeting piece is a knight
    ###############################################################
    def in_check(self, king: object, targetting_piece: object) -> None:
        """"
        Remove moves from player such that the only moves that can be made are ones that get out of check
        """
        # The pieces of the player that is in check
        pieces = self.white_pieces if king.colour else self.black_pieces
        pieces = pieces.copy()
        pieces.remove(king)

        if type(targetting_piece) == Knight:
            for piece in pieces:
                if targetting_piece.space in piece.possible_moves:
                    piece.possible_moves.clear()
                    piece.possible_moves[targetting_piece.space] = targetting_piece
                else:
                    piece.possible_moves.clear()
            self.check_end(True)
            return

        # Establish which direction the targetting piece is relative to the king.
        # Change with a function that can check sign
        direction = [targetting_piece.space[0]-king.space[0], targetting_piece.space[1]-king.space[1]]
        direction[0] = int(direction[0]/abs(direction[0])) if direction[0] else 0
        direction[1] = int(direction[1]/abs(direction[1])) if direction[1] else 0
        sign_x = direction[0]
        sign_y = direction[1]
        
        # Find the spaces that pieces can land on to get out of check
        spaces = {targetting_piece.space}
        while (self.get_space(king.space[0]+direction[0], king.space[1]+direction[1]) == '-'):
            spaces.add((king.space[0]+direction[0], king.space[1]+direction[1]))
            direction[0] += sign_x
            direction[1] += sign_y

        # Remove moves from all pieces that don't get out of check
        for piece in pieces:
            intersect = spaces.intersection(piece.possible_moves)
            temp_possible_moves = {}
            for move in intersect:
                temp_possible_moves[move] = piece.possible_moves[move]
            piece.possible_moves = temp_possible_moves.copy()
            #for move in piece.possible_moves.copy():
            #    if move not in intersect:
            #        piece.possible_moves.pop(move)
        
        # King cannot castle out of check
        for move in king.possible_moves.copy():
            if king.possible_moves[move] == '-':
                continue
            if king.possible_moves[move].colour == king.colour:
                king.possible_moves.pop(move)

        # Check for checkmate
        self.check_end(True)
    
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
        ## Dirty, but clearing all moves like this is an easy way to resolve this problem of calculating piece movements based off of other pieces
        if self.turn:
            for piece in self.white_pieces:
                piece.possible_moves.clear()
            for piece in self.black_pieces:
                piece.calculate_possible_moves(self)
            for piece in self.white_pieces:
                piece.calculate_possible_moves(self)
        else:
            for piece in self.black_pieces:
                piece.possible_moves.clear()
            for piece in self.white_pieces:
                piece.calculate_possible_moves(self)
            for piece in self.black_pieces:
                piece.calculate_possible_moves(self)


class Piece:
    def __init__(self, colour, space):
        # True for white, False for black
        self.colour = colour
        # tuple
        self.space = space
        self.possible_moves = {}
        self.starting_space = space     # In theory, should be a private variable
    
    def move(self, board: Board, terminal_space: tuple) -> None:
        # move/capture to space on board
        captured = ''

        if self.possible_moves[terminal_space] != '-':
            captured = 'x'
            captured_piece = self.possible_moves[terminal_space]

            if board.turn:
                board.black_pieces.remove(captured_piece)
            else:
                board.white_pieces.remove(captured_piece)
        
        board.moves.append((self.space, self, captured, terminal_space))
        board.chess_board[terminal_space[0]][terminal_space[1]] = self
        board.chess_board[self.space[0]][self.space[1]] = '-'
        self.space = terminal_space

    def copy(self):
        piece = type(self)(self.colour, self.space)
        piece.possible_moves = self.possible_moves.copy()
        return piece
    
    # Comparing Piece objects, only other comparison is '-' return false in this case
    def __eq__(self, __value: Union[object, str]) -> Union[object, bool]:
        if type(__value) == str:
            return False
        else:
            if type(self) == type(__value) and self.space == __value.space and self.colour == __value.colour:
                return True
            return False    

class Pawn(Piece):

    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♙" if self.colour else "♟︎"

    def __str__(self):
        return self.__str_repr
    
    def __repr__(self):
        return 'p'

    def calculate_possible_moves(self, board):
        self.possible_moves.clear()

        # Consider a1 to be the bottom left, then white moves towards list row 0 and black moves towards list row 7
        direction = -1 if self.colour else 1

        # Check if the space in front of the pawn is empty
        if board.get_space(self.space[0]+direction, self.space[1]) == '-':
            self.possible_moves[self.space[0]+direction, self.space[1]] = '-'
            
            # If at starting position, then check if two spaces in front is empty
            if self.space == self.starting_space:
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
        if not board.moves:
            return
        if type(board.moves[-1][1]) != Pawn:
            return
        initial_space = board.moves[-1][0]
        terminal_space = board.moves[-1][3]
        # Check if pawn moved two spaces
        if abs(initial_space[0]-terminal_space[0]) != 2:
            return
        if board.moves[-1][1] is self:
            return

        for direction in [-1, 1]:
            if board.get_space(terminal_space[0], terminal_space[1]+direction) is self:
                ## Fix where enpassent ends up
                self.possible_moves[terminal_space[0]+direction, terminal_space[1]] = board.get_space(terminal_space[0], terminal_space[1])
        
    def move(self, board: Board, terminal_space: tuple) -> None:
        captured = 'x' if self.possible_moves[terminal_space] != '-' else ''
        # Promotion
        if terminal_space[0] in [0, 7]:
            while True:
                promotion_piece = input("Promote pawn to (q, r, b, n): ")
                if promotion_piece == 'q':
                    promotion_piece = Queen(self.colour, terminal_space)
                    break
                elif promotion_piece == 'r':
                    promotion_piece = Rook(self.colour, terminal_space)
                    break
                elif promotion_piece == 'b':
                    promotion_piece = Bishop(self.colour, terminal_space)
                    break
                elif promotion_piece == 'n':
                    promotion_piece = Knight(self.colour, terminal_space)
                    break
                else:
                    continue

            if self.colour:
                board.white_pieces.remove(self)
                board.white_pieces.append(promotion_piece)
            else:
                board.black_pieces.remove(self)
                board.black_pieces.append(promotion_piece)
            
            if captured:
                if self.colour:
                    board.black_pieces.remove(self.possible_moves[terminal_space])
                else:
                    board.white_pieces.remove(self.possible_moves[terminal_space])

            board.moves.append((self.space, self, captured, terminal_space))
            board.chess_board[terminal_space[0]][terminal_space[1]] = promotion_piece
            board.chess_board[self.space[0]][self.space[1]] = '-'
            return
            
        ## Piece.move(), I think it is better to just copy/paste the code here rather than calling the method
        # move/capture to space on board

        if captured:
            captured_piece = self.possible_moves[terminal_space]
            board.chess_board[captured_piece.space[0]][captured_piece.space[1]] = '-' # For en-passent

            if board.turn:
                board.black_pieces.remove(captured_piece)
            else:
                board.white_pieces.remove(captured_piece)
            
            """if type(self) == Pawn and self.space[0] == self.possible_moves[terminal_space][0]:

            if board.turn:
                board.black_pieces.remove(board.chess_board[terminal_space[0]][terminal_space[1]])
            else:
                board.white_pieces.remove(board.chess_board[terminal_space[0]][terminal_space[1]])"""
        
        board.moves.append((self.space, self, captured, terminal_space))
        board.chess_board[terminal_space[0]][terminal_space[1]] = self
        board.chess_board[self.space[0]][self.space[1]] = '-'
        self.space = terminal_space

class Rook(Piece):
    
    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♖" if self.colour else "♜"

    def __str__(self):
        return self.__str_repr

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
    
    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♗" if self.colour else "♝"

    def __str__(self):
        return self.__str_repr
    
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
    
    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♘" if self.colour else "♞"

    def __str__(self):
        return self.__str_repr
    
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
    
    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♕" if self.colour else "♛"

    def __str__(self):
        return self.__str_repr
    
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
    
    def __init__(self, colour, space):
        super().__init__(colour, space)
        self.__str_repr = "♔" if self.colour else "♚"

    def __str__(self):
        return self.__str_repr
    
    def __repr__(self):
        return 'k'

    def calculate_possible_moves(self, board):
        self.possible_moves.clear()
        opponent_pieces = board.black_pieces if self.colour else board.white_pieces
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

        # Check king valid king spaces
        ## Dirty method, change this if optimization is needed
        empty_spaces = {move for move in self.possible_moves if self.possible_moves[move] != '-'}
        for piece in opponent_pieces:
            if empty_spaces:
                temp_board = Board([piece.copy()])
                temp_board.white_pieces[0].calculate_possible_moves(temp_board)
                for move in empty_spaces.intersection(temp_board.white_pieces[0].possible_moves):
                    self.possible_moves.pop(move)
                    empty_spaces.remove(move)
            for move in (self.possible_moves.keys()-empty_spaces).intersection(piece.possible_moves):
                self.possible_moves.pop(move)

        # Check for castling
        if self.space != self.starting_space:
            return
        
        for corner in [0, 7]:
            rook = board.get_space(self.space[0], corner)
            if type(rook) != Rook:
                continue
            if rook.space != rook.starting_space:
                continue

            direction = -1 if corner else 1
            current_space = [self.space[0], corner+direction]
            check = False
            while(board.get_space(current_space[0], current_space[1]) == '-'):
                if check:
                    break
                # Cannot castle into/through check
                if abs(4-current_space[1]) < 3:
                    for piece in opponent_pieces:
                        if tuple(current_space) in piece.possible_moves:
                            check = True
                            break
                current_space[1] += direction
            current_space = board.get_space(current_space[0], current_space[1])
            if current_space is not self:
                continue
            if current_space.space != current_space.starting_space:
                continue
            self.possible_moves[(self.space[0], self.space[1]+(-2*direction))] = rook

    def move(self, board: Board, terminal_space: tuple) -> None:
        # Move/capture to space on board
        captured = ''

        if self.possible_moves[terminal_space] != '-':
            # Castling
            if self.possible_moves[terminal_space].colour == self.colour:
                rook = self.possible_moves[terminal_space]
                direction = -1 if rook.space[1] else 1
                board.chess_board[terminal_space[0]][terminal_space[1]+direction] = rook
                board.chess_board[rook.space[0]][rook.space[1]] = '-'
                rook.space = (terminal_space[0], terminal_space[1]+direction)
            else:    
                captured = 'x'
                captured_piece = self.possible_moves[terminal_space]

                if board.turn:
                    board.black_pieces.remove(captured_piece)
                else:
                    board.white_pieces.remove(captured_piece)

        board.moves.append((self.space, self, captured, terminal_space))
        board.chess_board[terminal_space[0]][terminal_space[1]] = self
        board.chess_board[self.space[0]][self.space[1]] = '-'
        self.space = terminal_space

def main():

    board = Board()

    print("Hello, in order to move your pieces, you will have to input the space of the piece you're moving and the space you want to move it to.")
    print("For example, to move pawn to e5, enter 'e3e5'.")
    input("Press any key to play.")
    system('cls')

    while True:
        board.display_board()
        board.check_board()
        board.ply()
        

if __name__ == "__main__":
    main()