"""

    # Bias toward the gradient direction. then randomize a turn rate and pair it with the correct duration
    def sample_queue_using_gradient(self, num_queues: int, current_dir: Tuple[float, float], grad_dir: Tuple[float, float], std_dev: float = 80) -> List[List[Dict]]:
        # ------------------  First rotate ------------------
        # randomize direction
        offsets = np.random.normal(0, std_dev, num_queues)
        biased_dirs = (grad_dir + offsets) % 360 
        # get difference in angle with the correct sign
        diffs = (biased_dirs - current_dir + 180) % 360 - 180
        #turn_rates = [60, 120, 180]
        #random_turn_rate = abs(diff)/diff * random.choice(turn_rates)
        diffs = np.where(np.abs(diffs) < 1e-6, 1e-6, diffs)

        turn_rates = np.sign(diffs) * 180
        turn_durations = (np.abs(diffs) / 180 * 10).astype(int)

        thrust_options = np.array([0, 120, 240, 360, -480])
        thrusts = np.random.choice(thrust_options, size=self.num_sims)
        thrust_durations = np.random.randint(1, 10, size=self.num_sims)

        queues = []

        for i in range(self.num_sims):
            queues.append([
                {"thrust": 0.0, "turn_rate": turn_rates[i], "duration": turn_durations[i]},
                {"thrust": float(thrusts[i]), "turn_rate": 0.0, "duration": thrust_durations[i]}
            ])

            self.durations.extend(turn_durations + thrust_durations)

        return queues

    def run_single_sim(self, scenario: SimulationScenario, actions_queue: List[Dict], duration: int) -> Tuple[float, List[Dict]]:
        """
        # Run a single simulation and return (fitness_score, actions_used)
        """

        scenario = scenario
        # Set the scenario frame limit to be the duration of the actions + the max ttc
        scenario.update_frame_limit(duration + self.max_ttc*30)

        action_array = np.array([(a['thrust'], a['turn_rate'], a['duration'], a['fire'], a['mine'])
                                for a in actions_queue], dtype=self.action_prototyp)
    
        # game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario
        game = TrainerEnvironment(settings=self.game_settings)  # Use this for max-speed, no-graphics simulation
            
        # Run the game with an action_queue from the action_queues
        perf_data, stop_reason_name, total_frames = game.run(sim_scenario=scenario, controllers=[SimulationController(action_array)])

        # Get the fitness score of this move sequence and update the best_fitness
        fitness = self.get_fitness(stop_reason_name, total_frames, duration)
        #print(actions_queue, "fitness:", fitness)
        return fitness, action_array


        # Simulate using threads
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self.run_single_sim, 
                    scenario_template,
                    self.fast_queue_copy(queue),
                    self.durations[i]
                ): i for i, queue in enumerate(actions_queues)
            }
            
            for future in as_completed(futures):
                sim_start = time.perf_counter()
                # if (time.perf_counter() - start_time) >= self.max_duration:
                #     future.cancel() # stop if timeout reached
                #     continue
                fitness, actions = future.result()
                if fitness > self.best_fitness:
                    
                    self.best_fitness = fitness 
                
                    self.best_actions = actions
                print(f"Sim{futures[future]} finished in {time.perf_counter() - sim_start:.7f} seconds")


    # ORIGINAL APPROACH: randomly choose from predefined actions (defined above)
    # randomly sample an action queue. An actions queue is a queue of actions to be performed until the frame limit 
    def sample_actions_queue(self, probs) -> List[Dict]:
        queue = []
        tot_frame = 0
        while tot_frame < self.frame_limit:
            next_action = self.sample_action(probs)
            duration = 10 # random.randint(self.min_duration, self.max_duration)
            next_action["duration"] = duration
            queue.append(next_action)
            tot_frame += duration
        return queue

    def sample_action(self, probs):
        chosen_action = copy.deepcopy(random.choices(ACTIONS, weights = probs, k=1)[0])
        return chosen_action
    
    # get bias score for an action
    def get_action_bias(self, action, turn_weight, thrust_weight):
        score = 1.0
        if action["turn_rate"] != 0:
            score *= turn_weight
        if action["thrust"] != 0:
            score *= thrust_weight
        #return score
        return 1

    def softmax(self, x, temperature=1.0):
        x = [i / temperature for i in x]
        e_x = [math.exp(i) for i in x]
        total = sum(e_x)
        return [i / total for i in e_x]

# difference between the gradient direction and the ship direction
        delta_theta = abs(self.best_theta - ship_ownstate["heading"]) % 360 # [0, 360]
        delta_theta = min(delta_theta, 360 - delta_theta) # [0, 180]
        assert 0 <= delta_theta <= 180 
        print("best_dir:", self.best_theta, delta_theta)

        # normalize
        norm_theta = min(delta_theta/90, 1)

        # bias weights
        turn_weight = norm_theta
        forward_thrust_weight = 1 - norm_theta
        #reverse_thrust_weight = 1 - norm_theta

        # assign bias to the actions
        bias_scores = [self.get_action_bias(a, turn_weight, forward_thrust_weight) for a in ACTIONS2]
        print(bias_scores)

        probs = self.softmax(bias_scores, temperature=0.5)"""

# this checks the time to collision on the edges of the ship. Only called when 
    # the center ttc is high to avoid high computations
    def get_ttc_on_circumference(self, game_state: Dict, points: int=2) -> float:
        shortest_time = None
        theta_list = [2*np.pi/points * i for i in range(points)]  
        # loop through a number of evenly spaced points along the ship circumference
        for theta in theta_list:
            x = self.position[0] + int(self.radius * np.cos(theta))
            y = self.position[1] + int(self.radius * np.sin(theta))

            for asteroid in game_state["asteroids"]:
                asteroid_coord = asteroid["position"]

                # distance between the asteroid and the point on the ship that we are checking
                dx = x - asteroid_coord[0]
                dy = y - asteroid_coord[1]
                distance = np.sqrt(dx**2 + dy**2)
                asteroid_speed = np.sqrt(asteroid["velocity"][0]**2 + asteroid["velocity"][1]**2)
                time_to_collision = distance / (asteroid_speed + 1e10)
                time_to_collision = 10 if time_to_collision > 10 else time_to_collision
                if shortest_time is None or time_to_collision < shortest_time:
                    shortest_time = time_to_collision
        print("shortest_time", shortest_time)
        return shortest_time


    # get the time to collision for the current position 
    def get_ttc(self, game_state: Dict, ship_state: Dict, margin: float = 0) -> float:
        """
        Called by the game to check the time to collision of the ship in the current spot
        """
        lowest_ttc = None
        for asteroid in game_state["asteroids"]:
            asteroid_pos = np.array(asteroid["position"])
            asteroid_vel = np.array(asteroid["velocity"])

            ship_pos = np.array(ship_state["position"])
            ship_vel = np.array(ship_state["velocity"])
            asteroid_speed = np.linalg.norm(asteroid_vel)

            rel_pos = ship_pos - asteroid_pos
            distance = np.linalg.norm(rel_pos)
            
            # skip if the asteroid is stationary
            if asteroid_speed == 0:
                continue

            dot = np.dot(asteroid_vel, rel_pos)

            # skip if they are moving away from eachother
            if dot <= 0:
                continue

            # Calculate what theta would result in a collision
            safe_distance = asteroid["radius"] + ship_state["radius"] + margin

            # if they have already collided
            if np.linalg.norm(rel_pos) < safe_distance:
                return 0.0

            theta = np.arccos(dot / (distance * asteroid_speed))
            min_theta = np.arctan(safe_distance / distance)

            if theta < min_theta:
                time_to_collision = distance / asteroid_speed
                if lowest_ttc is None or time_to_collision < lowest_ttc:
                    lowest_ttc = time_to_collision
        return lowest_ttc

for i in range(self.grid_width):
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
        return trajectory