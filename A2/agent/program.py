# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent 

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .function import *
from .agent_board import Agent_Board
from referee.game.board import CellState
import time


class Timer:
    def __init__(self):
        self.start_time = None
        self.total_time = 0.0
        self.move_count = 0
        self.time_per_move = {}
        self.game_start_time = time.time() 

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.total_time += elapsed
            self.move_count += 1
            self.time_per_move[self.move_count] = elapsed
            self.start_time = None
            return elapsed
        return 0.0

    def get_total_time(self):
        return self.total_time

    def get_game_total_time(self):
        return time.time() - self.game_start_time

    def get_average_time(self):
        if self.move_count == 0:
            return 0.0
        return self.total_time / self.move_count

    def print_final_stats(self):
        game_time = self.get_game_total_time()
        print(f"\nGame Performance:")
        print(f"Total Game Time: {game_time:.4f} seconds")
        print(f"Number of Moves: {self.move_count}")
        print(f"Average Time per Move: {self.get_average_time():.4f} seconds")

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Freckers game events.
    """
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")
        self.agent_board = Agent_Board(color)
        self.timer = Timer()
        
    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        
        """
        self.timer.start()
        next_move = find_next_move(self.agent_board, self._color, self.timer)
        elapsed = self.timer.stop()
        
        if next_move == "GROW":
            return GrowAction()
        else:
            # Checks if path valids
            frog, path = next_move
            if path:
                directions = []
                current = frog
                
                if not isinstance(path, list):
                    path = [path]
                
                for move in path:
                    if move:
                        # Caculate vector
                        r_diff = move.__getattribute__("r") - current.__getattribute__("r")
                        c_diff = move.__getattribute__("c") - current.__getattribute__("c")
                        
                        # Normalize vector
                        if r_diff != 0:
                            r_diff = r_diff // abs(r_diff)
                        if c_diff != 0:
                            c_diff = c_diff // abs(c_diff)
                            
                        # Add direction
                        directions.append(Direction(r_diff, c_diff))
                        current = move
                
                if directions:
                    return MoveAction(frog, directions)
            
            # If the path not valid, grow
            print("WARNING: Invalid path, defaulting to GROW")
            return GrowAction()
    
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after a player has taken their
        turn. You should use it to update the agent's internal game state.
        
        """
        next_move = find_cell(self.agent_board, action)
        if next_move == "GROW":
            update_board_grow(self.agent_board, color)
        else:
            update_board(self.agent_board, next_move, color)
            
        # Checks if game terminate
        if is_terminal(self.agent_board):
            self.timer.print_final_stats()
        
        match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")
            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")
    
    def __del__(self):
        if hasattr(self, 'timer'):
            self.timer.print_final_stats()