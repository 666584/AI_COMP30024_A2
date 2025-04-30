from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .agent_board import Agent_Board
from referee.game.board import CellState
import math
import copy
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
                        if jump_cell not in reachable_cells:
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
    
    while i < FROG_N:
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
        if board._state[Coord(0,c)] == CellState(PlayerColor.BLUE):
            num_blue = num_blue + 1
        c = c + 1
    if num_blue == 6:
        return True
    c = 0
    while c < BOARD_N:
        if board._state[Coord(7,c)] == CellState(PlayerColor.RED):
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
                eval = alpha_beta_search(new_board, depth-1, alpha, beta, False, other_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            else:
                for next_move in moves:
                    new_board = copy.deepcopy(board)
                    new_board = update_board(new_board, (frog, next_move), player)
                    eval = alpha_beta_search(new_board, depth-1, alpha, beta, False, other_player)
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
                    new_board = copy.deepcopy(board)
                    new_board = update_board(new_board, (frog, next_move), player)
                    eval = alpha_beta_search(new_board, depth-1, alpha, beta, True, other_player)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break 
        return min_eval   

# Find path of move
def find_path_by_move(move, frog, reachable_cells):
    possible_paths = reachable_cells.get(frog, [])
    for path in possible_paths:
        if isinstance(path, list) and path[-1] == move:
            return path
        elif not isinstance(path, list) and path == move:
            return [move]
    return []

# Determine next move by alpha-beta pruning and minmax search
def find_next_move(board, player):        
    
    max_score = -float('inf')
    next_move = None
    reachable_cells = get_reachable_cells(board, player)
    final_moves = get_final_moves(reachable_cells)
    
    for frog, moves in final_moves.items():
        if frog == "GROW":
            new_board = copy.deepcopy(board)
            new_board = update_board_grow(new_board, player)
            score = alpha_beta_search(new_board, 2, -float('inf'), float('inf'), False, player)
            if score > max_score:
                max_score = score
                next_move = "GROW"
        else: 
            for move in moves:
                new_board = copy.deepcopy(board)
                new_board = update_board(new_board, (frog, move), player)
                score = alpha_beta_search(new_board, 2, -float('inf'), float('inf'), False, player)
                if score > max_score:
                    max_score = score
                    paths = find_path_by_move(move, frog, reachable_cells)
                    next_move = (frog, paths)    
    
    return next_move

def find_direction(next_move):
    directions = []
    frog, moves = next_move
    x = frog.__getattribute__("r")
    y = frog.__getattribute__("c")
    for move in moves:
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