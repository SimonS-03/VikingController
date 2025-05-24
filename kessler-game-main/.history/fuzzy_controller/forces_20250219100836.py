import numpy as np
from typing import Dict, Tuple, Any
import math

class Forces():
    __slots__ = ('vector', 'magnitude', 'max_magnitude', 'heading')
    def __init__(self) -> None:
        self.vector = None
        self.magnitude = 0 
        self.max_magnitude = None
        self.heading = None

    def get_force_vector(self):
        pass

class PositionForce(Forces):
    def __init__(self, ship_state: Dict, game_state: Dict, scale_constant: float=1000000, radius: float=500) -> None:
        self.C = scale_constant
        self.update(ship_state, game_state, radius)
    
    # get the force vector from the vector field created by the POSITIONS of the asteroids
    def update(self, ship_state: Dict, game_state: Dict, radius: float) -> None:
        """ Recalculate the force acting on the ship """
        asteroid_idx = self.find_asteroids_inside_radius(ship_state, game_state, radius)
        asteroids_nearby = [game_state["asteroids"][idx] for idx in asteroid_idx]

        # get the force vector created from the position of the asteroids
        force_vector = np.array([0.0, 0.0])
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
        self.heading = (180/np.pi)*np.arctan(force_vector[1] / force_vector[0])

    # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(self, ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx
    
    # get the magnitude of the force vector
    def force_value(self, distance: float) -> float:
        # distance threshold where the force doesnt keep growing
        cap_distance = 16
        self.max_magnitude = self.C / (cap_distance**2)
        if distance > cap_distance:
            return self.C / distance
        else:
            return self.max_magnitude

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "vector": self.vector,
            "magnitude": self.magnitude,
            "max_magnitude": self.max_magnitude,
            "heading": self.heading,  
            }

# create scalar field created by the velocity of the asteroids     1 
class VelocityForce(Forces):
    __slots__ = ('scalar_field')
    def __init__(self, ship_state: Dict, game_state: Dict) -> None:
        self.update(ship_state, game_state)

    # assign a scalar value to each point in the grid
    def update(self, ship_state: Dict, game_state: Dict) -> None:
        map_size = game_state["map_size"]
        field = []
        for x in map_size[0]:
            to_append = []
            for y in map_size[1]:
                r = np.sqrt(x**2 + y**2)
                theta = np.arctan(y/x) * (180/np.pi)
                to_append.append(self.get_value_at_point(game_state, x, y))
    # get the scalar value at (x, y)
    def get_value_at_point(self, game_state: Dict, x, y) -> float:
        for asteroid in game_state["asteroids"]:
             

    # get the magnitude of the
    def force_value(self, r, theta):
        #return
    
    @property
    def state(self) -> Dict[str, Any]:

