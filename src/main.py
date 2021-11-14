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
    d1 = 0
    t = 0
    d2 = 0
    a = False
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

        # Max depth of adversarial search for player 1
        while self.d1 < 1:
            self.d1 = int(input('enter the max depth of the adversarial search for player 1: '))

        # Max depth of adversarial search for player 2
        while self.d2 < 1:
            self.d2 = int(input('enter the max depth of the adversarial search for player 2: '))

        # Max time for program to return a move
        while self.t < 1:
            self.t = int(input('enter the maximum allowed time (in seconds) for the program to return a move: '))

        # Boolean for use of minimax or alphabeta
        temp = 0
        while temp < 1 or temp > 2:
            print('Please select which type of adversarial search the program should implement')
            temp = int(input('Enter 1 for Minimax or 2 for AlphaBeta: '))

        if temp == 2:
            self.a = True

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

        # print horizontal indices according to size
        print("   ", end="")
        for i in range(0, self.n):
            print(F'{self.get_letter(i)}', end="")

        # print line at top of board
        print()
        print("  +", end="")
        for i in range(0, self.n):
            print("-", end="")

        print()
        for y in range(0, self.n):
            print(y, "|", end="")
            for x in range(0, self.n):
                print(F'{self.current_state[x][y]}', end="")
            print()
        print()

    @staticmethod
    def get_letter(index):
        switcher = {
            0: "A",
            1: "B",
            2: "C",
            3: "D",
            4: "E",
            5: "F",
            6: "G",
            7: "H",
            8: "I",
            9: "J"
        }

        return switcher.get(index, " ")

    @staticmethod
    def get_index(letter):
        letter = letter.upper()
        switcher = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
            "E": 4,
            "F": 5,
            "G": 6,
            "H": 7,
            "I": 8,
            "J": 9
        }

        return switcher.get(letter, -1)

    def is_valid(self, px, py):
        if px < 0 or px > (self.n - 1) or py < 0 or py > (self.n - 1):
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):
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
            px = self.get_index(input(F'enter the x coordinate (A-{self.get_letter(self.n - 1)}): '))
            py = int(input(F'enter the y coordinate (0-{self.n - 1}): '))
            if self.is_valid(px, py):
                return px, py
            else:
                print('The move is not valid! Try again.')

    def input_block(self):
        block_count = 0
        while block_count < self.b:
            self.draw_board()
            print('Enter the location of the block to be placed:')
            px = self.get_index(input(F'enter the x coordinate (A-{self.get_letter(self.n - 1)}): '))
            py = int(input(F'enter the y coordinate (0-{self.n - 1}): '))
            if self.is_valid(py, px):
                self.current_state[px][py] = '*'
                block_count += 1
            else:
                print('This is not a valid location for a block, please try again')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def is_valid_coordinates(self, coords):
        return 0 <= coords[0] < self.n and 0 <= coords[1] < self.n

    def heuristic_simple(self, max):
        # Blocked
        # side = 0
        # Free
        # side = +1
        # Side
        # with same symbol = +2

        heuristic = 0
        player = 'X'
        other_player = 'O'
        if max:
            player = 'O'
            other_player = 'X'

        neighbor_offsets = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == player:
                    for neighbor in neighbor_offsets:
                        coords = (i + neighbor[0], j + neighbor[1])
                        if self.is_valid_coordinates(coords):
                            symbol = self.current_state[coords[0]][coords[1]]
                            if symbol == player:
                                heuristic += 2
                            elif symbol == ".":
                                heuristic += 1
                            elif symbol == other_player:
                                heuristic -= 1
        return heuristic

    def minimax(self, depth=3, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 10000
        if max:
            value = -10000
        x = y = None
        result = self.is_end()
        if result == 'X':
            return value, x, y
        elif result == 'O':
            return value, x, y
        elif result == '.':
            return 0, x, y
        elif result is None and depth == 0:
            return self.heuristic_simple(max), x, y
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(depth - 1, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(depth - 1, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return value, x, y

    def alphabeta(self, depth=3, alpha=-10000, beta=10000, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 10000
        if max:
            value = -10000
        x = y = None
        # check depth = 0
        result = self.is_end()
        if result == 'X':
            return value, x, y
        elif result == 'O':
            return value, x, y
        elif result == '.' and depth == 0:
            return self.heuristic_simple(), x, y
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(depth - 1, alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(depth - 1, alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return value, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y
                        if value < beta:
                            beta = value
        return value, x, y

    def play(self, algo=None, player_x=None, player_o=None):
        if algo is None:
            algo = self.ALPHABETA
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(depth=self.d1, max=False)
                else:
                    (_, x, y) = self.minimax(depth=self.d2, max=True)
            else:  # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(depth=self.d1, max=False)
                else:
                    (m, x, y) = self.alphabeta(depth=self.d2, max=True)
            end = time.time()
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {self.get_letter(x)}, y = {y}')
                (x, y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {self.get_letter(x)}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()


def main():
    g = Game(recommend=True)
    g.play(algo=Game.MINIMAX, player_x=Game.HUMAN, player_o=Game.HUMAN)


if __name__ == "__main__":
    main()
