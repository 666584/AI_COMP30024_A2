from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .agent_board import Agent_Board
from referee.game.board import CellState
import math
import copy
import time

BOARD_N = 8
FROG_N = 6
RED_DIRECTION = [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]
BLUE_DIRECTION = [Direction.Up, Direction.UpLeft, Direction.UpRight, Direction.Left, Direction.Right]
GROW_DIRECTION = [Direction.Up, Direction.UpLeft, Direction.UpRight, Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]


# Find list of positions of all frogs 
def find_all_frog_position(agent_board, player):
    frog_position_list = []
    r = 0
    c = 0
    while r < BOARD_N:
        while c < BOARD_N:
            cell_state = agent_board._state[Coord(r, c)].state
            if cell_state == player: 
                frog_position_list.append(Coord(r, c))
            c = c + 1
        c = 0
        r = r + 1
    return frog_position_list

# Find all jumpable moves 
def get_jump_cells(curr_frog, next_move, agent_board, directions):
    jump_cells_list = []
    visited = set()
    x = curr_frog.__getattribute__("r")
    y = curr_frog.__getattribute__("c")
    i = next_move.__getattribute__("r")
    j = next_move.__getattribute__("c")
    r = i - (x - i)
    c = j - (y - j)

    def dfs(curr_frog, jump):
        for direction in directions: 
            try:
                next_move = curr_frog.__add__(direction)
                state = agent_board._state[next_move].state
                
                if state == PlayerColor.BLUE or state == PlayerColor.RED:
                    x = curr_frog.__getattribute__("r")
                    y = curr_frog.__getattribute__("c")
                    i = next_move.__getattribute__("r")
                    j = next_move.__getattribute__("c")
                    r = i - (x - i)
                    c = j - (y - j)
                    try:
                        jump_cell = Coord(r,c)
                        state = agent_board._state[jump_cell].state
                        
                        if state == "LilyPad" and jump_cell not in visited:
                            new_jumps = jump + [jump_cell]
                            jump_cells_list.append(new_jumps)
                            visited.add(jump_cell)
                            dfs(jump_cell, new_jumps)
                    except ValueError:
                        continue
            except ValueError:
                continue
    try:
        jump_cell = Coord(r,c)
        state = agent_board._state[jump_cell].state
        if state == "LilyPad":
            first_jump = [jump_cell]
            jump_cells_list.append(first_jump)
            visited.add(jump_cell)         
            dfs(jump_cell, first_jump)
    except ValueError:
        return None
    return jump_cells_list

# Find list of cells that player can move next for each frog
def find_reachable_cells(curr_frog, agent_board, directions):
    reachable_cells = []
    
    for direction in directions:
        try:
            next_move = curr_frog.__add__(direction)            
            state = agent_board._state[next_move].state
            if (state == "LilyPad"):
                reachable_cells.append(next_move)
            elif (state == PlayerColor.BLUE or state == PlayerColor.RED):
                jump_cell_list = get_jump_cells(curr_frog, next_move, agent_board, directions)
                if jump_cell_list:
                    for jump_cell in jump_cell_list:
                        reachable_cells.append(jump_cell)        
        except ValueError:
            continue
    
    return reachable_cells

# Get dictionary of all cells that player can move next
def get_reachable_cells(board, player):
    reachable_cells = {}
    frog_position_list = find_all_frog_position(board, player)

    i = 0
    
    if player == PlayerColor.RED:
        direction  = RED_DIRECTION
    else :
        direction = BLUE_DIRECTION
    
    while i < len(frog_position_list):
        reachable_cell = find_reachable_cells(frog_position_list[i], board, direction)
        if reachable_cell:
            reachable_cells[frog_position_list[i]] = reachable_cell
        i = i + 1
    reachable_cells["GROW"] = None
    return reachable_cells

# Evaluate each move with score
def evaluate(board, player):
    frogs = find_all_frog_position(board, player)
    other_player = get_other_player(player)
    other_frogs = find_all_frog_position(board, other_player)
    value = 0
    if player == PlayerColor.RED:
        goal = 7
    else:
        goal = 0
    # Number of player's frogs can move
    reachable_cells = get_reachable_cells(board, player)
    value = value + len(reachable_cells) 
   
    # How close player's frogs are to the goal
    for frog in frogs:
        x = frog.__getattribute__("r")
        if player == PlayerColor.RED:
            value = value + x
        else:
            value = value + (7 - x)
    # Number of player's frogs at goal 
    for frog in frogs:
        x = frog.__getattribute__("r")
        if x == goal:
            value = value + 10
    # Number of other player's frogs at goal
    for frog in other_frogs:
        x = frog.__getattribute__("r")
        if x == goal:
            value = value - 10
    # Number of other player's frogs can move
    reachable_cells_other = get_reachable_cells(board, other_player)
    value = value - len(reachable_cells_other) 
    return value

# Determine if the game is end or not 
def is_terminal(board):
    c = 0
    num_blue = 0
    num_red = 0
    while c < BOARD_N:
        if board._state[Coord(0,c)].state == PlayerColor.BLUE:
            num_blue = num_blue + 1
        c = c + 1
    if num_blue == 6:
        return True
    c = 0
    while c < BOARD_N:
        if board._state[Coord(7,c)].state == PlayerColor.RED:
            num_red = num_red + 1
        c = c + 1
    if num_red == 6:
        return True
    return False

# Update board
def update_board(board, next_move, player):
    frog, move = next_move
    board._state[move] = CellState(player)
    board._state[frog] = CellState(None)
    return board

# Update board with grow action
def update_board_grow(board, player):
    frogs = find_all_frog_position(board, player)
    for frog in frogs:
        for direction in GROW_DIRECTION:
            try:
                grow_cell = frog.__add__(direction) 
                if board._state[grow_cell].state == None:
                    board._state[grow_cell] = CellState("LilyPad")
            except ValueError:
                continue
    return board
    
# Get opponent
def get_other_player(player):
    if player == PlayerColor.RED:
        return PlayerColor.BLUE
    else:
        return PlayerColor.RED

# Get only final destination of jump action
def get_final_moves(reachable_moves):
    final_moves = {}
    for frog, moves in reachable_moves.items():
        if frog == "GROW":
            final_moves[frog] = None
            continue
        final_move = []
        for move in moves:
            if isinstance(move, list):
                if move:
                    final_move.append(move[-1])
            else:
                final_move.append(move)
        final_moves[frog] = final_move
    return final_moves   

# Check if move is valid
def is_valid_move(board, frog, move):
    """
    Check if a move from frog to move is valid:
    - The destination must not have a frog (RED or BLUE)
    - Must be a LilyPad
    """
    try:
        if not move:
            return False
        dest_state = board._state[move].state
        
        # If position has one frog exist, not valid
        if dest_state == PlayerColor.RED or dest_state == PlayerColor.BLUE:
            return False
        return dest_state == "LilyPad"
    except ValueError:
        return False

# Check if path is valid
def is_valid_path(board, frog, path):
    if not path:
        return False
    if not isinstance(path, list):
        return is_valid_move(board, frog, path)
    final_destination = path[-1] if path else None
    return is_valid_move(board, frog, final_destination)

# Find all valid path
def find_path_by_move(move, frog, reachable_cells):
    possible_paths = reachable_cells.get(frog, [])
    for path in possible_paths:
        if isinstance(path, list):
            # Jump
            if path and path[-1] == move:
                return path
        elif path == move:
            # Move
            return [path]
    return []

def alpha_beta_search(board, depth, alpha, beta, maximizing_player, player):
    if depth == 0 or is_terminal(board):
        return evaluate(board, player)
    
    other_player = get_other_player(player)
    if maximizing_player:
        max_eval = float('-inf')
        reachable_moves = get_reachable_cells(board, player)
        reachable_moves = get_final_moves(reachable_moves)
        for frog, moves in reachable_moves.items():
            if frog == "GROW":
                new_board = copy.deepcopy(board)
                new_board = update_board_grow(new_board, player)
                eval = alpha_beta_search(new_board, depth-1, alpha, beta, False, player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            else:
                for next_move in moves:
                    if not is_valid_move(board, frog, next_move):
                        continue
                        
                    new_board = copy.deepcopy(board)
                    new_board = update_board(new_board, (frog, next_move), player)
                    eval = alpha_beta_search(new_board, depth-1, alpha, beta, False, player)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:                        
                        break
        return max_eval
    
    else:
        min_eval = float('inf')
        reachable_moves = get_reachable_cells(board, player)        
        reachable_moves = get_final_moves(reachable_moves)
        for frog, moves in reachable_moves.items():
            if frog == "GROW":
                new_board = copy.deepcopy(board)
                new_board = update_board_grow(new_board, player)
                eval = alpha_beta_search(new_board, depth-1, alpha, beta, True, other_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            else: 
                for next_move in moves:
                    if not is_valid_move(board, frog, next_move):
                        continue
                        
                    new_board = copy.deepcopy(board)
                    new_board = update_board(new_board, (frog, next_move), player)
                    eval = alpha_beta_search(new_board, depth-1, alpha, beta, True, other_player)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break 
        return min_eval   

def find_direction(next_move):
    if next_move == "GROW":
        return None
        
    frog, moves = next_move
    if not moves:
        return []
        
    if not isinstance(moves, list):
        moves = [moves]
        
    directions = []
    x = frog.__getattribute__("r")
    y = frog.__getattribute__("c")
    
    for move in moves:
        if move is None:
            continue
            
        i = move.__getattribute__("r")
        j = move.__getattribute__("c")    
        r = i - x
        c = j - y
        if r != 0:
            r = int(r // abs(r))
        if c != 0:
            c = int(c // abs(c))
        directions.append(Direction(r, c))
        x = i
        y = j
    
    return directions

def find_cell(board, action):
    match action:
        case MoveAction(coord, dirs):
            x = coord.__getattribute__("r")
            y = coord.__getattribute__("c")
            r = 0
            c = 0
            for dir in dirs:
                i = dir.__getattribute__("r")
                j = dir.__getattribute__("c")
                r = r + i
                c = c + j
                state = board._state[Coord(r + x, c + y)].state
                if state == PlayerColor.BLUE or state == PlayerColor.RED:
                    r = r + i
                    c = c + j
            return (coord, Coord(r + x, c + y))
        case GrowAction():
            return "GROW"
        
# Evaluate distance to target
def heuristic(board, player):
    frogs = find_all_frog_position(board, player)
    value = 0
    
    if player == PlayerColor.RED:
        goal_row = 7
    else:
        goal_row = 0
    
    # Caculate distance to target for each frog
    for frog in frogs:
        row = frog.__getattribute__("r")
        if player == PlayerColor.RED:
            distance = goal_row - row
        else:
            distance = row - goal_row
        value += distance
    
    return value

# A* to find the best path
def astar_search(board, player, max_depth=3):
    import heapq
    
    initial_state = (board, None, None)
    
    # Store all visited path
    visited = set()
    
    # User priority queue
    state_counter = 0
    queue = [(heuristic(board, player), 0, state_counter, initial_state)]
    state_counter += 1
    
    g_score = {str(board._state): 0}
    
    best_action = None
    best_score = float('-inf')
    
    while queue and len(queue) < 1000:  
        f_score, depth, _, (current_board, frog, move) = heapq.heappop(queue)
        
        board_str = str(current_board._state)
        if board_str in visited:
            continue
        visited.add(board_str)
        
        if depth >= max_depth or is_terminal(current_board):
            current_score = evaluate(current_board, player)
            if current_score > best_score:
                best_score = current_score
                best_action = (frog, move)
            continue
        
        # Find all possible movements
        reachable_moves = get_reachable_cells(current_board, player)
        final_moves = get_final_moves(reachable_moves)
        
        # Generate next possible movement
        for next_frog, moves in final_moves.items():
            if next_frog == "GROW":
                new_board = copy.deepcopy(current_board)
                new_board = update_board_grow(new_board, player)
                
                new_g_score = g_score[board_str] + 1
                new_board_str = str(new_board._state)
                
                if new_board_str not in g_score or new_g_score < g_score[new_board_str]:
                    g_score[new_board_str] = new_g_score
                    h_score = heuristic(new_board, player)
                    f_score = new_g_score + h_score
                    
                    # Add to queue
                    next_state = (new_board, "GROW", None)
                    heapq.heappush(queue, (f_score, depth + 1, state_counter, next_state))
                    state_counter += 1
                    
                    # If it's first movement
                    if depth == 0:
                        current_score = evaluate(new_board, player)
                        if current_score > best_score:
                            best_score = current_score
                            best_action = "GROW"
            else:
                if moves:
                    for next_move in moves:
                        # Skip all invalid move
                        if not is_valid_move(current_board, next_frog, next_move):
                            continue
                            
                        # Find best path
                        paths = find_path_by_move(next_move, next_frog, reachable_moves)
                        if paths:
                            new_board = copy.deepcopy(current_board)
                            new_board = update_board(new_board, (next_frog, next_move), player)
                            
                            new_g_score = g_score[board_str] + 1
                            new_board_str = str(new_board._state)
                            
                            if new_board_str not in g_score or new_g_score < g_score[new_board_str]:
                                g_score[new_board_str] = new_g_score
                                h_score = heuristic(new_board, player)
                                f_score = new_g_score + h_score
                                
                                # Add to queue
                                next_state = (new_board, next_frog, paths)
                                heapq.heappush(queue, (f_score, depth + 1, state_counter, next_state))
                                state_counter += 1
                                
                                if depth == 0:
                                    current_score = evaluate(new_board, player)
                                    if current_score > best_score:
                                        best_score = current_score
                                        best_action = (next_frog, paths)
    
    return best_action
# Find the best movement for current frog
def find_next_move(board, player, timer=None):
    # Record score of all movements
    move_scores = {}
    reachable_cells = get_reachable_cells(board, player)
    final_moves = get_final_moves(reachable_cells)
    for frog, moves in final_moves.items():
        if frog != "GROW" and moves:
            for move in moves:
                if is_valid_move(board, frog, move):
                    path = find_path_by_move(move, frog, reachable_cells)
                    if path:
                        # Evaluate score
                        new_board = copy.deepcopy(board)
                        new_board = update_board(new_board, (frog, move), player)
                        score = evaluate(new_board, player)
                        move_scores[(frog, tuple(path))] = score
    
    new_board = copy.deepcopy(board)
    new_board = update_board_grow(new_board, player)
    grow_score = evaluate(new_board, player)
    move_scores["GROW"] = grow_score
    
    if move_scores:
        best_move = max(move_scores.items(), key=lambda x: x[1])[0]
        if best_move == "GROW":
            return "GROW"
        else:
            frog, path = best_move
            if not isinstance(path, list):
                path = list(path)
            return (frog, path)

    return "GROW"