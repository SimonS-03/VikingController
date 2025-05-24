import numpy as np
import math
from typing import Dict, List
import time
import copy
import random

from MCTS_simulation.sim_scenario import SimulationScenario
from MCTS_simulation.kessler_game_sim import KesslerGame, TrainerEnvironment, GraphicsType
from MCTS_simulation.sim_controller import SimulationController
from MCTS_simulation.heatmap import Heatmap
from graphics_both import GraphicsBoth


ACTIONS = [
    {"thrust": 180.0, "turn_rate": 0.0}, 
    {"thrust": -180.0, "turn_rate": 0.0},
    {"thrust": 0.0, "turn_rate": 20.0},
    {"thrust": 0.0, "turn_rate": -20.0},
    {"thrust": 0.0, "turn_rate": 0.0}
]

# A MCTS simulator
class Simulator:
    def __init__(self, num_sims: int=1000, total_frames: int=30):
        self.num_sims = num_sims
        self.action_duration = 10
        self.max_depth = total_frames // self.action_duration
        self.total_frames = total_frames

        # Heatmap params
        self.heatmap_size = (1000, 800)
        self.heatmap_resolution = 10

        # desired theta from heatmap 
        self.best_theta = None
        self.ship_ttc = None
        self.frames_travelled = 0
    
    def run_simulations(self, ship_ownstate: Dict, game_state: Dict, ttc_threshold: float) -> List[Dict]:
        """
        Clone the real game and run the game with different action queues. Then return the best performing one
        """
        # initialize scenario
        asteroids = game_state["asteroids"]
        bullets = game_state["bullets"]
        mines = game_state["mines"]

        # create a scenario using the current game state. 
        scenario = SimulationScenario(name='Simulation Scenario',
                            asteroid_states=[{'position': asteroid["position"], 
                                              'velocity': asteroid["velocity"],
                                              'size': asteroid["size"]} 
                                              for asteroid in asteroids
                                              ],
                            ship_states=[{'position': ship_ownstate["position"], 
                                          'angle': ship_ownstate["heading"], 
                                          'lives_remaining': ship_ownstate["lives_remaining"], 
                                          'team': 1, 
                                          'bullets_remaining': ship_ownstate["bullets_remaining"], 
                                          'mines_remaining': ship_ownstate["mines_remaining"], 
                                          'is_respawning': ship_ownstate["is_respawning"]}
                                          ],
                            bullet_states=[{'starting_position': bullet["position"],
                                            'starting_heading': bullet["heading"]}
                                            for bullet in bullets
                                            ],
                            mine_states=[{'starting_position': mine["position"],
                                          'countdown_timer': mine["remaining_time"],
                                          }
                                         for mine in mines
                                         ],
                            map_size=(1000, 800),
                            sim_time=game_state["time"],
                            frame_limit = self.total_frames,
                            ttc_threshold=ttc_threshold
                            )
        
        # Define Game Settings
        game_settings = {'perf_tracker': True,  
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'frequency': 30}
        
        # run MCTS
        root = Node()
        for _ in range(self.num_sims):
            node = root
            action_queue = []

            while node.children:
                node = node.best_child()
                action_queue.append(node.action)

            if len(action_queue) < self.max_depth:
                possible_actions = [a for a in ACTIONS if a not in [child.action for child in node.children]]
                if possible_actions:
                    action = copy.deepcopy(random.choice(possible_actions))
                    action["duration"] = self.action_duration
                    new_node = Node(parent=node, action=action)
                    node.children.append(new_node)
                    node = new_node
                    action_queue.append(action)

            # simulate
            for _ in range(self.max_depth - len(action_queue)):
                rand_action = copy.deepcopy(random.choice(ACTIONS))
                rand_action["duration"] = self.action_duration
                action_queue.append(copy.deepcopy(rand_action))
                
            #game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario
            game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation

            # Evaluate the game
            pre = time.perf_counter()
            # Run the game with an action_queue from the action_queues
            score, perf_data = game.run(sim_scenario=scenario, controllers=[SimulationController(copy.deepcopy(action_queue))])

            # Get the fitness score of this move sequence   
            fitness = self.get_fitness(score)
            
            # Backpropagate
            while node is not None:
                node.visits += 1
                node.reward += fitness
                node = node.parent

            print("-------end--------")
        best = max(root.children, key=lambda n: n.reward / n.visits)
        return best.action
    
    # score the performance of a sequence of moves
    def get_fitness(self, score):
        current_score = 0 
        #own_score = score.teams[0]

        # This is the worst outcome and will get the lowest score
        if score.stop_reason.name == 'asteroid_ship_collision':
            print("collision")
            current_score -= (1000 + score.frames_to_safespot)
            return current_score
    
            
        current_score += score.final_ttc
        
        return current_score

    def sample_action(self, ship_state: Dict, game_state: Dict):

        # initialize heatmap
        ship_coord = ship_state["position"]
        width, height = self.heatmap_size
        x_boundary = (max(ship_coord[0]-width/2, 0), min(ship_coord[0]+width/2, 1000))
        y_boundary = (max(ship_coord[1]-height/2, 0), min(ship_coord[1]+height/2, 800))
        map = Heatmap(x_boundary, y_boundary, self.heatmap_resolution)
        map.actions(ship_state, game_state)
        best_dir = map.weighted_gradient(ship_state["radius"], 3)

        theta = 180/np.pi * np.arctan2(best_dir[1], best_dir[0])
        # convert to [0, 360]
        theta = (theta + 360) % 360     

        # difference between the gradient direction and the ship direction
        delta_theta = abs(theta - ship_state["heading"]) % 360 # [0, 360]
        delta_theta = min(delta_theta, 360 - delta_theta) # [0, 180]
        assert 0 <= delta_theta <= 180 

        # normalize
        norm_theta = theta/180

        # bias weights
        turn_weight = norm_theta
        thrust_weight = 1 - norm_theta

        # assign bias to the actions
        bias_scores = [self.get_action_bias(a, turn_weight, thrust_weight) for a in ACTIONS]

        probs = self.softmax(bias_scores, temperature=0.5)

        chosen_action = random.choices(ACTIONS, weights = probs, k=1)[0]
        return chosen_action
    
    # get bias score for an action
    def get_action_bias(self, action, turn_weight, thrust_weight):
        score = 1.0
        if action["turn_rate"] != 0:
            score *= turn_weight
        if action["thrust"] > 0:
            score *= thrust_weight
        return score

    def softmax(self, x, temperature=1.0):
        x = [i / temperature for i in x]
        e_x = [math.exp(i) for i in x]
        total = sum(e_x)
        return [i / total for i in e_x]


class Node:
    def __init__(self, parent=None, action=None):
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.reward = 0.0
    
    def is_fully_expanded(self):
        return len(self.children) == len(ACTIONS)

    def best_child(self, c_param=1.41):
        return max(self.children, key=lambda child: (child.reward / child.visits) + c_param * np.sqrt(np.log(self.visits) / child.visits))