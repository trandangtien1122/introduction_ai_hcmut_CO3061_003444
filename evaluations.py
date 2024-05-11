import copy

MOVE_DIRS = [(-1, -1), (-1, 0), (-1, +1),
             (0, -1), (0, +1),
             (+1, -1), (+1, 0), (+1, +1)]

POINT_TABLE_GOOD_BAD = [[8, -4, 6, 6, 6, 6, -4, 8],
                        [-4, -4, -3, -3, -3, -3, -4, -4],
                        [6, -3, 1, 1, 1, 1, -3, 6],
                        [6, -3, 1, 2, 2, 1, -3, 6],
                        [6, -3, 1, 2, 2, 1, -3, 6],
                        [6, -3, 1, 1, 1, 1, -3, 6],
                        [-4, -4, -3, -3, -3, -3, -4, -4],
                        [8, -4, 6, 6, 6, 6, -4, 8]]

POINT_TABLE_0 = [[100, -100, 1, 1, 1, 1, -100, 100],
                 [-100, -100, -1, -1, -1, -1, -100, -100],
                 [1, -1, 1, -1, -1, 1, -1, 1],
                 [1, -1, -1, 1, 1, -1, -1, 1],
                 [1, -1, -1, 1, 1, -1, -1, 1],
                 [1, -1, 1, -1, -1, 1, -1, 1],
                 [-100, -100, -1, -1, -1, -1, -100, -100],
                 [100, -100, 1, 1, 1, 1, -100, 100]]

POINT_TABLE_1 = copy.deepcopy(POINT_TABLE_0)


def has_tile_to_flip(board: list, move_location: tuple, direction: tuple, player_to_move: int):
    i = 1
    if player_to_move in (-1, 1) and is_valid_coord(board, move_location[0], move_location[1]):
        curr_tile = player_to_move
        while True:
            row = move_location[0] + direction[0] * i
            col = move_location[1] + direction[1] * i
            if not is_valid_coord(board, row, col) or board[row][col] == 0:
                return False
            elif board[row][col] == curr_tile:
                break
            else:
                i += 1
        return i > 1


def make_move(board: list, move_location: tuple, player_to_move: int):
    new_board = [row.copy() for row in board]
    new_board[move_location[0]][move_location[1]] = player_to_move

    for direction in MOVE_DIRS:
        if has_tile_to_flip(new_board, move_location, direction, player_to_move):
            row, col = move_location[0] + direction[0], move_location[1] + direction[1]
            while new_board[row][col] == -player_to_move:
                new_board[row][col] = player_to_move
                row += direction[0]
                col += direction[1]
    return new_board


def is_valid_coord(board: list, row: int, col: int):
    size = len(board)
    return 0 <= row < size and 0 <= col < size


def is_legal_action(board: list, move_location: tuple, player_to_move: int):
    check_1 = len(move_location) > 0
    if not check_1:
        return False
    check_valid_coord = is_valid_coord(board, move_location[0], move_location[1])
    if not check_valid_coord:
        return False
    check_board = board[move_location[0]][move_location[1]] == 0
    if not check_board:
        return False
    check_flip = any(has_tile_to_flip(board, move_location, direction, player_to_move) for direction in MOVE_DIRS)
    if not check_flip:
        return False
    return True


def get_legal_moves(current_state: list, player_to_move: int):
    legal_moves = []
    size = len(current_state)
    for row in range(size):
        for col in range(size):
            if is_legal_action(current_state, (row, col), player_to_move):
                legal_moves.append((row, col))
    return legal_moves


def evaluate_final(board: list):
    total_tile = 0
    for row in board:
        for tile in row:
            total_tile += tile
    if total_tile > 0:
        return 10000 + total_tile
    elif total_tile < 0:
        return -10000 + total_tile
    else:
        return 0


def evaluate_simple_table(board: list, player_to_move: int):
    legal_moves = get_legal_moves(board, player_to_move)
    score = 0
    total_tile = 0
    for i, row in enumerate(board):
        for j, tile in enumerate(row):
            if tile != 0:
                total_tile += tile
                score += tile * POINT_TABLE_GOOD_BAD[i][j]
    return (2 * score + len(legal_moves) * player_to_move) * 10 + total_tile


def evaluate_good(move_location: tuple, board: list):
    tale = board[move_location[0]][move_location[1]]
    max_point = 0
    size = len(board)
    for direction in MOVE_DIRS:
        row, col = move_location
        row += direction[0]
        col += direction[1]
        if not is_valid_coord(board, row, col):
            break
        if board[row][col] == tale:
            break
        for _ in range(1, size):
            row += direction[0]
            col += direction[1]
            if is_valid_coord(board, row, col):
                if board[row][col] == tale:
                    break
                elif board[row][col] == 0 and POINT_TABLE_GOOD_BAD[row][col] > max_point:
                    max_point = POINT_TABLE_GOOD_BAD[row][col]
            else:
                break

    return max_point * tale


def evaluate_bad(move_location: tuple, board: list):
    tale = board[move_location[0]][move_location[1]]
    max_point = 0
    row, col = move_location
    for direction in MOVE_DIRS:
        row += direction[0]
        col += direction[1]
        if is_valid_coord(board, row, col) and board[row][col] == 0 and POINT_TABLE_GOOD_BAD[row][col] > max_point:
            max_point = POINT_TABLE_GOOD_BAD[row][col]

    return -tale * max_point * 2


def evaluate_good_bad(board: list, player_to_move: int):
    legal_moves = get_legal_moves(board, player_to_move)
    score = 0
    total_tile = 0
    for i, row in enumerate(board):
        for j, tile in enumerate(row):
            if tile != 0:
                total_tile += tile
                score += evaluate_good((i, j), board) + evaluate_bad((i, j), board)
    return 2 * score + 2 * player_to_move * len(legal_moves)


def evaluate_corner(board: list):
    score = 0
    total_tile = 0
    num_tile = 0

    if board[0][0] != 0:
        if board[0][0] == -1:
            POINT_TABLE_0[0][1] = 100
            POINT_TABLE_1[0][1] = 1

            POINT_TABLE_0[1][0] = 100
            POINT_TABLE_1[1][0] = 1

            POINT_TABLE_0[1][1] = 1
            POINT_TABLE_1[1][1] = 1
        elif board[0][0] == 1:
            POINT_TABLE_0[0][1] = 1
            POINT_TABLE_1[0][1] = 100

            POINT_TABLE_0[1][0] = 1
            POINT_TABLE_1[1][0] = 100

            POINT_TABLE_0[1][1] = 1
            POINT_TABLE_1[1][1] = 1

    if board[0][7] != 0:
        if board[0][7] == -1:
            POINT_TABLE_0[0][6] = 100
            POINT_TABLE_1[0][6] = 1

            POINT_TABLE_0[1][7] = 100
            POINT_TABLE_1[1][7] = 1

            POINT_TABLE_0[1][6] = 1
            POINT_TABLE_1[1][6] = 1
        elif board[0][7] == 1:
            POINT_TABLE_0[0][6] = 1
            POINT_TABLE_1[0][6] = 100

            POINT_TABLE_0[1][7] = 1
            POINT_TABLE_1[1][7] = 100

            POINT_TABLE_0[1][6] = 1
            POINT_TABLE_1[1][6] = 1

    if board[7][0] != 0:
        if board[7][0] == -1:
            POINT_TABLE_0[6][0] = 100
            POINT_TABLE_1[6][0] = 1

            POINT_TABLE_0[7][1] = 100
            POINT_TABLE_1[7][1] = 1

            POINT_TABLE_0[6][1] = 1
            POINT_TABLE_1[6][1] = 1
        elif board[7][0] == 1:
            POINT_TABLE_0[6][0] = 1
            POINT_TABLE_1[6][0] = 100

            POINT_TABLE_0[7][1] = 1
            POINT_TABLE_1[7][1] = 100

            POINT_TABLE_0[6][1] = 1
            POINT_TABLE_1[6][1] = 1

    if board[7][7] != 0:
        if board[7][7] == -1:
            POINT_TABLE_0[6][7] = 100
            POINT_TABLE_1[6][7] = 1

            POINT_TABLE_0[7][6] = 100
            POINT_TABLE_1[7][6] = 1

            POINT_TABLE_0[6][6] = 1
            POINT_TABLE_1[6][6] = 1
        elif board[0][0] == 1:
            POINT_TABLE_0[6][7] = 1
            POINT_TABLE_1[6][7] = 100

            POINT_TABLE_0[7][6] = 1
            POINT_TABLE_1[7][6] = 100

            POINT_TABLE_0[6][6] = 1
            POINT_TABLE_1[6][6] = 1

    for i, row in enumerate(board):
        for j, tile in enumerate(row):
            total_tile += tile
            if tile == -1:
                num_tile += 1
                score += tile * POINT_TABLE_0[i][j]
            elif tile == 1:
                num_tile += 1
                score += tile * POINT_TABLE_1[i][j]
    return score + 3 * total_tile / (65 - num_tile)
