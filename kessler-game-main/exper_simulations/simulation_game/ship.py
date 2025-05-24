# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import math
import warnings
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from .controller import KesslerController


class Ship:
    __slots__ = (
        'controller', 'thrust', 'turn_rate', 'id', 'speed', 'position',
        'velocity', 'heading', 'lives', 'deaths', 'team', 'team_name',
        'fire', 'drop_mine', 'thrust_range', 'turn_rate_range', 'max_speed',
        'drag', 'radius', 'mass', '_respawning', '_respawn_time', '_fire_limiter',
        '_fire_time', '_mine_limiter', '_mine_deploy_time', 'mines_remaining',
        'bullets_remaining', 'bullets_shot', 'mines_dropped', 'bullets_hit',
        'mines_hit', 'asteroids_hit', 'custom_sprite_path', 'frames_to_stop',
        'final_ttc'
    )
    def __init__(self, ship_id: int,
                 position: Tuple[float, float],
                 angle: float = 90.0,
                 lives_remaining: int = 3,
                 team: int = 1,
                 team_name: Optional[str] = None,
                 is_respawning: bool = False) -> None:
        """
        Instantiate a ship with default parameters and infinite bullets if not specified
        """

        # Control information
        self.controller: Optional[KesslerController] = None
        self.thrust: float = 0.0  # speed defaults to minimum
        self.turn_rate: float = 0.0

        # Ship custom graphics
        self.custom_sprite_path = None

        # State info
        self.id: int = ship_id
        self.speed: float = 0.0
        self.position: tuple[float, float] = position
        self.velocity: tuple[float, float] = (0.0, 0.0)
        self.heading: float = angle
        self.lives: int = lives_remaining
        self.deaths: int = 0
        self.team: int = team
        self.team_name: str = team_name if team_name is not None else 'Team ' + str(self.team)

        # Controller inputs
        self.fire = False
        self.thrust = 0.0
        self.turn_rate = 0.0
        self.drop_mine = False

        # Physical model constants/params
        self.thrust_range = (-480.0, 480.0)  # m/s^2
        self.turn_rate_range = (-180.0, 180.0)  # Degrees per second
        self.max_speed = 240.0  # Meters per second
        self.drag = 80.0  # m/s^2
        self.radius = 20.0  # meters TODO verify radius size
        self.mass = 300.0  # kg - reasonable? max asteroid mass currently is ~490 kg

        # Manage respawns/firing via timers
        self._respawning = is_respawning
        self._respawn_time = 3.0  # seconds

        # Tracks the number of frames it took to reach an early end of the simulation 
        # (Caused by either collision with and asteroid or reaching a safespot)
        #self.frames_to_stop = None
        # Tracks the ttc at the end of a simulation if the simulation runs until the frame limit
        #self.final_ttc = None

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "is_respawning": True if self.is_respawning else False,
            "position": tuple(self.position),
            "velocity": tuple([float(v) for v in self.velocity]),
            "speed": float(self.speed),
            "heading": float(self.heading),
            "mass": float(self.mass),
            "radius": float(self.radius),
            "id": int(self.id),
            "team": str(self.team),
            "lives_remaining": int(self.lives),
        }

    @property
    def ownstate(self) -> Dict[str, Any]:
        return {**self.state,
                "thrust_range": self.thrust_range,
                "turn_rate_range": self.turn_rate_range,
                "max_speed": self.max_speed,
                "drag": self.drag,
        }

    @property
    def alive(self) -> bool:
        return True if self.lives > 0 else False

    @property
    def is_respawning(self) -> bool:
        return True if self._respawning else False

    @property
    def respawn_time_left(self) -> float:
        return self._respawning

    @property
    def respawn_time(self) -> float:
        return self._respawn_time

    def update(self, delta_time: float = 1 / 30):
        """
        Update our position and other particulars.
        """

        # Decrement respawn timer (if necessary)
        if self._respawning <= 0.0:
            self._respawning = 0.0
        else:
            self._respawning -= delta_time

        # Apply drag. Fully stop the ship if it would cross zero speed in this time (prevents oscillation)
        drag_amount = self.drag * delta_time
        if drag_amount > abs(self.speed):
            self.speed = 0.0
        else:
            self.speed -= drag_amount * np.sign(self.speed)

        # Bounds check the thrust
        if self.thrust < self.thrust_range[0] or self.thrust > self.thrust_range[1]:
            self.thrust = min(max(self.thrust_range[0], self.thrust), self.thrust_range[1])
            warnings.warn('Ship ' + str(self.id) + ' thrust command outside of allowable range', RuntimeWarning)

        # Apply thrust
        self.speed += self.thrust * delta_time

        # Bounds check the speed
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # Update the angle based on turning rate
        self.heading += self.turn_rate * delta_time

        # Keep the angle within (0, 360)
        self.heading %= 360.0

        # Use speed magnitude to get velocity vector
        rad_heading = math.radians(self.heading)
        self.velocity = (math.cos(rad_heading) * self.speed,
                         math.sin(rad_heading) * self.speed)

        # Update the position based off the velocities
        self.position = (self.position[0] + self.velocity[0] * delta_time, self.position[1] + self.velocity[1] * delta_time)
        return 

