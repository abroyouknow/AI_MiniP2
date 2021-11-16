# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python
import sys
import time

counter = 4


def iota():
    global counter
    counter += 1
    return counter


class Game:
    # Game Modes
    H_VS_H = 1
    H_VS_AI = 2
    AI_VS_H = 3
    AI_VS_AI = 4

    # Algorithms
    MINIMAX = iota()
    ALPHABETA = iota()

    # Heuristics
    HEURISTIC_SIMPLE = iota()
    HEURISTIC_COMPLEX = iota()

    # Player modes
    HUMAN = iota()
    AI = iota()

    # Private variables
    n = 0
    s = 1
    b = -1
    d1 = 0
    t = 0
    d2 = 0
    temp1 = 0
    temp2 = 0
    a1 = False
    a2 = False
    game_mode = 0
    current_state = []
    block_coords = []

    # game statstics counters
    num_move = 0
    total_eval_time = 0
    total_heuristic_eval_count = 0
    total_ard = 0
    total_depth_map = {}
    total_avg_eval_depth = 0

    # scoreboard statstics counters
    total_win_h1 = 0
    total_win_h2 = 0
    total_game_eval_time = 0
    total_game_heuristic_eval_count = 0
    total_game_avg_eval_depth = 0
    total_game_ard = 0
    total_game_depth_map = {}
    total_game_moves = 0

    def __init__(self, recommend=True):
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

        # Boolean for use of minimax or alphabeta
        while self.temp1 < 1 or self.temp1 > 2:
            print()
            print('Which type of adversarial search should the player 1 implement?')
            print('\t1- Minimax')
            print('\t2- Alpha-Beta')
            self.temp1 = int(input('Enter the number associated with your choice: '))
        self.a1 = self.temp1 == 2

        while self.temp2 < 1 or self.temp2 > 2:
            print()
            print('Which type of adversarial search should the player 2 implement?')
            print('\t1- Minimax')
            print('\t2- Alpha-Beta')
            self.temp2 = int(input('Enter the number associated with your choice: '))
        self.a2 = self.temp2 == 2

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

    def check_end(self, heuristic_x, heuristic_o):
        result = self.is_end()
        # Printing the appropriate message if the game has ended
        if result is not None:
            if result == 'X':
                if heuristic_x == self.HEURISTIC_SIMPLE:
                    self.total_win_h1 += 1
                else:
                    self.total_win_h2 += 1
                print('The winner is X!')
            elif result == 'O':
                if heuristic_o == self.HEURISTIC_SIMPLE:
                    self.total_win_h1 += 1
                else:
                    self.total_win_h2 += 1
                print('The winner is O!')
            elif result == '.':
                print("It's a tie!")
            self.print_and_accumulate_game_statistics()
        return result

    def input_move(self):
        while True:
            print()
            print(F'Player {self.player_turn}, enter your move:')
            px = self.get_index(input(F'Enter the x coordinate (A-{self.get_letter(self.n - 1)}): '))
            py = int(input(F'Enter the y coordinate (0-{self.n - 1}): '))
            if self.is_valid(px, py):
                return px, py
            else:
                print('The move is not valid! Try again.')

    def input_block(self):
        block_count = len(self.block_coords)
        if block_count <= 0:
            self.draw_board()
        while block_count < self.b:
            print()
            print('Enter the location of the block to be placed:')
            px = self.get_index(input(F'Enter the x coordinate (A-{self.get_letter(self.n - 1)}): '))
            py = int(input(F'Enter the y coordinate (0-{self.n - 1}): '))
            if self.is_valid(px, py):
                self.current_state[px][py] = '*'
                self.block_coords.append((px, py))
                block_count += 1
                self.draw_board()
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

    def minimax(self, start_time, heuristic, depth_map, depth=3, max_depth=3, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # We're initially setting it to inf or -inf as the worst case
        value = float('inf')
        if max:
            value = -value
        x = y = None

        # Calculate depth
        current_depth = max_depth - depth
        if depth_map.get(current_depth) is None:
            depth_map[current_depth] = 1
        else:
            depth_map[current_depth] += 1

        # Not enough time left to evaluate
        if (self.t - (time.time() - start_time)) <= 0.002:
            return value, current_depth, x, y

        # Evaluate heuristic at tree leaves or win/loss/tie
        result = self.is_end()
        if result == 'X':
            return value, current_depth, x, y
        elif result == 'O':
            return value, current_depth, x, y
        elif result == '.':
            return 0, current_depth, x, y
        elif result is None and depth == 0:
            return heuristic(), current_depth, x, y

        # Build the next layer of the tree
        count = 0
        ard_sum = 0
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, ard, _, _) = self.minimax(start_time=start_time, heuristic=heuristic, depth_map=depth_map,
                                                      depth=depth - 1, max_depth=max_depth, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, ard, _, _) = self.minimax(start_time=start_time, heuristic=heuristic, depth_map=depth_map,
                                                      depth=depth - 1, max_depth=max_depth, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    ard_sum += ard
                    count += 1

        # Propagate H, ARD, and move upwards
        return value, ard_sum / count, x, y

    def alphabeta(self, start_time, heuristic, depth_map, depth=3, max_depth=3, alpha=-float('inf'), beta=float('inf'),
                  max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # We're initially setting it to inf or -inf as the worst case
        value = float('inf')
        if max:
            value = -value
        x = y = None

        # Calculate depth
        current_depth = max_depth - depth
        if depth_map.get(current_depth) is None:
            depth_map[current_depth] = 1
        else:
            depth_map[current_depth] += 1

        # Not enough time left to evaluate
        if (self.t - (time.time() - start_time)) <= 0.002:
            return value, current_depth, x, y

        # Evaluate heuristic at tree leaves or win/loss/tie
        result = self.is_end()
        if result == 'X':
            return value, current_depth, x, y
        elif result == 'O':
            return value, current_depth, x, y
        elif result == '.':
            return 0, current_depth, x, y
        elif result is None and depth == 0:
            return heuristic(), current_depth, x, y

        # Build the next layer of the tree
        count = 0
        ard_sum = 0
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, ard, _, _) = self.alphabeta(start_time, heuristic, depth_map, depth - 1, max_depth, alpha,
                                                        beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, ard, _, _) = self.alphabeta(start_time, heuristic, depth_map, depth - 1, max_depth, alpha,
                                                        beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    ard_sum += ard
                    count += 1
                    # Alpha-Beta pruning
                    if max:
                        if value >= beta:
                            return value, ard_sum / count, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, ard_sum / count, x, y
                        if value < beta:
                            beta = value

        # Propagate H, ARD, and move upwards
        return value, ard_sum / count, x, y

    def play(self, algo_x=None, algo_o=None, heuristic_x=None, heuristic_o=None, player_x=None, player_o=None,
             swap=False):

        # Defaults
        if algo_x is None:
            algo_x = self.ALPHABETA
        if algo_o is None:
            algo_o = self.MINIMAX
        if heuristic_x is None:
            heuristic_x = self.HEURISTIC_SIMPLE
        if heuristic_o is None:
            heuristic_o = self.HEURISTIC_SIMPLE
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN

        # Swap players if needed
        if swap:
            algo_x, algo_o = algo_o, algo_x
            heuristic_x, heuristic_o = heuristic_o, heuristic_x
            player_x, player_o = player_o, player_x

        # Pick heuristic functions for each player
        if heuristic_x == Game.HEURISTIC_SIMPLE:
            hx_fn = lambda: self.heuristic_simple()
        else:
            hx_fn = lambda: self.heuristic_complex()
        if heuristic_o == Game.HEURISTIC_SIMPLE:
            ho_fn = lambda: self.heuristic_simple()
        else:
            ho_fn = lambda: self.heuristic_complex()

        # Game loop
        while True:
            self.draw_board()

            # Game over
            if self.check_end(heuristic_x, heuristic_o):
                return

            # Evaluate recommendation
            value = ard = x = y = None
            start = time.time()
            depth_map = {}
            if self.player_turn == 'X' and algo_x == self.MINIMAX:
                (value, ard, x, y) = self.minimax(start_time=start, heuristic=hx_fn, depth_map=depth_map,
                                                  depth=self.d1, max_depth=self.d1, max=False)
            elif self.player_turn == 'X' and algo_x == self.ALPHABETA:
                (value, ard, x, y) = self.alphabeta(start_time=start, heuristic=hx_fn, depth_map=depth_map,
                                                    depth=self.d1, max_depth=self.d1, max=False)
            elif self.player_turn == 'O' and algo_o == self.MINIMAX:
                (value, ard, x, y) = self.minimax(start_time=start, heuristic=ho_fn, depth_map=depth_map,
                                                  depth=self.d2, max_depth=self.d2, max=True)
            elif self.player_turn == 'O' and algo_o == self.ALPHABETA:
                (value, ard, x, y) = self.alphabeta(start_time=start, heuristic=ho_fn, depth_map=depth_map,
                                                    depth=self.d2, max_depth=self.d2, max=True)
            if x is None or y is None:
                print("Checkmate! Any moves you play will result in a loss.")
                x, y = self.return_first_spot()
            end = time.time()

            # Player turn
            if (self.player_turn == 'X' and player_x == self.HUMAN) or \
                    (self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Recommended move: {self.get_letter(x)}{y}')
                    print(F'Output value: value = {value}')
                (x, y) = self.input_move()

            # AI turn
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):

                # AI took too long to come up with a move
                if end - start > self.t:
                    print(F'Game Over! Player {self.player_turn} took too long to pick a move.')
                    print(F"The winner is {'O' if self.player_turn == 'X' else 'X'}!")
                    return

                print(F'Player {self.player_turn} under AI control plays: {self.get_letter(x)}{y}')

            # Print move statistics and increment move counter
            evaluation_time = round(end - start, 7)
            self.print_and_accumulate_move_statistics(evaluation_time, depth_map, ard)
            self.num_move += 1

            # Play move and switch players
            self.current_state[x][y] = self.player_turn
            self.switch_player()

    def return_first_spot(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] == '.':
                    return i, j
        return None

    def print_and_accumulate_move_statistics(self, evaluation_time, depth_map, ard):
        count = sum(depth_map.values())
        avg_eval_depth = sum(map(lambda k, v: k * v, depth_map.keys(), depth_map.values())) / count
        print(F'i\tEvaluation time: {round(evaluation_time, 7)}')
        print(F'ii\tHeuristic evaluations: {sum(depth_map.values())}')
        print(F'iii\tEvaluations by depth: {depth_map}')
        print(F'iv\tAverage evaluation depth: {round(avg_eval_depth, 4)}')
        print(F'v\tAverage recursion depth: {round(ard, 4)}')

        self.num_move += 1
        self.total_eval_time += evaluation_time
        self.total_heuristic_eval_count += count
        self.total_ard += ard
        self.total_avg_eval_depth += avg_eval_depth

        for depth, count in depth_map.items():
            if self.total_depth_map.get(depth) is None:
                self.total_depth_map[depth] = count
            else:
                depth_map[depth] += count

    def print_and_accumulate_game_statistics(self):
        print(F'i\tAverage evaluation time: {round(self.total_eval_time / self.num_move, 7)}')
        print(F'ii\tTotal heuristic evaluations: {self.total_heuristic_eval_count}')
        print(F'iii\tEvaluations by depth: {self.total_depth_map}')
        print(F'iv\tAverage evaluation depth: {round(self.total_avg_eval_depth / self.num_move, 4)}')
        print(F'v\tAverage recursion depth: {round(self.total_ard / self.num_move, 4)}')
        print(F'vi\tTotal moves: {self.num_move}')

        self.total_game_eval_time += self.total_eval_time
        self.total_game_heuristic_eval_count += self.total_eval_time
        self.total_game_ard += self.total_ard
        self.total_game_avg_eval_depth += self.total_avg_eval_depth
        self.total_game_moves += self.num_move

        for depth, count in self.total_depth_map.items():
            if self.total_game_depth_map.get(depth) is None:
                self.total_depth_map[depth] = count
            else:
                self.total_game_depth_map[depth] += count

        self.total_eval_time = 0
        self.total_eval_time = 0
        self.total_ard = 0
        self.total_avg_eval_depth = 0
        self.num_move = 0
        self.total_depth_map = {}

    def print_scoreboard(self, r):
        num_games = 2 * r

        print(F'n={self.n} b={self.b} s={self.s} t={self.t}')
        print('\n')
        print(F'Player 1: d={self.d1} a={self.a1}')
        print(F'Player 2: d={self.d2} a={self.a2}')
        print('\n')
        print(F'{num_games} game(s)')
        print('\n')
        print(F'Total wins for heuristic e1: {self.total_win_h1} ({self.total_win_h1 / num_games * 100}%) (simple)')
        print(F'Total wins for heuristic e2: {self.total_win_h2} ({self.total_win_h2 / num_games * 100}%) (complex)')
        print('\n')
        print(F'i\tAverage Evaluation time: {self.total_game_eval_time / num_games}')
        print(F'ii\tTotal Heuristic evaluation: {self.total_game_heuristic_eval_count}')
        print(F'iii\tEvaluations by depth: {self.total_game_depth_map}')
        print(F'iv\tAverage evaluation depth: {self.total_game_avg_eval_depth / num_games}')
        print(F'v\tAverage recursion depth: {self.total_game_ard / num_games}')
        print(F'vi\tAverage total moves: {self.total_game_moves / num_games}')


def main():
    g = Game(recommend=True)

    # Number of games to play
    r = 0
    while r < 1:
        print()
        r = int(input('Enter the number of games you wish to play: '))

    console = sys.stdout

    for i in range(2 * r):
        # Init game in console
        sys.stdout = console
        g.initialize_game()

        # Switch to file for game trace
        if g.game_mode == Game.AI_VS_AI:
            # Open output file and redirect stdout to it
            game_file = open(F'../results/gameTrace-{g.n}{g.b}{g.s}{g.t}-{i}.txt', 'w')
            sys.stdout = game_file

        # Draw initial board
        swap = i & 0x1 == 1
        print(F'n = {g.n} b = {g.b} s = {g.s} t = {g.t}')
        print(F'blocks = {g.block_coords}')
        print('\n')
        print(F"Player 1: d = {g.d1} a = {g.a1} heuristic = {'simple' if not swap else 'complex'}")
        print(F"Player 2: d = {g.d1} a = {g.a1} heuristic = {'simple' if swap else 'complex'}")
        print('\n')
        g.play(algo_x=Game.ALPHABETA if g.a1 else Game.MINIMAX,
               algo_o=Game.ALPHABETA if g.a2 else Game.MINIMAX,
               heuristic_x=Game.HEURISTIC_SIMPLE,
               heuristic_o=Game.HEURISTIC_COMPLEX,
               player_x=Game.HUMAN if g.game_mode in [Game.H_VS_H, Game.H_VS_AI] else Game.AI,
               player_o=Game.HUMAN if g.game_mode in [Game.H_VS_H, Game.AI_VS_H] else Game.AI,
               swap=swap)

    if g.game_mode == Game.AI_VS_AI:
        # Open output file and redirect stdout to it
        score_board_file = open(F'../results/scoreboard-{g.n}{g.b}{g.s}{g.t}.txt', 'w')
        sys.stdout = score_board_file

    g.print_scoreboard(r)

if __name__ == "__main__":
    main()
