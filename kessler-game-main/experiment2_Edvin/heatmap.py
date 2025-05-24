import numpy as np
from typing import Dict

class Heatmap:
    def __init__(self, grid_size: float, x_boundary: tuple[float, float], y_boundary: tuple[float, float],
                resolution: float, dt: float, time_steps: float) -> None:

        self.grid = np.empty(grid_size, dtype=object)
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.grid[i, j] = {"ttcs": [], "processed_asteroids": set()}
        self.resolution = resolution

        self.x_min = x_boundary[0]
        self.x_max = x_boundary[1]
        self.y_min = y_boundary[0]
        self.y_max = y_boundary[1]
        
        
        self.dt = dt
        self.time_steps = time_steps                                              
    
    def update_map(self, game_state: Dict, lambda_ttc: float, p: float, sigma: float) -> None:
        """
        Update the heatmap looping through asteroids
        """
        asteroids = game_state["asteroids"]
        
        # compute ttc and add to danger functions
        for asteroid_idx, asteroid in enumerate(asteroids):
            trajectory = self.get_trajectory(asteroid)
            radius = asteroid["radius"]
            grid_radius = int(radius / self.resolution)

            for step, (x_pred, y_pred) in enumerate(trajectory):
                grid_x = int((x_pred - self.x_min) / self.resolution)
                grid_y = int((y_pred - self.y_min) / self.resolution)
                # time to collision at the current grid cell
                ttc = step * self.dt
                # check all grid cells within the radius of the asteroid
                for dx in range(-grid_radius, grid_radius + 1):
                    for dy in range(-grid_radius, grid_radius + 1):
                        # distance from cell to the asteroid's position
                        distance = np.sqrt(dx**2 + dy**2)
                        if distance <= grid_radius:
                            neighbour_x = grid_x + dx
                            neighbour_y = grid_y + dy

                            if 0 <= neighbour_x < self.grid.shape[0] and 0 <= neighbour_y < self.grid.shape[1]:
                                # check if the cell has been previously processed
                                if asteroid_idx not in self.grid[neighbour_x, neighbour_y]["processed_asteroids"]:
                                    self.grid[neighbour_x, neighbour_y]["ttcs"].append(ttc)
                                    self.grid[neighbour_x, neighbour_y]["processed_asteroids"].add(asteroid_idx)
        return
    
    def get_trajectory(self, asteroid: Dict) -> list:
        trajectory = []
        pos = asteroid["position"]
        vel = asteroid["velocity"]
        for t in range(self.time_steps):
            trajectory.append((pos[0] + vel[0] * t * self.dt, pos[1] + vel[1] * t * self.dt))
        return trajectory


"""for i in range(self.grid_width):
            for j in range(self.grid_height):
                x_cell = self.x_min + i * self.resolution
                y_cell = self.y_min + j * self.resolution
                total_danger = 0
                for asteroid in asteroids:
                    asteroid_coord = asteroid["position"]
                    distance = np.sqrt((x_cell - asteroid_coord[0])**2 + (y_cell - asteroid_coord[1])**2)
                    total_danger += np.exp(-distance**2/(2*sigma))
                self.grid[i, j] = total_danger"""

