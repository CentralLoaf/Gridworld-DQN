import numpy as np
from typing import Tuple
import utils

class Env:
    def __init__(self, initial_state: np.ndarray, prey_loc: Tuple[int, int], pred_loc: Tuple[int, int], terminal_reward: float = 10, distance_scale_factor: float = 0.5):
        self.states = [initial_state]
        self.prey_locs = [prey_loc]
        self.pred_locs = [pred_loc]
        
        self.tr = terminal_reward
        self.dsf = distance_scale_factor
        self.done = False
        
        self.prey_value, self.pred_value = 0, 0
        
        
    def reward(self) -> int:
        '''
        Simple reward function based on manhattan distance changes between agents and 
        '''
        distance = abs(self.prey_locs[-1][0] - self.pred_locs[-1][0]) + abs(self.pred_locs[-1][1] - self.pred_locs[-1][1])
        
        # Handle prey reward
        prey_r = 1.0 + (-self.tr if self.pred_locs[-1] == self.prey_locs[-1] else 0.0) + (self.dsf * distance)
        
        # Handle predator reward
        pred_r = (self.tr if self.pred_locs[-1] == self.prey_locs[-1] else 0.0) + (self.dsf / distance)
        
        return prey_r, pred_r
        
        
    def step(self, prey_action: int, pred_action: int) -> Tuple[np.ndarray, float, float, bool]:
        '''
        Updates the environment by one step
        '''
        get_action = lambda action_index: (1, 0) if action_index == 0 else ((0, -1) if action_index == 1 else ((-1, 0) if action_index == 2 else (0, 1)))
        self.states.append(self.states[-1].copy())
        
        # Reset current agent locations
        self.states[-1][self.prey_locs[-1][0]][self.prey_locs[-1][1]] = 0.0
        self.states[-1][self.pred_locs[-1][0]][self.pred_locs[-1][1]] = 0.0
        
        # Decode action index
        prey_a, pred_a = get_action(prey_action), get_action(pred_action)
        
        # Assign new agent locations
        self.prey_locs.append(utils.verify_shift(self.states[-1], self.prey_locs[-1], prey_a, 1.0))
        self.pred_locs.append(utils.verify_shift(self.states[-1], self.pred_locs[-1], pred_a, 2.0))
        
        # Handle agent relocating
        self.states[-1][self.prey_locs[-1]] = 1.0
        self.states[-1][self.pred_locs[-1]] = 2.0
        
        prey_r, pred_r = self.reward()
    
        self.done = True if self.prey_locs[-1] == self.pred_locs[-1] else False
        return self.states[-2], self.states[-1], prey_r, pred_r
        
        
    @classmethod
    def gen_grid(cls) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
        '''
        Creates a new 10x10 map, randomly places the prey and pred
        '''
        state = np.zeros((10, 10), dtype=float)
        
        # Prepare random agent starting locations
        pred_loc, prey_loc = np.random.choice(100, 2, replace=False)
        pred_loc, prey_loc = np.unravel_index(prey_loc, (10, 10)), np.unravel_index(pred_loc, (10, 10))
        
        state[prey_loc[0]][pred_loc[1]] = 1.0 # Starting location of the prey
        state[pred_loc[0]][pred_loc[1]] = 2.0 # Starting location of the predator
        
        return state, prey_loc, pred_loc