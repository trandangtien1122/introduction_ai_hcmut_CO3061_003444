import random
import time

import algorithms as al
import evaluations as ev


class VietnameseChess:
    def __init__(self, size: int):
        self.size = size
        self.board = [[0] * self.size for _ in range(self.size)]
        self.current_player = 1
        self.num_tiles = [2, 2]

    def init_board(self):
        if self.size < 2:
            return

        coord1 = int(self.size / 2 - 1)
        coord2 = int(self.size / 2)
        initial_squares = [(coord1, coord2), (coord1, coord1),
                           (coord2, coord1), (coord2, coord2)]

        for i in range(len(initial_squares)):
            color = i % 2
            row = initial_squares[i][0]
            col = initial_squares[i][1]
            if color == 0:
                self.board[row][col] = 1
            else:
                self.board[row][col] = -1

    def move_tile(self, move_location: tuple):
        if ev.is_legal_action(self.board, move_location, self.current_player):
            self.board[move_location[0]][move_location[1]] = self.current_player
            self.num_tiles[self.current_player] += 1
            self.flip_tiles(move_location)

    def flip_tiles(self, move_location: tuple):
        for direction in ev.MOVE_DIRS:
            if ev.has_tile_to_flip(self.board, move_location, direction, self.current_player):
                count = 1
                while True:
                    row = move_location[0] + direction[0] * count
                    col = move_location[1] + direction[1] * count
                    if self.board[row][col] != self.current_player:
                        self.board[row][col] = self.current_player
                        self.num_tiles[self.current_player] += 1
                        self.num_tiles[self.current_player * -1] -= 1
                        count += 1
                    else:
                        break

    def has_legal_action(self):
        for row in range(self.size):
            for col in range(self.size):
                if ev.is_legal_action(self.board, (row, col), self.current_player):
                    return True
        return False

    def print_begin_board(self):
        head = "  "
        for i in range(self.size):
            head += f" | {i}"
        print(head)
        for i, row in enumerate(self.board):
            str_row = str(i) + "  | "
            for j, tale in enumerate(row):
                if tale == -1:
                    str_row += "o | "
                elif tale == 1:
                    str_row += "x | "
                else:
                    str_row += "_ | "
            print(str_row)

    def print_new_state_board(self, move_location: tuple):
        print("Board:")
        head = "  "
        for i in range(self.size):
            head += f" | {i}"
        print(head)
        for i, row in enumerate(self.board):
            strow = str(i) + "   "
            for j, tale in enumerate(row):
                if i == move_location[0] and j == move_location[1]:
                    if tale == -1:
                        strow += "O | "
                    elif tale == 1:
                        strow += "X | "
                    else:
                        strow += "_ | "
                else:
                    if tale == -1:
                        strow += "o | "
                    elif tale == 1:
                        strow += "x | "
                    else:
                        strow += "_ | "
            print(strow)

    def playing_turn(self, evaluation_method: int, cur_state: list, player_to_move: int, remain_time=60):
        if player_to_move == 1:
            print("Player 1's turn:")
        else:
            print("Player 2's turn:")

        time_amount = -1
        if self.has_legal_action():
            start_time = time.perf_counter()
            move_location = self.select_move_location(evaluation_method, cur_state, player_to_move, remain_time)
            end_time = time.perf_counter()
            time_amount = end_time - start_time
            print("time: ", time_amount)
            if time_amount > 3:
                raise TimeoutError("time limit is 3s")
            if time_amount > remain_time:
                raise TimeoutError("total time limit is 60s")

            self.move_tile(move_location)
            self.print_new_state_board(move_location)
        else:
            print('no legal move.')
        print("=============================")
        return time_amount

    def run(self, player_1_mode: int, player_2_mode: int, is_player_1_agent: bool):
        num_moves = 120
        if self.current_player not in (-1, 1):
            raise ValueError(f'Player {self.current_player}')

        print("Game started:")
        self.print_begin_board()

        self.current_player = 1
        time_left_0 = 60
        time_left_1 = 60
        no_move = False
        for i in range(num_moves):
            if self.current_player == 1:
                time_amount = self.playing_turn(player_1_mode, self.board, 1, time_left_0)
                if time_amount < 0:
                    if no_move:
                        break
                    else:
                        no_move = True
                else:
                    no_move = False
                    time_left_0 -= time_amount
            else:
                time_amount = self.playing_turn(player_2_mode, self.board, -1, time_left_1)
                if time_amount < 0:
                    if no_move:
                        break
                    else:
                        no_move = True
                else:
                    no_move = False
                    time_left_1 -= time_amount
            self.current_player = -self.current_player

        print("=============================")
        player_1, player_2 = self.count_scores(self.board)
        if is_player_1_agent:
            agent_score = player_1
            rand_score = player_2
        else:
            agent_score = player_2
            rand_score = player_1
        if agent_score > rand_score:
            print("Your agent won!")
        else:
            print("Your agent lose!")
        print(f"Your agent score {agent_score}")
        print(f"Random agent score {rand_score}")

    @staticmethod
    def count_scores(board: list):
        count_1 = 0
        count_minus_1 = 0
        for row in board:
            for num in row:
                if num == 1:
                    count_1 += 1
                elif num == -1:
                    count_minus_1 += 1
        return count_1, count_minus_1

    @staticmethod
    def select_move_location(evaluation_method: int, current_state: list, player_to_move: int, remain_time=60):
        time_limit = 2.8
        if remain_time < 3:
            time_limit = 0.5
        if evaluation_method == 0:  # random
            moves = ev.get_legal_moves(current_state, player_to_move)
            if moves:
                return random.choice(moves)
            else:
                return None
        else:
            if evaluation_method == 1:  # simple table
                evaluate_func = ev.evaluate_simple_table
            elif evaluation_method == 2:  # good bad evaluate
                evaluate_func = ev.evaluate_good_bad
            elif evaluation_method == 3:  # corner table
                evaluate_func = ev.evaluate_corner
            else:
                raise ValueError(evaluation_method)
            move_location, _, _ = al.minimax(current_state, player_to_move, time_limit, float('-inf'), float('inf'), evaluate_func)
        return move_location


def go():
    board_size = int(input("Enter board size: "))
    game = VietnameseChess(board_size)
    game.init_board()
    print("Mode list:")
    print("1. Simple table algorithm")
    print("2. Good and bad algorithm")
    print("3. Corner algorithm (main)")
    print("---------------------")
    start_idx = int(input("Do your Agent go fist? \n 0: Yes \n 1: No \n"))
    if start_idx == 0:
        go_first = True
        player_1_mode = int(input("Enter mode id to gain the random : "))
        player_2_mode = 0
    else:
        go_first = False
        player_1_mode = 0
        player_2_mode = int(input("Enter mode id to gain the random : "))
    game.run(player_1_mode, player_2_mode, go_first)


if __name__ == "__main__":
    go()
