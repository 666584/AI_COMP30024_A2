from referee.game import Board
class Agent_Board:
    def __init__(self, player):
        self.new_board = Board(initial_player=player)
        self._state = self.new_board._state
    
    def render(self, use_color: bool = False, use_unicode: bool = False) -> str:
        return self.new_board.render(use_color=use_color, use_unicode=use_unicode)