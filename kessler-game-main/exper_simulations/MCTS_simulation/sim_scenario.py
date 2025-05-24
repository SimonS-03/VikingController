# -*- coding: utf-8 -*-
# Copyright © 2018-2020 Thales Avionics USA
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

from typing import List, Tuple, Dict, Any, Optional
import random

from .ship import Ship
from .asteroid import Asteroid
from .bullet import Bullet
from .mines import Mine


class SimulationScenario:
    def __init__(self, name: str = "Unnamed", 
                 asteroid_states: Dict = None,
                 ship_states: Dict = None, 
                 bullet_states: Dict = None, 
                 mine_states: Dict = None,
                 map_size: Optional[Tuple[int, int]] = None, seed: Optional[int] = None,
                 time_limit: float = float("inf"), # Not used for simulations
                 frame_limit: float = float("inf"), 
                 #ammo_limit_multiplier: float = 0.0, 
                 sim_time: float = 0,
                 ttc_threshold: float = 0
                 ) -> None:
        """
        Specify the starting state of the environment, including map dimensions and optional features

        Make sure to only set either ``num_asteroids`` or ``asteroid_states``. If neither are set, the
        Scenario defaults to 3 randomly placed asteroids

        :param name: Optional, name of the scenario
        :param num_asteroids: Optional, Number of asteroids
        :param asteroid_states: Optional, Asteroid Starting states
        :param ship_states: Optional, Ship Starting states (list of dictionaries)
        :param game_map: Game Map using ``Map`` object
        :param time_limit: Optional seeding value to pass to random.seed() which is called before asteroid creation
        """
        # Protected variable for managing the name, through getter/setter interface
        self._name: Optional[str] = None

        # Store name as string using setter
        self.name = name

        # Store map size
        self.map_size = map_size if map_size else (1000, 800)

        # Store ship states if not None, otherwise, create one ship at center
        self.ship_states = ship_states 

        # Storing for simulations starting mid-game
        self.bullet_states = bullet_states
        self.mine_states = mine_states

        # Time to collision threshold where the ship considers the 
        # current position to be safe enough to quit simulating
        self.ttc_threshold = ttc_threshold

        # Time when the game should be started at
        self.sim_time = sim_time

        # NOT USED
        self.time_limit = time_limit
        
        # Set frame limit
        self.frame_limit = frame_limit

        # Store random seed
        self.seed = seed

        # Will be built later
        self.asteroid_states = list()

        """# Set the ammo limit multiplier
        if ammo_limit_multiplier < 0:
            raise ValueError("Ammo limit multiplier must be > 0."
                             "If unlimited ammo is desired, do not pass the ammo limit multiplier")
        else:
            self._ammo_limit_multiplier = ammo_limit_multiplier

        if ammo_limit_multiplier and stop_if_no_ammo:
            self.stop_if_no_ammo = True
        elif not ammo_limit_multiplier and stop_if_no_ammo:
            self.stop_if_no_ammo = False
            raise ValueError("Cannot enforce no ammo stopping condition because ammo is unlimited"
                             "Do not pass ammo_limit_multiplier during scenario creation if unlimited ammo is desired")
        else:
            self.stop_if_no_ammo = False"""

        # Store asteroid states
        if asteroid_states:
            self.asteroid_states = asteroid_states

        else:
            raise (ValueError("User should define `asteroid_states` to create "
                              "valid custom starting states for the environment"))

    @property
    def name(self) -> None | str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        # Raises error if the name cannot be converted to string
        self._name = str(name)

    @property
    def num_starting_asteroids(self) -> float:
        return len(self.asteroid_states)

    @property
    def is_random(self) -> bool:
        return not all(state for state in self.asteroid_states) if self.asteroid_states else True

    @property
    def max_asteroids(self) -> int:
        return sum([SimulationScenario.count_asteroids(asteroid.size) for asteroid in self.asteroids()])

    """@property
    def bullet_limit(self) -> int:
        if self._ammo_limit_multiplier:
            temp = round(self.max_asteroids*self._ammo_limit_multiplier)
            if temp == 0:
                return temp + 1
            else:
                return temp

        else:
            return -1"""

    @staticmethod
    def count_asteroids(asteroid_size: int) -> int:
        # Counting based off of each asteroid making 3 children when destroyed
        return sum([3 ** (size - 1) for size in range(1, asteroid_size + 1)])

    def asteroids(self) -> List[Asteroid]:
        """
        Create asteroid sprites
        :param frequency: Operating frequency of the game
        :return: List of ShipSprites
        """
        # Loop through and create AsteroidSprites based on current game state
        return [Asteroid(**asteroid_state) for asteroid_state in self.asteroid_states]

    def ships(self) -> List[Ship]:
        """
        Create ship sprites
        :param frequency: Operating frequency of the game
        :return: List of ShipSprites
        """
        # Loop through and create ShipSprites based on current game state
        return [Ship(idx+1, **ship_state) for idx, ship_state in enumerate(self.ship_states)]

    def bullets(self) -> List[Bullet]:
        """
        Create bullet sprites
        :return: List of Bullets
        """
        # Loop through and create BulletSprites based on current game state
        return [Bullet(**bullet_state) for bullet_state in self.bullet_states]

    def mines(self) -> List[Mine]:
        """
        Create mine sprites
        :return: List of Mines
        """
        # Loop through and create MineSprites based on current game state
        return [Mine(**mine_state) for mine_state in self.mine_states]