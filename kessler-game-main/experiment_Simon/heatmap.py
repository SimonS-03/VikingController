import numpy as np
from bresenham import bresenham
from typing import Dict
import sys
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

class Heatmap:
    def __init__(self, x_boundary: tuple[float, float], y_boundary: tuple[float, float],
                resolution: float, T: float=10, max_ttc: float=15, array_size: tuple[float, float] = (500, 400)) -> None:
        self.resolution = resolution

        self.grid_size = (int(1000 / self.resolution), int(800 / self.resolution))
        self.array_size = (int(array_size[0]/self.resolution), int(array_size[1]/self.resolution))

        self.max_ttc = max_ttc
        self.ship_position = (int(self.grid_size[0]/2), int(self.grid_size[1]/2))
        self.resolution = resolution
        self.ship_ttc = None

        self.T = T
        self.grid = np.empty(self.grid_size, dtype=object)
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                #self.grid[i, j] = {"index": (i, j), "ttcs": [np.float64(max_ttc), {np.float64(round(max_ttc, 2))}]}
                self.grid[i, j] = {"ttcs": [max_ttc, set()]}
            
        self.grid_array = None
        self.grid_array_gaussian = None
        self.ship_position_array = None
        self.computed_asteroids = dict()
        self.frameSincePlot = 0
        self.best_dir = None  
        self.mapArtist = None
        self.first_plot = True

        self.moduleActive = ""
        self.explain = False

        self.old_keys = set()

        plt.ion()

    

    def actions(self, ship_state: Dict, game_state: Dict):
        self.update_map(ship_state, game_state) 
        if self.explain: # Controlls if heatmap is plotted or not
            if self.frameSincePlot > 5:
                self.plot()
                self.frameSincePlot = 0
            self.frameSincePlot += 1

    
    def get_Key(asteroid: Dict, game_state: Dict):
        "Returns a hash key for an asteroid"
        initialPos = (round(asteroid["position"][0]-game_state["time"]*asteroid["velocity"][0])%1000, round(asteroid["position"][1]-game_state["time"]*asteroid["velocity"][1])%800, 4)
        #print(initialPos)
        hashKey = hash((initialPos, int(asteroid["velocity"][0]*100), int(asteroid["velocity"][1]*100), round(asteroid["size"])))
        
        #print(f"Hash {hashKey}, created from {key}")
        return hashKey

    def update_map(self, ship_state: Dict, game_state: Dict) -> None:
        """
        Update the heatmap looping through asteroids
        """
        asteroids = game_state["asteroids"] 
        #old_keys = set(self.computed_asteroids.keys())

        
        new_keys = set()
        recomputed_asteroids = dict()
        #print(f"Nbr of asteroids: {len(asteroids)}")
        # compute ttc
        for asteroid in asteroids:

            key = Heatmap.get_Key(asteroid, game_state)
            if key in self.old_keys:
                if (self.computed_asteroids[key][1]-game_state["time"]) > 2.1:
                    new_keys.add(key)
                    #print("Skipped process")
                    #print((self.computed_asteroids[key][1]-game_state["time"]))
                    continue
                else:
                    recomputed_asteroids[key] = self.computed_asteroids[key][0].copy()
                    #print("recomputing")



            start_point = np.array(asteroid["position"])
            grid_start = (start_point / self.resolution).astype(int)

            vel = np.array(asteroid["velocity"])
            grid_vel = np.sqrt(vel[0]**2 + vel[1]**2) / self.resolution

            end_point = (start_point + vel * self.T).astype(int) # TODO attach time to time_limit
            grid_end = (end_point / self.resolution).astype(int)

            line_points = list(bresenham(grid_start[0], grid_start[1], grid_end[0], grid_end[1]))  
            
            points = set()
            point_and_ttc = set()

            radius = asteroid["radius"]
            grid_radius = int(np.ceil(radius / self.resolution)) + 4  # was 2
            #if grid_radius == 0: grid_radius += 1

            for i in range(len(line_points)):
                x1, y1 = line_points[i]
                for dx in range(-grid_radius, grid_radius+1):
                    for dy in range(-grid_radius, grid_radius+1):
                        if np.sqrt(dx**2 + dy**2) > grid_radius: 
                            continue
                        
                        x, y = x1 + dx, y1 + dy
                        if (x, y) in points: 
                            continue

                        points.add((x, y))

                        xRel, yRel = x-grid_start[0], y-grid_start[1]
                        xWrapped, yWrapped = x%self.grid_size[0], y%self.grid_size[1]
                        
                        #print(f"Original: {x}, {y} -> Wrapped: {xWrapped}, {yWrapped}")

                        ttc = np.sqrt(xRel**2 + yRel**2)/grid_vel + game_state["time"]


                        if self.grid[xWrapped, yWrapped]["ttcs"][0] > ttc:
                            #self.update_lowest_ttc(self.grid[xWrapped, yWrapped]["ttcs"], game_state)
                            self.grid[xWrapped, yWrapped]["ttcs"][0] = ttc


                        self.grid[xWrapped, yWrapped]["ttcs"][1].add(ttc)
                        point_and_ttc.add(((xWrapped, yWrapped), ttc))


            #print(f"computed heat signature for asteroid with key {key}")

            self.computed_asteroids[key] = (point_and_ttc, game_state["time"]+self.T*(1-np.random.rand()*0.5))
            new_keys.add(key)

        
        keys_to_remove = set()
        
        for old_key in self.old_keys:
            recompute = False
            if not (old_key in new_keys):
                elements = self.computed_asteroids[old_key][0]
            elif old_key in recomputed_asteroids:
                elements = recomputed_asteroids[old_key]
                recompute = True
            else:
                continue
            
            elems_missed = 0
            for elem in elements:
                grid_elem = self.grid[elem[0][0], elem[0][1]]["ttcs"]
                ttcs = grid_elem[1]
                
                ttc = elem[1]
                

                found_ttc = None
                # Look around (if coordinate got changed somehow)

                found_ttc = next((t for t in ttcs 
                    if abs(t - ttc) < 1e-6), None)

                if not found_ttc is None:
                    ttcs.remove(found_ttc)
                    if grid_elem[0] == found_ttc:
                        self.update_lowest_ttc(grid_elem, game_state)
                else:
                    elems_missed += 1
                    #print(f"Looking for {ttc} in {self.grid[coord[0], coord[1]]["ttcs"][1]}")
                    
            #print(f"Missed {elems_missed} elems with {recompute} value in recompute")
            if not recompute: keys_to_remove.add(old_key)

        
        for removable_key in keys_to_remove:
            self.old_keys.remove(removable_key)
            del self.computed_asteroids[removable_key]
        
        self.old_keys.update(new_keys)
        self.update_array(ship_state, game_state)
        #self.ship_ttc = self.grid[self.ship_position[0], self.ship_position[1]]["ttcs"][0]-game_state["time"]
        future_time = 0.2
        self.ship_position_array = (int(self.array_size[0]//2 + future_time*ship_state["velocity"][0] / self.resolution), int(self.array_size[1]//2 + future_time*ship_state["velocity"][1] / self.resolution))
        self.ship_ttc = self.grid_array[self.ship_position_array[0], self.ship_position_array[1]]
        
    def update_lowest_ttc(self, entry: tuple[float, set[float]], game_state: Dict):
        lowest = self.max_ttc + game_state["time"]
        for ttc in entry[1]:
            if lowest > ttc > game_state["time"]:
                lowest = ttc
        #if entry[0] in entry[1]:
        #    entry[1].remove(entry[0])
        entry[0] = lowest

    
    def update_array(self, ship_state: Dict, game_state: Dict):
        x_low = int(ship_state["position"][0]//self.resolution - self.array_size[0]//2)
        y_low = int(ship_state["position"][1]//self.resolution - self.array_size[1]//2)

        if not self.grid_array is None:
            for i in range(self.array_size[0]):
                for j in range(self.array_size[1]):
                    
                    current_ttcs = self.grid[(i+x_low)%self.grid_size[0], (j+y_low)%self.grid_size[1]]["ttcs"]
                    if current_ttcs[0]-game_state["time"] < 10:
                        self.update_lowest_ttc(current_ttcs, game_state)
                    self.grid_array[i, j] = round(current_ttcs[0] - game_state["time"], 2)

                    """
                    if current_ttcs[0] < game_state["time"]:
                        self.update_lowest_ttc(current_ttcs, game_state)
                    
                    if current_ttcs[0] == self.max_ttc:
                        self.grid_array[i, j] = round(current_ttcs[0], 2)
                    else:
                        self.grid_array[i, j] = round(current_ttcs[0] - game_state["time"], 2)"""
            return
        
        self.grid_array = np.zeros(shape = self.array_size)

        for i in range(self.array_size[0]):
            for j in range(self.array_size[1]):
                    self.grid_array[i, j] = round(self.grid[(i+x_low)%self.grid_size[0], (j+y_low)%self.grid_size[1]]["ttcs"][0]-game_state["time"], 2)
            


    # returns the gradient at a point (x, y)
    def get_gradient_and_ttc(self, x, y, grad_x, grad_y):
        if 0 <= x < self.array_size[0] and 0 <= y < self.array_size[1]:
            ttc = self.grid_array_gaussian[x, y]
            dx, dy = grad_x[x, y], grad_y[x, y]
        else:
            ttc, dx, dy = 0, 0, 0
        return ttc, dx, dy
    
    # take gradient at a number of points on the edges of the ship, then sum them weighted by the ttc
    def weighted_gradient(self, ship_radius: float, points: int, ship_state: Dict, game_state: Dict) -> tuple[float, float]:
        
        #self.update_array(ship_state, game_state)
        self.apply_gaussian(sigma = 2.5)
        grad_x, grad_y = np.gradient(self.grid_array_gaussian)

        grid_radius = int(ship_radius / self.resolution)
        theta_list = [2*np.pi/points * i for i in range(points)]   
        vector_sum = np.zeros(2, dtype=float)
        for theta in theta_list:
            x = int(self.array_size[0]/2) + int(grid_radius * np.cos(theta))
            y = int(self.array_size[1]/2) + int(grid_radius * np.sin(theta))
            ttc, dx, dy = self.get_gradient_and_ttc(x, y, grad_x, grad_y)
            vector_sum += 1/(1+ttc) * np.array([dx, dy])
        return tuple(vector_sum)

    
    def apply_gaussian(self, sigma):
        self.grid_array_gaussian = gaussian_filter(self.grid_array, sigma=sigma)

    
    def plot(self):
        self.apply_gaussian(sigma = 2.5)

        if self.first_plot:
            self.mapArtist = plt.imshow(self.grid_array.T, cmap='hot_r', interpolation='nearest', origin="lower")
            
            bar = plt.colorbar()
            bar.set_label("time to collision (seconds)")
            self.shipArtist = plt.scatter(self.ship_position_array[0], self.ship_position_array[1], color='blue', marker='o', label='Ship')
            plt.legend()
            #plt.title(label="Heat map of TTC value")
            plt.ylabel("grid Value (y)")
            plt.xlabel("grid value (x)")

            self.first_plot = False
            plt.show(block = False)
            
        plt.title(self.moduleActive)
        self.shipArtist.set_offsets((self.ship_position_array[0], self.ship_position_array[1]))
        self.mapArtist.set_data(self.grid_array_gaussian.T)
        plt.draw()


    
    @property
    def name(self) -> str:
        return "Heatmap"
