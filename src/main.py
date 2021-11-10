# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    n = 0
    s = 1
    b = -1
    current_state = []

    def __init__(self, recommend=True):
        self.initialize_game()
        self.recommend = recommend

    def initialize_game(self):

        # get board size from user
        while (self.n < 3) or (self.n > 10):
            self.n = int(input('enter the size of the board n (3 - 10): '))

        # get number of blocks from user
        while (self.b < 0) or (self.b > (2 * self.n)):
            self.b = int(input('enter the number of blocks you want on the board b (0 - 2n): '))

        for i in range(self.n):
            temp = []
            for j in range(self.n):
                temp.append('.')
            self.current_state.append(temp)

        # set blocks
        self.input_block()

        # get winning line-up size from user
        while (self.s < 3) or (self.s > self.n):
            self.s = int(input('enter the winning line-up size s (3 - n): '))

        # Player X always plays first
        self.player_turn = 'X'

        # Generate winning combination indices
        self.win_indices = []

        # Horizontal / Vertical
        for i in range(self.n):
            win_v = []
            win_h = []
            for j in range(self.n):
                win_v.append((i, j))
                win_h.append((j, i))
            self.win_indices.append(win_h)
            self.win_indices.append(win_v)

        # Diagonal
        for i in range(self.s - 1, self.n):
            #
            offset_top_right = (1, -1)
            offset_top_left = (-1, -1)
            win_bl_tr1 = []
            win_bl_tr2 = []
            win_br_tl1 = []
            win_br_tl2 = []
            for j in range(i + 1):
                # Bottom Left to Top Right
                diag_bl_tr1 = (offset_top_right[0] * j, offset_top_right[1] * j + i)
                diag_bl_tr2 = (offset_top_right[0] * j + self.n - 1 - i, offset_top_right[1] * j + self.n - 1)
                # Bottom Right to Top Left
                diag_br_tl1 = (offset_top_left[0] * j + self.n - 1, offset_top_left[1] * j + i)
                diag_br_tl2 = (offset_top_left[0] * j + i, offset_top_left[1] * j + self.n - 1)
                # Add points to lists
                win_bl_tr1.append(diag_bl_tr1)
                win_br_tl1.append(diag_br_tl1)
                win_bl_tr2.append(diag_bl_tr2)
                win_br_tl2.append(diag_br_tl2)

            # Append each diagonal
            self.win_indices.append(win_bl_tr1)
            self.win_indices.append(win_br_tl1)

            # Mirror diagonal if not largest
            if i + 1 != self.n:
                self.win_indices.append(win_bl_tr2)
                self.win_indices.append(win_br_tl2)

    def draw_board(self):
        print()
        for y in range(0, self.n):
            for x in range(0, self.n):
                print(F'{self.current_state[x][y]}', end="")
            print()
        print()

    def is_valid(self, px, py):
        if px < 0 or px > (self.n - 1) or py < 0 or py > (self.n - 1):
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):
        # # limit for win
        # limit_for_win = self.n - self.s + 1
        #
        # # Vertical win
        # for column in range(self.n):
        #     for c in range(limit_for_win):
        #         if self.current_state[column][c] != '.' and self.current_state[column][c] != '*':
        #             score = 1
        #             for next_c in range(c + 1, self.n):
        #                 if self.current_state[column][c] != self.current_state[column][next_c]:
        #                     break
        #                 score += 1
        #                 if score == self.s:
        #                     return self.current_state[column][next_c]
        # # Horizontal win
        # for i in range(self.n):
        #     for j in range(limit_for_win):
        #         if self.current_state[i][j] != '.' and self.current_state[i][j] != '*':
        #             score = 1
        #             for k in range(j + 1, self.n):
        #                 if self.current_state[i][j] != self.current_state[i][k]:
        #                     break
        #                 score += 1
        #                 if score == self.s:
        #                     return self.current_state[i][j]

        # # Main diagonal win
        # if (self.current_state[0][0] != '.' and
        #         self.current_state[0][0] == self.current_state[1][1] and
        #         self.current_state[0][0] == self.current_state[2][2]):
        #     return self.current_state[0][0]
        # # Second diagonal win
        # if (self.current_state[0][2] != '.' and
        #         self.current_state[0][2] == self.current_state[1][1] and
        #         self.current_state[0][2] == self.current_state[2][0]):
        #     return self.current_state[0][2]
        # Is whole board full?
        # for i in range(0, self.n):
        #     for j in range(0, self.n):
        #         # There's an empty field, we continue the game
        #         if self.current_state[i][j] == '.':
        #             return None

        # Iterate over all possible winning lines
        for win in self.win_indices:
            # Keep track of last k symbols in a row (and corresponding player)
            last_player = None
            score = 0
            for i in range(len(win)):
                # Get the symbol at coordinates
                coords = win[i]
                symbol = self.current_state[coords[0]][coords[1]]

                # Symbol is the same as the last one, increment score
                if symbol == last_player:
                    score += 1

                # Symbol belongs to a different player than last symbol
                elif symbol != '.' and symbol != '*':

                    # Attempt match S players symbols in a row to win
                    last_player = symbol
                    score = 1

                # Symbol is empty or block
                else:
                    last_player = None

                    # Not enough symbols left to make S in a row
                    if len(win) - i < self.s:
                        break

                # Player wins
                if score >= self.s:
                    return last_player

        for i in range(0, self.n):
            for j in range(0, self.n):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == '.':
                    return None

        # It's a tie!
        return '.'

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                print('The winner is X!')
            elif self.result == 'O':
                print('The winner is O!')
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                return (px, py)
            else:
                print('The move is not valid! Try again.')

    def input_block(self):
        block_count = 0
        while block_count < self.b:
            self.draw_board()
            print('Enter the location of the block to be placed:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                self.current_state[py][px] = '*'
                block_count += 1
            else:
                print('This is not a valid location for a block, please try again')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def minimax(self, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return (value, x, y)

    def alphabeta(self, alpha=-2, beta=2, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return (value, x, y)
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return (value, x, y)
                        if value < beta:
                            beta = value
        return (value, x, y)

    def play(self, algo=None, player_x=None, player_o=None):
        if algo == None:
            algo = self.ALPHABETA
        if player_x == None:
            player_x = self.HUMAN
        if player_o == None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else:  # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {x}, y = {y}')
                (x, y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()


def main():
    g = Game(recommend=True)
    g.play(algo=Game.MINIMAX, player_x=Game.HUMAN, player_o=Game.HUMAN)


if __name__ == "__main__":
    main()
