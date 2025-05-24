def find_threatlevels(self, ship_state: Dict, game_state: Dict, radius) -> list[tuple[float, float]]:
        ast_idx = self.find_asteroids_inside_radius(ship_state, game_state, radius)
        time_to_collision = []
        for asteroid in game_state["asteroids"]:
            time_to_collision.append(self.time_to_collision(ship_state, asteroid, game_state["map_size"]))
        print(time_to_collision)
        sys.exit()
        return time_to_collision
    
        # Takes ship and asteroid state and returns the time between the object crossing the collision point and the time to collision
    def time_to_collision(self, ship_state: Dict, asteroid: Dict, map_size: tuple[float, float]) -> float:
        print(map_size)
        t1 = self.one_direction_collision(ship_state["position"][0], asteroid["position"][0], ship_state["velocity"][0], asteroid["velocity"][0], map_size[0])
        t2 = self.one_direction_collision(ship_state["position"][1], asteroid["position"][1], ship_state["velocity"][1], asteroid["velocity"][1], map_size[1])
        try:
            print(t1, t2)
            delta_t = abs(t2-t1)
        except TypeError:
            return None, None
        return delta_t, min(t1, t2)
    
        # Time to collision in one coordinate where map_len is the mapsize in the direction of interest
    def one_direction_collision(self, x1, x2, v1, v2, map_len) -> float:
        if v1 == v2:
            return None
        
        if x1 > x2:
            x1, x2 = x2, x1
            v1, v2 = v2, v1

        if v1 >= 0 and v2 <= 0:
            dist = x2-x1
            return dist/(v1-v2)
        elif v1 <= 0 and v2 >= 0:
            dist = x1 + (map_len-x2)
            return dist/(v2-v1)
        elif (v1 < 0 and v2 < 0) and abs(v1) < abs(v2):
            return (x2-x1)/(v1-v2)
        elif (v1 < 0 and v2 < 0) and abs(v1) > abs(v2):
            x1 += map_len
            return (x2-x1)/(v1-v2)
        elif (v1 > 0 and v2 > 0) and abs(v2) < abs(v1):
            return (x2-x1)/(v1-v2)
        elif (v1 > 0 and v2 > 0) and abs(v2) > abs(v1):
            x2 -= map_len
            return (x2-x1)/(v1-v2)

        # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(self, ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx

    # Get threat from one asteroid
    def asteroid_threat(asteroid):
        
        # Input 1
        distance = ctrl.Antecedent(np.linspace(0.0, 1.0, 11))
        # Input 2
        relative_velocity

    
        # asteroid density, assuming each asteroid is of size 4 -> area = pi*(4*8)**2 = 3217
        norm_density = nbr_asteroids * 3217 / (np.pi*r**2)

        # capped at 1
        norm_density = min(1, norm_density)

        # average distance between the asteroids and the ship
        average_distance = 0
        for idx in asteroid_idx:
            current_asteroid = game_state["asteroid"][idx]
            dx = current_asteroid["position"][0]-ship_state["position"][0]
            dy = current_asteroid["position"][1]-ship_state["position"][1]
            average_distance += np.sqrt(dx**2 + dy**2)
        average_distance /= nbr_asteroids