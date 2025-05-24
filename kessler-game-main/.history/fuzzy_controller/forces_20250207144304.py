import numpy as np
from typing import Dict, Tuple, Any
import math

class Forces():
    __slots__ = ('vector', 'magnitude', 'angle')
    def __init__(self) -> None:
        self.vector = None
        self.magnitude = 0 
        self.angle = None

    def get_force_vector(self):
        pass

class PositionForce(Forces):
    def __init__(self, scale_constant=1) -> None:
        self.C = scale_constant
        self.update()
    
    # get the force vector from the vector field created by the POSITIONS of the asteroids
    def update(self, ship_state: Dict, game_state: Dict, radius: float):
        """ Recalculate the force acting on the ship """
        asteroid_idx = self.find_asteroids_inside_radius(radius)
        asteroids_nearby = [game_state["asteroids"][idx] for idx in asteroid_idx]

        # get the force vector created from the position of the asteroids
        force_vector = np.array([0, 0])
        # ship coordinates
        ship_x = ship_state["position"][0]
        ship_y = ship_state["position"][1]

        # sum all force vectors
        for asteroid in asteroids_nearby:
            dx = ship_x - asteroid["position"][0]
            dy = ship_y - asteroid["position"][1]
            distance = np.sqrt(dx**2 + dy**2)

            # unit vector in the direction of the force
            f_hat = np.array([dx/distance, dy/distance])

            # accounting for object sizes
            distance -= ship_state["radius"] - asteroid["radius"]

            magnitude = self.force_value(distance)
            force_vector += f_hat * magnitude
        self.vector = force_vector
        self.magnitude = np.sqrt(force_vector[0]**2 + force_vector[1]**2)
        self.angle = np.arctan(force_vector[1] - force_vector[0])

    # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx
    
    # get the magnitude of the force vector
    def force_value(self, distance: float) -> float:
        return self.C / distance

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "vector": self.vector,
            "magnitude": self.angle,
            "angle": self.angle 
            }
        
#class VelocityForce(Forces):
#    def get_force_vector(self):

