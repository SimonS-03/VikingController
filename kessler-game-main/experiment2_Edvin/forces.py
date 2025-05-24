import numpy as np
from typing import Dict, Tuple, Any
import math

class Forces():
    __slots__ = ('vector', 'magnitude', 'max_magnitude', 'heading')
    def __init__(self) -> None:
        self.vector = None
        self.magnitude = 0 
        self.heading = None

    def actions(self):
        pass

class PositionForce(Forces):
    def __init__(self, ship_state: Dict, game_state: Dict,
                 max_force_distance: float, scale_constant: float=1, radius: float=500) -> None:
        self.max_force_distance = max_force_distance
        self.C = scale_constant
        self.max_magnitude = self.C / (self.max_force_distance**2)
        self.update(ship_state, game_state, radius)
    
    # get the force vector from the vector field created by the POSITIONS of the asteroids
    def update(self, ship_state: Dict, game_state: Dict, radius: float) -> None:
        """ Calculate the total force acting on the ship """
        # get the force vector created from the position of the asteroids
        force_vector = np.array([0.0, 0.0])

        # ship coordinates
        ship_x = ship_state["position"][0]
        ship_y = ship_state["position"][1]
        map_size = game_state["map_size"]
        num_asteroids = 0
        for idx, asteroid in enumerate(game_state["asteroids"]):
            # distance between ship and asteroid accounting for map size
            dx = ship_x - asteroid["position"][0]
            if dx > 0:
                over_edge_dx = dx - map_size[0]
                dx = dx if abs(dx) < abs(over_edge_dx) else over_edge_dx
            else:
                over_edge_dx = dx + map_size[0]
                dx = dx if abs(dx) < abs(over_edge_dx) else over_edge_dx

            dy = ship_y - asteroid["position"][1]
            if dy > 0:
                over_edge_dy = dy - map_size[1]
                dy = dy if abs(dy) < abs(over_edge_dy) else over_edge_dy
            else:
                over_edge_dy = dy + map_size[1]
                dy = dy if abs(dy) < abs(over_edge_dy) else over_edge_dy
            distance = np.sqrt(dx**2 + dy**2)
            # only consider asteroids inside a radius
            if distance < radius:
                num_asteroids += 1
                # unit vector in the direction of the force
                f_hat = np.array([dx/distance, dy/distance])
                # accounting for object sizes
                distance -= ship_state["radius"] - asteroid["radius"]
                mass = asteroid["mass"]
                magnitude = self.force_value(distance, mass)
                force_vector += f_hat * magnitude
        #print(num_asteroids)
        self.vector = force_vector    
        self.magnitude = np.sqrt(force_vector[0]**2 + force_vector[1]**2)
        if self.magnitude != 0:
            self.heading = (180/np.pi)*np.arctan2(force_vector[1], force_vector[0])
        else:
            self.heading = 0
    
    # get the magnitude of the force vector
    def force_value(self, distance: float, mass: float) -> float:
        if distance < self.max_force_distance:
            return self.max_magnitude
        return self.C / (distance**2) * mass /

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "vector": self.vector,
            "magnitude": self.magnitude,
            "max_magnitude": self.max_magnitude,
            "heading": self.heading
            }
        
#class VelocityForce(Forces):
#    def get_force_vector(self):

