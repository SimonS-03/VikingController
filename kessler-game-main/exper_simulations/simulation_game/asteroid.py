# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

from typing import Tuple, Dict, List, Any, Optional, TYPE_CHECKING, Union
import random
import math
import numpy as np

if TYPE_CHECKING:
    from .ship import Ship

class Asteroid:
    """ Sprite that represents an asteroid. """
    __slots__ = ('size', 'max_speed', 'num_children', 'radius', 'mass', 'vx', 'vy', 'velocity', 'position', 'angle', 'turnrate')
    def __init__(self,
                 position: Tuple[float, float],
                 velocity: Tuple[float, float],
                 size: Optional[int] = None
                 ) -> None:
        """
        Constructor for Asteroid Sprite

        :param position:  Optional Starting position (x, y) position
        :param speed: Optional Starting Speed
        :param angle: Optional Starting heading angle (degrees)
        :param size: Optional Starting size (1 to 4 inclusive)
        """

        # Set size to 4 if none is specified. Notify if out of size range
        if size:
            if 1 <= size <= 4:
                self.size = size
            else:
                raise ValueError("Asteroid size can only be between 1 and 4")
        else:
            self.size = 4

        # Set max speed based off of scaling factor
        speed_scaler = 2.0 + (4.0 - self.size) / 4.0
        self.max_speed = 60.0 * speed_scaler

        # Number of child asteroids spawned when this asteroid is destroyed
        self.num_children = 3

        # Set collision radius based on size # TODO May need to change once size can be visualized
        self.radius = self.size * 9.3

        self.mass = 0.25*math.pi*self.radius*self.radius

        self.vx = velocity[0]
        self.vy = velocity[1]
        self.velocity = (self.vx, self.vy)

        self.angle = np.arctan2(self.vy, self.vx)

        # Set position as specified
        self.position = position

        # Random rotations for use in display or future use with complex hit box
        self.turnrate: float = random.uniform(-100, 100)

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "velocity": self.velocity,
            "size": self.size,
            "mass": self.mass,
            "radius": self.radius,
            "angle": self.angle
        }

    def update(self, delta_time: float = 1/30) -> None:
        """ Move the asteroid based on velocity"""
        self.position = (self.position[0] + self.velocity[0] * delta_time, self.position[1] + self.velocity[1] * delta_time)
        self.angle += delta_time * self.turnrate