import numpy as np
from bresenham import bresenham
from typing import Dict
import sys
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

class Heatmap:
    def __init__(self, x_boundary: tuple[float, float], y_boundary: tuple[float, float],
                resolution: float, T: float=15, max_ttc: float=1000) -> None:
        self.resolution = resolution

        self.x_min = x_boundary[0]
        self.x_max = x_boundary[1]
        self.y_min = y_boundary[0]
        self.y_max = y_boundary[1]
        self.grid_width = int((self.x_max-self.x_min) / resolution)
        self.grid_height = int((self.y_max-self.y_min) / resolution)
        self.ship_position = (int(self.grid_width/2), int(self.grid_height/2))
        self.ship_ttc = None

        self.grid = np.empty((self.grid_width, self.grid_height), dtype=object)
        for i in range(self.grid_width):
            for j in range(self.grid_height):
                self.grid[i, j] = {"index": (i, j), "ttcs": np.float64(max_ttc)}
            
        self.grid_array = None
        # simulation time of asteroids
        self.T = T
        # best direction [dx, dy]
        self.best_dir = None

    def actions(self, ship_state: Dict, game_state: Dict):
        self.update_map(game_state) 
        self.create_array()
        self.weighted_gradient(32, 4)
        self.plot()                                  
    
    def update_map(self, game_state: Dict) -> None:
        """
        Update the heatmap looping through asteroids
        """
        asteroids = game_state["asteroids"] 
        
        # compute ttc
        for asteroid in asteroids:
            start_point = np.array(asteroid["position"])
            grid_start = ((start_point - np.array([self.x_min, self.y_min])) / self.resolution).astype(int)
            vel = np.array(asteroid["velocity"])
            grid_vel = np.sqrt(vel[0]**2 + vel[1]**2) / self.resolution
            end_point = start_point + vel * self.T
            grid_end = ((end_point - self.x_min) / self.resolution).astype(int)

            line_points = list(bresenham(grid_start[0], grid_start[1], grid_end[0], grid_end[1]))  
            line_points = set((int(point[0]), int(point[1])) for point in line_points)

            # add points at radius r or closer
            radius = asteroid["radius"]
            grid_radius = int(radius / self.resolution)

            elems_to_add = set()
            for x1, y1 in line_points:
                for dx in range(-grid_radius, grid_radius+1):
                    for dy in range(-grid_radius, grid_radius+1):
                        x, y = x1 + dx, y1 + dy
                        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                            distance = np.sqrt((x-x1)**2 + (y-y1)**2)
                            if distance <= grid_radius:
                                elems_to_add.add((x, y))
            line_points.update(elems_to_add)

            # add ttc's 
            start_x = grid_start[0]
            start_y = grid_start[1]
            for coord in line_points:
                x, y = coord
                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                    grid_distance = np.sqrt((start_x-coord[0])**2 + (start_y-coord[1])**2)
                    ttc = grid_distance * grid_vel
                    current_ttcs = self.grid[x, y]["ttcs"]
                    if ttc < current_ttcs: #all(ttc < other_ttc for other_ttc in current_ttcs):
                        self.grid[x, y]["ttcs"] = round(ttc, 2)
            self.ship_ttc = self.grid[self.ship_position[0], self.ship_position[1]]["ttcs"]
        return

    def create_array(self):
        self.grid_array = []
        for i in range(self.grid_width):
            row = []
            for j in range(self.grid_height):
                    row.append(self.grid[i, j]["ttcs"]) 
            self.grid_array.append(row)
        self.grid_array = np.array(self.grid_array)
        print(self.grid_array)

    # returns the gradient at a point (x, y)
    def get_gradient_and_ttc(self, x, y):
        #self.apply_gaussian()
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            grad_x, grad_y = np.gradient(self.grid_array)
            ttc = self.grid_array[x, y]
            dx, dy = grad_x[x, y], grad_y[x, y]
        else:
            ttc, dx, dy = 0, 0, 0
        return ttc, dx, dy
    
    # take gradient at a number of points on the edges of the ship, then sum them weighted by the ttc
    def weighted_gradient(self, ship_radius: float, points: int) -> tuple[float, float]:
        grid_radius = int(ship_radius / self.resolution)
        theta_list = [2*np.pi/points * i for i in range(points)]   
        vector_sum = np.zeros(2, dtype=float)
        for theta in theta_list:
            x = self.ship_position[0] + int(grid_radius * np.cos(theta))
            y = self.ship_position[1] + int(grid_radius * np.sin(theta))
            ttc, dx, dy = self.get_gradient_and_ttc(x, y)
            vector_sum += 1/(1+ttc) * np.array([dx, dy])
        return tuple(vector_sum)
    #def smooth_gradient(self) -> tuple[float, float]:

    
    def apply_gaussian(self):
        self.grid_array = gaussian_filter(self.grid_array, sigma=2)
        return
    
    def plot(self):
        grid = np.array(self.grid_array)

        plt.imshow(grid.T, cmap='hot', interpolation='nearest', origin="lower")
        plt.scatter(self.ship_position[0], self.ship_position[1], color='blue', marker='o', label='Ship')
        plt.legend()
        plt.title(label="Heat map of TTC value")
        plt.show()

    # find safest direction for the ship to move
    def find_direction(self, lookahead: int, num_directions: int, decay: float=0.95) -> tuple[float, float]:
        x, y = self.grid_width/2, self.grid_height/2
        directions = np.linspace(0, 2 * np.pi, num_directions, endpoint=False)
        best_dir = None
        max_safety = -float('inf')
        for theta in directions:
            dx, dy = np.cos(theta), np.sin(theta)
            safety_score = 0 
            weight = 1.0

            for step in range(1, lookahead + 1):
                sample_x = int(x + step * dx)
                sample_y = int(y + step * dy)

                if 0 <= sample_x < self.grid_width and 0 <= sample_y < self.grid_height:
                    current_ttc = self.grid[sample_x, sample_y]["ttcs"][0] if self.grid[sample_x, sample_y]["ttcs"] else 0 
                    safety_score += weight * current_ttc
                    weight *= decay
            
            if safety_score > max_safety:
                max_safety = safety_score
                best_dir = (dx, dy)
        return best_dir
    
    @property
    def name(self) -> str:
        return "Heatmap"

"""for i in range(self.grid_width):
            for j in range(self.grid_height):
                x_cell = self.x_min + i * self.resolution
                y_cell = self.y_min + j * self.resolution
                total_danger = 0
                for asteroid in asteroids:
                    asteroid_coord = asteroid["position"]
                    distance = np.sqrt((x_cell - asteroid_coord[0])**2 + (y_cell - asteroid_coord[1])**2)
                    total_danger += np.exp(-distance**2/(2*sigma))
                self.grid[i, j] = total_danger
                
    for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.grid[i, j] = {"ttcs": [], "processed_asteroids": set()}
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
                
            
            def get_trajectory(self, asteroid: Dict) -> list:
        trajectory = []
        pos = asteroid["position"]
        vel = asteroid["velocity"]
        for t in range(self.time_steps):
            trajectory.append((pos[0] + vel[0] * t * self.dt, pos[1] + vel[1] * t * self.dt))
        return trajectory"""
