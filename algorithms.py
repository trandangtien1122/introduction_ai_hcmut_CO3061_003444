import time

import evaluations as ev


def minimax(current_state: list, player_to_move: int, time_limit: float,
            alpha: float, beta: float, eval_func, no_legal=False):
    start_time = time.perf_counter()

    # minimax algorithm
    if time_limit <= 0.005:
        return None, eval_func(current_state, player_to_move), 0

    legal_moves = ev.get_legal_moves(current_state, player_to_move)

    if len(legal_moves) == 0:
        if no_legal:
            time_amount = time.perf_counter() - start_time
            time_spare = 0 if time_amount > time_limit else time_limit - time_amount
            return None, ev.evaluate_final(current_state), time_spare
        else:
            return minimax(current_state, -player_to_move, time_limit, alpha, beta, eval_func, True)

    time_slot = time_limit / len(legal_moves)

    best_move = None

    if player_to_move == 1:
        max_value = float('-inf')
        for i, move in enumerate(legal_moves):
            new_state = ev.make_move(current_state, move, player_to_move)
            _, value, time_spare = minimax(new_state, -player_to_move, time_slot, alpha, beta, eval_func)
            if i + 1 < len(legal_moves):
                time_slot += time_spare / (len(legal_moves) - (i + 1))
            if value > max_value:
                max_value = value
                best_move = move
            alpha = max(alpha, value)
            if beta <= alpha:
                break

        time_amount = time.perf_counter() - start_time
        time_spare = 0 if time_amount > time_limit else time_limit - time_amount
        return best_move, max_value, time_spare
    else:
        min_value = float('inf')
        for i, move in enumerate(legal_moves):
            new_state = ev.make_move(current_state, move, player_to_move)
            _, value, time_spare = minimax(new_state, -player_to_move, time_slot, alpha, beta, eval_func)
            if i + 1 < len(legal_moves):
                time_slot += time_spare / (len(legal_moves) - (i + 1))
            if value < min_value:
                min_value = value
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break

        time_amount = time.perf_counter() - start_time
        time_spare = 0 if time_amount > time_limit else time_limit - time_amount
        return best_move, min_value, time_spare
