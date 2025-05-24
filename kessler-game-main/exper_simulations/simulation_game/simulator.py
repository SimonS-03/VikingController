import numpy as np
from typing import Dict, List, Optional, Tuple
import time
import random
from math import exp
import sys
import copy
import os
import glob

# from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from .frame_cache import FrameCache
from exper_simulations.simulation_game.sim_scenario import SimulationScenario
from exper_simulations.simulation_game.kessler_game_sim import KesslerGame, TrainerEnvironment, GraphicsType
from exper_simulations.simulation_game.sim_controller import SimulationController
from graphics_both import GraphicsBoth

#TODO handle respawning ship. _respawn_time is not passed to the controller
ACTIONS = [
    [{"thrust": 480.0, "turn_rate": 0.0}, 
     {"thrust": 480.0, "turn_rate": 0.0}], 
    {"thrust": -480.0, "turn_rate": 0.0}, 
    {"thrust": 0.4*480, "turn_rate": 0.7*180},
    {"thrust": 0.4*480, "turn_rate": -0.7*180},
    {"thrust": -0.4*480, "turn_rate": 0.7*180},
    {"thrust": -0.4*480, "turn_rate": -0.7*180},
    {"thrust": 0.4*480, "turn_rate": 0.3*180},
    {"thrust": 0.4*480, "turn_rate": -0.3*180},
    {"thrust": -0.4*480, "turn_rate": 0.3*180},
    {"thrust": -0.4*480, "turn_rate": -0.3*180}
]

# This runs simulations to find the best action queue for the current frame
class Simulator:
    def __init__(self, ship_ownstate: Dict, game_state: Dict, num_sims: Optional[float] = None, max_ttc: float = None, frames_into_future: int = None):
        self.cache = {}

        self.action_prototyp = np.dtype([
            ('thrust', 'f4'),
            ('turn_rate', 'f4'),
            ('duration', 'u4')
        ])

        self.best_fitness = -float('inf')
        self.best_actions = None
        
        #self.ammo_limit_multiplier = ammo_limit_multiplier
        
        self.num_sims = num_sims

        self.plot_sims = False

        self.max_duration = 200 if self.plot_sims else 20

        self.sims_each_frame = num_sims / frames_into_future

        # to keep track of what action queue has been simulated
        self.i = 0

        # duration of each action queue
        self.durations = []

        # maximum ttc that the simulation checks for
        self.max_ttc = max_ttc

        self.frames_into_future = frames_into_future

        # initialize scenario
        self.asteroids = game_state["asteroids"]

        # create a scenario using the current game state. 
        self.scenario_template = SimulationScenario(name='Simulation Scenario',
                            asteroid_states=[{'position': asteroid["position"], 
                                            'velocity': asteroid["velocity"],
                                            'size': asteroid["size"]} 
                                            for asteroid in self.asteroids
                                            ],
                            ship_states=[{'position': ship_ownstate["position"], 
                                        'angle': ship_ownstate["heading"], 
                                        'lives_remaining': ship_ownstate["lives_remaining"], 
                                        'team': 1, 
                                        'is_respawning': ship_ownstate["is_respawning"]}
                                        ],
                            map_size=(1000, 800),
                            sim_time=game_state["time"],
                            step=game_state["sim_frame"]
                            )
        
        # sample num_sims number of actions queues
        # self.actions_queues = self.sample_queue_heuristic()
        #actions_queues = self.sample_queue_using_gradient(self.num_sims, ship_ownstate["heading"], self.best_theta)
        self.actions_queues = self.sample_queue()


        # Define Game Settings
        self.game_settings = {'perf_tracker': True,  
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'frequency': 30}    
    
    
    def run_simulations(self) -> List[Dict]:
        
        #Clone the real game and run the game with different action queues. Then return the best performing one
        start_time = time.perf_counter()
        use_cache = False
        frame_cache = FrameCache() if use_cache else None

        # do simulations
        if self.plot_sims:
            game = KesslerGame(settings=self.game_settings)  # Use this to visualize the game scenario
        else:
            game = TrainerEnvironment(settings=self.game_settings)  # Use this for max-speed, no-graphics simulation

        """while (time.perf_counter() - start_time) < self.max_duration and (self.i < len(self.actions_queues)):

            actions_queue = self.actions_queues[self.i]
            # how long the actions run for
            action_duration = self.durations[i]

            # Set the scenario frame limit to be the duration of the actions + the max ttc
            self.scenario_template.update_frame_limit(action_duration + self.max_ttc*30) # Ändrade från scenario.upodate_frame_limit, var ej definerat
            
            action_array = np.array([(a['thrust'], a['turn_rate'], a['duration'])
                                for a in actions_queue], dtype=self.action_prototyp)
            game = TrainerEnvironment(settings = self.game_settings)
            # Run the game with an action_queue from the action_queues
            perf_data, stop_reason_name, total_frames = game.run(frame_cache, sim_scenario=copy.deepcopy(self.scenario_template), controllers=[SimulationController(action_array.copy())])

            # Get the fitness score of this move sequence and update the best_fitness
            fitness = self.get_fitness(stop_reason_name, total_frames, action_duration)
            #print("fitness:", fitness)
            #print(actions_queue, "fitness:", fitness)
            if fitness > self.best_fitness:
                self.best_fitness = fitness 
                self.best_actions = action_array[1:]
                best_stop_reason = stop_reason_name
            self.i += 1"""
        # what i to end on this frame
        end_i = self.i + self.sims_each_frame
        
        while self.i < end_i:
            actions_queue = self.actions_queues[self.i]
            # how long the actions run for
            action_duration = self.durations[self.i]

            # create scenario_template clone
            scenario = self.scenario_template.clone()

            # Set the scenario frame limit to be the duration of the actions + the max ttc
            scenario.update_frame_limit(action_duration + self.max_ttc*30)
            
            action_array = np.array([(a['thrust'], a['turn_rate'], a['duration'])
                                for a in actions_queue], dtype=self.action_prototyp)

            # Run the game with an action_queue from the action_queues
            perf_data, stop_reason_name, total_frames = game.run(frame_cache, sim_scenario=scenario, controllers=[SimulationController(action_array.copy())])
        
            # Get the fitness score of this move sequence and update the best_fitness
            fitness = self.get_fitness(stop_reason_name, total_frames, action_duration)

            if fitness > self.best_fitness:
                self.best_fitness = fitness 
                self.best_actions = action_array[1:]
                best_stop_reason = stop_reason_name
            self.i += 1

        #     print(action_array)
        # print("Ran", self.i,"simulations")
        # print(f"Stop reason{best_stop_reason} {total_frames - action_duration}")
        # print(self.best_fitness, self.best_actions)
        

        return self.best_actions
    
    # score the performance of a sequence of moves
    def get_fitness(self, stop_reason_name, total_frames, action_duration: int):
        current_score = 0 
        #own_score = score.teams[0]
        #print(score.teams[0].final_ttc)

        # collisions
        if stop_reason_name == 'asteroid_ship_collision':
            # collision before having performed all queued actions
            if total_frames < action_duration:
                current_score -= 1000
                current_score += total_frames
            # collision after having performed all queued actions (ship is stationary).
            else:
                ttc = total_frames - action_duration
                current_score += ttc 

        # no collision happens and the ttc is set to the maximum
        elif stop_reason_name == 'frame_limit_reached':
            current_score += 1000
            ttc = total_frames - action_duration
            current_score += ttc 

        return current_score
    
      # randomly sample an action queue. An actions queue is a queue of actions to be performed until the frame limit 
    def sample_queue_heuristic(self) -> List[Dict]:
        min_duration = 15
        max_duration = 50

        queues = []

        for i in range(self.num_sims):
            next_action = [{"thrust": 0.0, "turn_rate": 0.0, "duration": self.frames_into_future}, 
                           random.choice(ACTIONS)]
            duration = random.randint(min_duration, max_duration)
            next_action[1]["duration"] = duration
            queues.append(next_action)
            self.durations.append(self.frames_into_future + 15)

        return queues

    
    # Bias toward the current direction. then randomize a turn rate and pair it with the correct duration
    def sample_queue(self, std_dev: float = 30) -> List[List[Dict]]:
        # ------------------  First rotate ------------------
        # randomize direction
        # offsets = np.random.normal(0, std_dev, num_queues)
        turn_rates = []
        turn_durations = []
        for i in range(int(self.num_sims)):
            if i < int(self.num_sims)/2:
                turn_rates.append(180)
                turn_durations.append(int(30/self.num_sims * (i+1)))
            else:
                turn_rates.append(-180)
                turn_durations.append(int(30/self.num_sims * (i+1 - int(self.num_sims/2))))

        # turn_rates = np.sign(offsets) * 180
        # turn_durations = (np.abs(offsets) / 180 * 30).astype(int)

        # # check how many asteroids are nearby
        # if num_close_asterois > 5:
        #     thrust_options = np.array([100, 150, 200, 150, 300, -200, -300])
        # else:
        #     thrust_options = np.array([100, 200, 300, 400, -300, -400])
        # thrust_options = np.array([100, 150, 200, 250, -200, -300])
        # thrust_options = np.array([300, 350, 400, 480, -200, -300, -400, -480])

        # thrusts = np.random.choice(thrust_options, size=self.num_sims)

        # thrust_durations = np.random.randint(5, 15, size=self.num_sims)
        thrust_durations = np.random.randint(0, 3, size=self.num_sims)

        queues = []

        for i in range(self.num_sims):
            dir = random.choice([-1, 1])
            queues.append([
                {"thrust": 0.0, "turn_rate": 0.0, "duration": self.frames_into_future},
                {"thrust": dir * 300.0, "turn_rate": turn_rates[i], "duration": turn_durations[i]},
                {"thrust": dir * 400, "turn_rate": 0.0, "duration": thrust_durations[i]}
            ])

            self.durations.append(self.frames_into_future + turn_durations[i] + thrust_durations[i])

        return queues

    def fast_queue_copy(self, queue):
        return [{'thrust': a['thrust'],
                 'turn_rate': a['turn_rate'],
                 'duration': a['duration']}
                 for a in queue]

    @property
    def name(self) -> str:
        return "Simulator"
    

        """

    def run_single_sim(self, scenario: SimulationScenario, actions_queue: List[Dict], duration: int) -> Tuple[float, List[Dict]]:
        """
        # Run a single simulation and return (fitness_score, actions_used)
        """

        scenario = scenario
        # Set the scenario frame limit to be the duration of the actions + the max ttc
        scenario.update_frame_limit(duration + self.max_ttc*30)

        action_array = np.array([(a['thrust'], a['turn_rate'], a['duration'], a['fire'], a['mine'])
                                for a in actions_queue], dtype=self.action_prototyp)
    
        # game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario
        game = TrainerEnvironment(settings=self.game_settings)  # Use this for max-speed, no-graphics simulation
            
        # Run the game with an action_queue from the action_queues
        perf_data, stop_reason_name, total_frames = game.run(sim_scenario=scenario, controllers=[SimulationController(action_array)])

        # Get the fitness score of this move sequence and update the best_fitness
        fitness = self.get_fitness(stop_reason_name, total_frames, duration)
        #print(actions_queue, "fitness:", fitness)
        return fitness, action_array


        # Simulate using threads
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self.run_single_sim, 
                    scenario_template,
                    self.fast_queue_copy(queue),
                    self.durations[i]
                ): i for i, queue in enumerate(actions_queues)
            }
            
            for future in as_completed(futures):
                sim_start = time.perf_counter()
                # if (time.perf_counter() - start_time) >= self.max_duration:
                #     future.cancel() # stop if timeout reached
                #     continue
                fitness, actions = future.result()
                if fitness > self.best_fitness:
                    
                    self.best_fitness = fitness 
                
                    self.best_actions = actions
                print(f"Sim{futures[future]} finished in {time.perf_counter() - sim_start:.7f} seconds")


    # ORIGINAL APPROACH: randomly choose from predefined actions (defined above)
    # randomly sample an action queue. An actions queue is a queue of actions to be performed until the frame limit 
    def sample_actions_queue(self, probs) -> List[Dict]:
        queue = []
        tot_frame = 0
        while tot_frame < self.frame_limit:
            next_action = self.sample_action(probs)
            duration = 10 # random.randint(self.min_duration, self.max_duration)
            next_action["duration"] = duration
            queue.append(next_action)
            tot_frame += duration
        return queue

    def sample_action(self, probs):
        chosen_action = copy.deepcopy(random.choices(ACTIONS, weights = probs, k=1)[0])
        return chosen_action
    
    # get bias score for an action
    def get_action_bias(self, action, turn_weight, thrust_weight):
        score = 1.0
        if action["turn_rate"] != 0:
            score *= turn_weight
        if action["thrust"] != 0:
            score *= thrust_weight
        #return score
        return 1

    def softmax(self, x, temperature=1.0):
        x = [i / temperature for i in x]
        e_x = [math.exp(i) for i in x]
        total = sum(e_x)
        return [i / total for i in e_x]

# difference between the gradient direction and the ship direction
        delta_theta = abs(self.best_theta - ship_ownstate["heading"]) % 360 # [0, 360]
        delta_theta = min(delta_theta, 360 - delta_theta) # [0, 180]
        assert 0 <= delta_theta <= 180 
        print("best_dir:", self.best_theta, delta_theta)

        # normalize
        norm_theta = min(delta_theta/90, 1)

        # bias weights
        turn_weight = norm_theta
        forward_thrust_weight = 1 - norm_theta
        #reverse_thrust_weight = 1 - norm_theta

        # assign bias to the actions
        bias_scores = [self.get_action_bias(a, turn_weight, forward_thrust_weight) for a in ACTIONS2]
        print(bias_scores)

        probs = self.softmax(bias_scores, temperature=0.5)"""
