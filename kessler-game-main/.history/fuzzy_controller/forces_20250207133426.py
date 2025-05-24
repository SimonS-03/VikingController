import numpy as np
from typing import Dict, Tuple

class Forces():
    def get_force_vector(self):
        pass

class PositionForce(Forces):
    def __init__(self, scale_constant=1):
        self.C = scale_constant

    # get the force vector created from the position of the asteroids
    def get_total_vector(self, ship_state: Dict, asteroids: list) -> np.ndarray:
        force_vectors = np.array([0, 0])
        for ast in asteroids:
            force_vector += self.get_force_vector(ast, ship_state)
        return force_vector
        
    def get_force_vector(self, ship_state: Dict, asteroid_state: Dict) -> np.ndarray:
        dx = ship_state["position"][0] - asteroid_state["position"][0]
        dy = ship_state["position"][1] - asteroid_state["position"][1]

        distance = np.sqrt(dx**2 + dy**2)
        # unit vector in the direction of the force
        f_hat = np.array([dx/distance, dy/distance])

        # accounting for object sizes
        distance -= ship_state["radius"] - asteroid_state["radius"]

        magnitude = self.force_value(distance)
        
        return f_hat * magnitude
    
    # get the magnitude of the force vector
    def force_value(self, distance: float) -> float:
        return self.C / distance

class VelocityForce(Forces):
    def get_force_vector(self):
