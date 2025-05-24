from simulation_game.simulator import Simulator
from heatmap import Heatmap

import sys
from typing import Dict, Tuple, Optional
import numpy as np
 

# The action queue is stored, updated and executed in the real game here
class GetActionsUsingSimulations:
    def __init__(self, heatmap_size: tuple[float, float]=(1000, 800), heatmap_resolution: float=12, single_use: bool=False):
        # True if this module is used on its own
        self.single_use = single_use

        self.actions_queue = np.array([])

        # Adjust self.frames_into_future and this to handle lagging
        self.num_sims = 60

        # maximum ttc that the simulation checks for
        self.max_ttc = 10
        # if plotting sims
        if False: 
            self.num_sims = 2
            self.max_ttc = 2

        heatmap_size = (1000, 800)
        heatmap_resolution = 12
        # heatmap
        #self.map = Heatmap((0, heatmap_size[0]), (0, heatmap_size[1]), resolution = heatmap_resolution, max_ttc = self.max_ttc)
        self.best_theta = None

        # Simulate for a number of frames then execute the actions
        self.frames_into_future = 2
        # How many frames simulations has been run for
        self.current_frame = 0
        self.sim = None


    def actions(self, ship_state: Dict, game_state: Dict, called_last_frame: Optional[bool] = None): 
        if not self.single_use and not called_last_frame:
            self.current_frame = 0
            self.actions_queue = np.array([])
    
        fire = False
        safe_speed = 5
        if self.actions_queue.size == 0 and abs(ship_state["speed"]) > safe_speed:
            thrust = self.brake(ship_state, safe_speed)
            return thrust, 0, fire, False    
        
        if self.current_frame == self.frames_into_future:
            if self.actions_queue.size == 0:

                self.sim = Simulator(ship_state, game_state, num_sims=self.num_sims, max_ttc=self.max_ttc, frames_into_future=self.frames_into_future)
                self.current_frame = 0
            else:

                first_element = self.actions_queue[0]
                thrust = first_element['thrust'] 
                turn_rate = first_element['turn_rate']
                
                # edit duration (in frames)
                if first_element["duration"] > 0:
                    first_element["duration"] -= 1 
                elif first_element["duration"] == 0:
                    self.actions_queue = self.actions_queue[1:]
                else:
                    print("error in the queue")
                    sys.exit()

                return thrust, turn_rate, fire, False
        
        elif self.current_frame == 0:
            # Initialize simulator
            self.sim = Simulator(ship_state, game_state, num_sims=self.num_sims, max_ttc=self.max_ttc, frames_into_future=self.frames_into_future)
        
        # Simulate for 1 frame
        self.actions_queue = self.sim.run_simulations()
        
        self.current_frame += 1

        # Brake
        if abs(ship_state["speed"]) > safe_speed:
            thrust = self.brake(ship_state, safe_speed)
            return thrust, 0, fire, False
        else:
            return 0, 0, fire, False

    def brake(self, ship_state: Dict, safe_speed: float):
        current_speed = ship_state["speed"]
        if current_speed > 0:
            speed_error = current_speed - safe_speed
        else:
            speed_error = current_speed + safe_speed
        Kp = 10 

        # proportional control
        thrust = -Kp * speed_error
        thrust = max(min(thrust, 240), -240)
        return thrust

    @property
    def name(self) -> str:
        return "Get actions using simulations"
    

    """

    def actions(self, ship_state: Dict, game_state: Dict, called_last_frame: bool): 
        # self.map.actions(ship_state, game_state)
        # if self.best_theta is None or self.frames_travelled > 3:
        #     self.frames_travelled = 0
        #     self.ship_ttc = self.find_course(ship_state, game_state)

        # Resimulate if this module was not called last frame
        if not called_last_frame:
            self.actions_queue = np.array([])

        # self.frames_travelled += 1
        fire = False
            
        if self.actions_queue.size == 0: 
            safe_speed = 5
            if abs(ship_state["speed"]) > safe_speed:
                print("braking")
                thrust = self.brake(ship_state, safe_speed)
                return thrust, 0, True, False
            else:
                # Run simulator and return the best actions queue if the queue is empty
                sim = Simulator(num_sims=self.num_sims, best_theta=self.best_theta, max_ttc=self.max_ttc)
                self.actions_queue = sim.run_simulations(ship_state, game_state)

        first_element = self.actions_queue[0]
        thrust = first_element['thrust'] 
        turn_rate = first_element['turn_rate']
        
        # edit duration (in frames)
        if first_element["duration"] > 0:
            first_element["duration"] -= 1 
        elif first_element["duration"] == 0:
            self.actions_queue = self.actions_queue[1:]
        else:
            print("error in the queue")
            sys.exit()

        return thrust, turn_rate, False, False
    
    def find_course(self, ship_state: Dict, game_state: Dict):
        # initialize heatmap
        best_dir = self.map.weighted_gradient(ship_state["radius"], 4, ship_state, game_state)

        theta = 180/np.pi * np.arctan2(best_dir[1], best_dir[0])
        # convert to [0, 360]
        theta = (theta + 360) % 360
        self.best_theta = theta

        ship_ttc = self.map.ship_ttc
        return ship_ttc

    def brake(self, ship_state: Dict, safe_speed: float):
        current_speed = ship_state["speed"]
        if current_speed > 0:
            speed_error = current_speed - safe_speed
        else:
            speed_error = current_speed + safe_speed
        Kp = 50 

        # proportional control
        thrust = -Kp * speed_error
        thrust = max(min(thrust, 240), -240)
        return thrust

    @property
    def name(self) -> str:
        return "Get actions using simulations"
    

    """
    """
    def update_heatmap(self, ship_state: Dict, game_state: Dict):
        # initialize heatmap
        ship_coord = ship_state["position"]
        width, height = self.size
        x_boundary = (max(ship_coord[0]-width/2, 0), min(ship_coord[0]+width/2, 1000))
        y_boundary = (max(ship_coord[1]-height/2, 0), min(ship_coord[1]+height/2, 800))
        self.heatmap = Heatmap(x_boundary, y_boundary, self.resolution)
        self.heatmap.actions(ship_state, game_state)
        best_dir = self.map.weighted_gradient(ship_state["radius"], 4, ship_state, game_state)

        theta = 180/np.pi * np.arctan2(best_dir[1], best_dir[0])
        # convert to [0, 360]
        self.best_theta = (theta + 360) % 360
        return
    """
