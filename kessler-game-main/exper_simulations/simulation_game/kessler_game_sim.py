# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import time

import math
from typing import Dict, Any, List, Tuple, TypedDict, Optional
from enum import Enum
from collections import OrderedDict
from immutabledict import immutabledict

import sys

from .frame_cache import FrameCache
from .sim_scenario import SimulationScenario
from .controller import KesslerController
from .collisions import circle_line_collision
from .graphics import GraphicsType, GraphicsHandler
from .asteroid import Asteroid
from .ship import Ship
from .graphics import KesslerGraphics

class StopReason(Enum):
    not_stopped = 0
    no_ships = 1
    no_asteroids = 2
    time_expired = 3
    # for simulations
    asteroid_ship_collision = 5
    frame_limit_reached = 6


class PerfDict(TypedDict, total=False):
    controller_times: List[float]
    total_controller_time: float
    physics_update: float
    collisions_check: float
    score_update: float
    graphics_draw: float
    total_frame_time: float
    
class KesslerGame:
    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:

        if settings is None:
            settings = {}
        # Game settings
        self.frequency: float = settings.get("frequency", 30.0)
        self.time_step: float = 1 / settings.get("frequency", 30.0)
        self.perf_tracker: bool = settings.get("perf_tracker", True)
        self.prints_on: bool = settings.get("prints_on", True)
        self.graphics_type: GraphicsType = settings.get("graphics_type", GraphicsType.Tkinter)
        self.graphics_obj: Optional[KesslerGraphics] = settings.get("graphics_obj", None)
        self.realtime_multiplier: float = settings.get("realtime_multiplier", 0 if self.graphics_type==GraphicsType.NoGraphics else 1)
        self.time_limit: float = settings.get("time_limit", float("inf"))
        self.random_ast_splits = settings.get("random_ast_splits", False)

        # UI settings
        default_ui = {'ships': True, 'lives_remaining': True, 'accuracy': True,
                      'asteroids_hit': True, 'bullets_remaining': True, 'controller_name': True}
        self.UI_settings = settings.get("UI_settings", default_ui)
        if self.UI_settings == 'all':
            self.UI_settings = {'ships': True, 'lives_remaining': True, 'accuracy': True,
                                'asteroids_hit': True, 'shots_fired': True, 'bullets_remaining': True,
                                'controller_name': True}

    def run(self, cache: Optional[FrameCache], sim_scenario: SimulationScenario, controllers: List[KesslerController]) -> Tuple[List[PerfDict]]:
        """
        Simulate a scenario for a given number of frames
        """

        ################## 
        # INITIALIZATION #
        ##################
        # Initialize objects lists from scenario
        asteroids: List[Asteroid] = sim_scenario.asteroids()
        ships: List[Ship] = sim_scenario.ships()

        # Initialize environment parameters
        stop_reason = StopReason.not_stopped
        sim_time: float = sim_scenario.sim_time 
        step: int = sim_scenario.step
        starting_frame: int = step
        time_limit = sim_scenario.time_limit if sim_scenario.time_limit else self.time_limit

        # Assign controllers to each ship
        for controller, ship in zip(controllers, ships):
            controller.ship_id = ship.id
            ship.controller = controller
            if hasattr(controller, "custom_sprite_path"):
                ship.custom_sprite_path = controller.custom_sprite_path

        # Initialize graphics display
        graphics = GraphicsHandler(type=self.graphics_type, scenario=sim_scenario, UI_settings=self.UI_settings, graphics_obj=self.graphics_obj)

        # Initialize list of dictionary for performance tracking (will remain empty if perf_tracker is false
        perf_list: List[PerfDict] = []

        ######################
        # MAIN SCENARIO LOOP #
        ######################

        while stop_reason == StopReason.not_stopped:

            # Get perf time at the start of time step evaluation and initialize performance tracker
            step_start = time.perf_counter()
            perf_dict: PerfDict = {}

            # --- CALL CONTROLLER FOR EACH SHIP ------------------------------------------------------------------------
            # Get all live ships
            liveships = [ship for ship in ships if ship.alive]

            # Generate game_state info to send to controllers
            game_state: immutabledict = immutabledict({
                'asteroids': [asteroid.state for asteroid in asteroids],
                'ships': [ship.state for ship in liveships],
                'map_size': sim_scenario.map_size,
                'time': sim_time,
                'delta_time': self.time_step,
                'sim_frame': step,
                'time_limit': "None"
            })

            use_caching = False if cache is None else True
            # check if data is already cached
            cached_data = None
            if use_caching and step in cache._cache:
                cached_data = cache.load_frame(step)
                asteroids = [Asteroid(ast["position"], ast["velocity"], ast["size"]) for ast in cached_data]

            # Initialize controller time recording in performance tracker
            if self.perf_tracker:
                perf_dict['controller_times'] = []
                t_start = time.perf_counter()

            # Loop through each controller/ship combo and apply their actions
            for idx, ship in enumerate(ships):
                if ship.alive:
                    # Reset controls on ship to defaults
                    ship.thrust = 0.0
                    ship.turn_rate = 0.0
                    ship.fire = False
                    # Evaluate each controller letting control be applied
                    if controllers[idx].ship_id != ship.id:
                        raise RuntimeError("Controller and ship ID do not match")
                    ship.thrust, ship.turn_rate, ship.fire, ship.drop_mine = controllers[idx].actions(ship.ownstate, game_state)

                # Update controller evaluation time if performance tracking
                if self.perf_tracker:
                    controller_time = time.perf_counter() - t_start if ship.alive else 0.00
                    perf_dict['controller_times'].append(controller_time)
                    t_start = time.perf_counter()

            if self.perf_tracker:
                perf_dict['total_controller_time'] = time.perf_counter() - step_start
                prev = time.perf_counter()

            # --- UPDATE STATE INFORMATION OF EACH OBJECT --------------------------------------------------------------

            # Update each Asteroid and Ship
            if not cached_data:
                for asteroid in asteroids:
                    asteroid.update(self.time_step)
            for ship in liveships:
                if ship.alive:
                    ship.update(self.time_step)

            # Wrap ships and asteroids to other side of map
            for ship in liveships:
                ship.position = (ship.position[0] % sim_scenario.map_size[0], ship.position[1] % sim_scenario.map_size[1])

            if not cached_data:
                for asteroid in asteroids:
                    asteroid.position = (asteroid.position[0] % sim_scenario.map_size[0], asteroid.position[1] % sim_scenario.map_size[1])

            # Update performance tracker with
            if self.perf_tracker:
                perf_dict['physics_update'] = time.perf_counter() - prev
                prev = time.perf_counter()

            # --- CHECK FOR COLLISIONS ---------------------------------------------------------------------------------

            # Cull ships that are not alive
            liveships = [ship for ship in liveships if ship.alive]

            # Update performance tracker with collisions timing
            if self.perf_tracker:
                perf_dict['collisions_check'] = time.perf_counter() - prev
                prev = time.perf_counter()

            # --- UPDATE GRAPHICS --------------------------------------------------------------------------------------
            graphics.update(ships, asteroids)

            # Update performance tracker with graphics timing
            if self.perf_tracker:
                perf_dict['graphics_draw'] = time.perf_counter() - prev
                prev = time.perf_counter()

            # --- CHECK STOP CONDITIONS --------------------------------------------------------------------------------
            sim_time += self.time_step
            step += 1

            # No asteroids remain
            if not asteroids:
                stop_reason = StopReason.no_asteroids

            # Exceeding simulation frame limit
            elif step - starting_frame >= sim_scenario.frame_limit:
                # frame limit reached meaning no collision has happened and ttc is set to the maximum
                total_frames = step - starting_frame
                stop_reason = StopReason.frame_limit_reached
            
            # --- Check asteroid-ship collisions ---
            for ship in liveships:
                if not ship.is_respawning: 
                    for idx_ast, asteroid in enumerate(asteroids):
                        dx = ship.position[0] - asteroid.position[0]
                        dy = ship.position[1] - asteroid.position[1]
                        radius_sum = ship.radius + asteroid.radius
                        # Most of the time no collision occurs, so use early exit to optimize collision check
                        if abs(dx) <= radius_sum and abs(dy) <= radius_sum and dx * dx + dy * dy <= radius_sum * radius_sum:
                            # Stop checking this ship's collisions
                            # Record the number of frames it took to reach collision
                            total_frames = step - starting_frame
                            stop_reason = StopReason.asteroid_ship_collision
                            break

            if use_caching and not cached_data:
                if stop_reason == StopReason.not_stopped:
                    cache.save_frame(asteroids)

            # --- FINISHING TIME STEP ----------------------------------------------------------------------------------
            # Get overall time step compute time
            if self.perf_tracker:
                perf_dict['total_frame_time'] = time.perf_counter() - step_start
                perf_list.append(perf_dict)

            # Hold simulation so that it runs at realtime ratio if specified, else let it pass
            if self.realtime_multiplier != 0:
                time_dif = time.perf_counter() - step_start
                while time_dif < (self.time_step/self.realtime_multiplier):
                    time_dif = time.perf_counter() - step_start
            

            # End sim if taking too much time
            # if time.perf_counter() - sim_start > self.max_sim_len:
            #     total_frames = step - starting_frame
            #     stop_reason = StopReason.asteroid_ship_collision

        ############################################    
        # Finalization after scenario has been run #
        ############################################

        # Close graphics display
        graphics.close()

        # Return the score and stop condition
        return perf_list, stop_reason.name, total_frames
    
class TrainerEnvironment(KesslerGame):
    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        """
        Instantiates a KesslerGame object with settings to optimize training time
        """
        if settings is None:
            settings = {}
        trainer_settings = {
            'frequency': settings.get("frequency", 30.0),
            'perf_tracker': settings.get("perf_tracker", False),
            'prints_on': settings.get("prints_on", False),
            'graphics_type': GraphicsType.NoGraphics,
            'realtime_multiplier': 0,
            'time_limit': settings.get("time_limit", float("inf"))
        }
        super().__init__(trainer_settings)
