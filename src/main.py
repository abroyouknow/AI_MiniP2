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
    temp = 0
    a = False
    game_mode = 0
    num_games = 0
    current_state = []

    def __init__(self, recommend=True):
        self.initialize_game()
        self.recommend = recommend

    def initialize_game(self):

        # get board size from user
        while (self.n < 3) or (self.n > 10):
            print()
            self.n = int(input('Enter the size of the board n (3 - 10): '))

        # get number of blocks from user
        while (self.b < 0) or (self.b > (2 * self.n)):
            print()
            self.b = int(input('Enter the number of blocks you want on the board b (0 - 2n): '))

        new_state = []
        for i in range(self.n):
            temp = []
            for j in range(self.n):
                temp.append('.')
            new_state.append(temp)
        self.current_state = new_state

        # set blocks
        self.input_block()

        # get winning line-up size from user
        while (self.s < 3) or (self.s > self.n):
            print()
            self.s = int(input('Enter the winning line-up size s (3 - n): '))

        # Max depth of adversarial search for player 1
        while self.d1 < 1:
            print()
            self.d1 = int(input('Enter the max depth of the adversarial search for player 1: '))

        # Max depth of adversarial search for player 2
        while self.d2 < 1:
            print()
            self.d2 = int(input('Enter the max depth of the adversarial search for player 2: '))

        # Max time for program to return a move
        while self.t < 1:
            print()
            self.t = int(input('Enter the maximum allowed time (in seconds) for the program to return a move: '))

        # Number of games to play
        while self.num_games < 1:
            print()
            self.num_games = int(input('Enter the number of games you wish to play: '))

        # Boolean for use of minimax or alphabeta
        while self.temp < 1 or self.temp > 2:
            print()
            print('Which type of adversarial search should the program implement?')
            print('\t1- Minimax')
            print('\t2- Alpha-Beta')
            self.temp = int(input('Enter the number associated with your choice: '))
        self.a = self.temp == 2

        # Game mode
        while self.game_mode < 1 or self.game_mode > 4:
            print()
            print('Which game mode would you like to play?')
            print('\t1- Human vs Human')
            print('\t2- Human vs AI')
            print('\t3- AI vs Human')
            print('\t4- AI vs AI')
            self.game_mode = int(input('Enter the number associated with your choice: '))

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
        result = self.is_end()
        # Printing the appropriate message if the game has ended
        if result is not None:
            if result == 'X':
                print('The winner is X!')
            elif result == 'O':
                print('The winner is O!')
            elif result == '.':
                print("It's a tie!")
            self.initialize_game()
        return result

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

    def heuristic_simple(self):
        # Iterate over all possible winning lines
        # h += 10^o - 10^x for each winning line
        # where o and x are the number of each player symbol respectively
        heuristic = 0
        for win in self.win_indices:
            x = o = 0
            for coords in win:
                symbol = self.current_state[coords[0]][coords[1]]
                if symbol == 'O':
                    o += 1
                elif symbol == 'X':
                    x += 1
            heuristic += pow(10, o) - pow(10, x)
        return heuristic

    def heuristic_complex(self):
        # Iterate over all possible winning lines
        # h += o - x
        # where o and x are the number of ways each player can win in that line respectively
        heuristic = 0
        for win in self.win_indices:

            # Number of winning combinations for each player
            x = o = 0

            # Number of combinations to check in a line
            # N = Lwin - S + 1
            # Example: N = 4, S = 3, Lwin = 4
            # N = Lwin - S + 1 = 4 - 3 + 1 = 2
            # Visually:
            # 1. [* * *] *
            # 2. * [* * *]
            # where * is any symbol
            for i in range(len(win) - self.s + 1):

                # Count number of symbols in possible win
                x_count = 0
                o_count = 0
                for coords in win[i:i + self.s]:
                    symbol = self.current_state[coords[0]][coords[1]]
                    x_count += 1 if (symbol == 'X' or symbol == '.') else 0
                    o_count += 1 if (symbol == 'Y' or symbol == '.') else 0

                # x += 1 is we have at least s symbols
                if x_count >= self.s:
                    x += 1

                # o += 1 is we have at least s symbols
                if o_count >= self.s:
                    o += 1

            # Add evaluation of line to heuristic
            heuristic += o - x

        return heuristic

    def minimax(self, start_time, heuristic, depth=3, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = float('inf')
        if max:
            value = -value
        x = y = None

        # Not enough time left to evaluate
        if (self.t - (time.time() - start_time)) <= 0.002:
            return value, x, y

        # Evaluate heuristic at tree leaves or win/loss/tie
        result = self.is_end()
        if result == 'X':
            return heuristic() + value, x, y
        elif result == 'O':
            return heuristic() + value, x, y
        elif result == '.':
            return 0, x, y
        elif result is None and depth == 0:
            return heuristic(), x, y

        # Build the next layer of the tree
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(start_time, heuristic, depth - 1, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(start_time, heuristic, depth - 1, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return value, x, y

    def alphabeta(self, start_time, heuristic, depth=3, alpha=-10000, beta=10000, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = float('inf')
        if max:
            value = -value
        x = y = None

        # Not enough time left to evaluate
        if (self.t - (time.time() - start_time)) <= 0.001:
            return value, x, y

        # Evaluate heuristic at tree leaves or win/loss/tie
        result = self.is_end()
        if result == 'X':
            return heuristic() + value, x, y
        elif result == 'O':
            return heuristic() + value, x, y
        elif result == '.':
            return 0, x, y
        elif result is None and depth == 0:
            return heuristic(), x, y

        # Build the next layer of the tree
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(start_time, heuristic, depth - 1, alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(start_time, heuristic, depth - 1, alpha, beta, max=True)
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

        # Defaults
        if algo is None:
            algo = self.ALPHABETA
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN

        while True:
            self.draw_board()

            # Game over
            if self.check_end():
                return

            # Evaluate recommendation
            value = x = y = None
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (value, x, y) = self.minimax(start_time=start, heuristic=lambda: self.heuristic_simple(), depth=self.d1, max=False)
                else:
                    (value, x, y) = self.minimax(start_time=start, heuristic=lambda: self.heuristic_complex(), depth=self.d2, max=True)
            elif algo == self.ALPHABETA:
                if self.player_turn == 'X':
                    (value, x, y) = self.alphabeta(start_time=start, heuristic=lambda: self.heuristic_simple(), depth=self.d1, max=False)
                else:
                    (value, x, y) = self.alphabeta(start_time=start, heuristic=lambda: self.heuristic_complex(), depth=self.d2, max=True)
            if x is None or y is None:
                print("Checkmate! Any moves you play will result in a loss.")
                x, y = self.return_first_spot()
            end = time.time()

            # Player turn
            if (self.player_turn == 'X' and player_x == self.HUMAN) or \
                    (self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {self.get_letter(x)}, y = {y}')
                    print(F'Output value: value = {value}')
                (x, y) = self.input_move()

            # AI turn
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):

                # AI took too long to come up with a move
                if end - start > self.t:
                    print(F'Game Over! Player {self.player_turn} took too long to pick a move.')
                    print(F"Player {'O' if self.player_turn == 'X' else 'X'} wins!")
                    self.initialize_game()
                    return

                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {self.get_letter(x)}, y = {y}')

            # Play move and switch players
            self.current_state[x][y] = self.player_turn
            self.switch_player()

    def return_first_spot(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    return i, j
        return None


def main():
    g = Game(recommend=True)
    for _ in range(g.num_games):
        g.play(algo=Game.ALPHABETA if g.a else Game.MINIMAX,
               player_x=Game.HUMAN if g.game_mode in [1, 2] else Game.AI,
               player_o=Game.HUMAN if g.game_mode in [1, 3] else Game.AI)


if __name__ == "__main__":
    main()
