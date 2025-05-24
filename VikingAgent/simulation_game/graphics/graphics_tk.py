# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import os
from tkinter import Tk, Canvas, NW
from PIL import Image, ImageTk  # type: ignore[import-untyped]

from typing import Dict, Optional, List
from .graphics_base import KesslerGraphics
from ..ship import Ship
from ..asteroid import Asteroid
from ..sim_scenario import SimulationScenario
from ..team import Team


class GraphicsTK(KesslerGraphics):
    def __init__(self, UI_settings: Optional[Dict[str, bool]] = None) -> None:
        # UI settings
        # default_ui = {'ships': True, 'lives_remaining': True, 'accuracy': True, 'asteroids_hit': True}
        UI_settings = {} if UI_settings is None else UI_settings
        self.show_ships = UI_settings.get('ships', True)
        self.show_lives = UI_settings.get('lives_remaining', True)
        self.show_accuracy = UI_settings.get('accuracy', True)
        self.show_asteroids_hit = UI_settings.get('asteroids_hit', True)
        self.show_shots_fired = UI_settings.get('shots_fired', False)
        self.show_controller_name = UI_settings.get('controller_name', True)
        self.script_dir = os.path.dirname(__file__)
        self.img_dir = os.path.join(self.script_dir, "images")

    def sort_list(self, order, list_to_order):
        i = len(order)
        sorted_list = [None] * (len(list_to_order) + (len(order)))
        for value in list_to_order:
            try:
                idx = order.index(value)
                sorted_list[idx] = value
            except ValueError:  # value not found in the list
                sorted_list[i] = value
                i = i + 1
        return [x for x in sorted_list if x != None]

    def start(self, scenario: SimulationScenario) -> None:
        self.game_width = scenario.map_size[0]
        self.game_height = scenario.map_size[1]
        self.max_time = scenario.time_limit
        self.score_width = 385
        self.window_width = self.game_width + self.score_width
        ship_radius: int = int(scenario.ships()[0].radius * 2 - 5)

        # create and center main window
        self.window = Tk()
        self.window.title('Kessler')
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width / 2 - self.window_width / 2)
        center_y = int(screen_height / 2 - self.game_height / 2)
        self.window.geometry(f'{self.window_width}x{self.game_height}+{center_x}+{center_y}')

        # create canvas for object and image display
        self.game_canvas = Canvas(self.window, width=self.window_width, height=self.game_height, bg="black")
        self.game_canvas.pack()
        self.window.update()

        # Grab and open sprite images in python
        default_images = ["playerShip1_green.png",
                            "playerShip1_orange.png",
                            "playerShip2_orange.png",
                            "playerShip3_orange.png"]

        img_list = []
        for file in os.listdir(self.img_dir):
            if file.endswith(".png") or file.endswith(".jpg"):
                img_list.append(file)
        img_list2 = self.sort_list(default_images, img_list)
        self.image_paths = [os.path.join(self.img_dir, img) for img in img_list2]

        self.num_images = len(self.image_paths)
        self.ship_images = [(Image.open(image)).resize((ship_radius, ship_radius)) for image in self.image_paths]
        self.ship_sprites = [ImageTk.PhotoImage(img) for img in self.ship_images]
        self.ship_icons = [ImageTk.PhotoImage((Image.open(image)).resize((ship_radius, ship_radius))) for image in self.image_paths]

        self.detoantion_time = 0.3
        #self.detonation_timers = []

    def update(self, ships: List[Ship], asteroids: List[Asteroid]) -> None:

        # Delete everything from canvas so we can re-plot
        self.game_canvas.delete("all")

        # Plot shields, bullets, ships, and asteroids
        self.plot_shields(ships)
        self.plot_ships(ships)
        self.plot_asteroids(asteroids)

        # Update score box
        self.update_score(ships)

        # Push updates to graphics refresh
        self.window.update()

    def close(self) -> None:
        self.window.destroy()

    def update_score(self, ships: List[Ship]) -> None:

        # offsets to deal with cleanliness and window borders covering data
        x_offset = 5
        y_offset = 5

        # outline and center line
        self.game_canvas.create_rectangle(self.game_width, 0, self.window_width, self.game_height, outline="white", fill="black",)
        self.game_canvas.create_line(self.window_width - self.score_width / 2, 0,
                                self.window_width - self.score_width / 2, self.game_height, fill="white")


        # index for loop: allows teams to be displayed in order regardless of team num skipping or strings for team name
        team_num = 0

        output_location_y = 0
        max_lines = 0

    def format_ui(self, team: Team) -> str:
        # lives, accuracy, asteroids hit, shots taken
        team_info = "_________\n"
        if self.show_lives:
            team_info += "Lives: " + str(team.lives_remaining) + "\n"
        if self.show_accuracy:
            team_info += "Accuracy: " + str(round(team.accuracy * 100, 1)) + "\n"
        if self.show_asteroids_hit:
            team_info += "Asteroids Hit: " + str(team.asteroids_hit) + "\n"
        if self.show_shots_fired:
            team_info += "Shots Fired: " + str(team.shots_fired) + "\n"

        return team_info

    def plot_ships(self, ships: List[Ship]) -> None:
        """
        Plots each ship on the game screen using cached sprites and rotating them
        """
        for idx, ship in enumerate(ships):
            if ship.alive:
                # plot ship image and id text next to it
                if ship.custom_sprite_path:
                    sprite_idx = self.image_paths.index(os.path.join(self.img_dir,ship.custom_sprite_path))
                else:
                    sprite_idx = idx
                self.ship_sprites[sprite_idx] = ImageTk.PhotoImage(self.ship_images[sprite_idx].rotate(180 - (-ship.heading - 90)))
                self.game_canvas.create_image(ship.position[0], self.game_height - ship.position[1],
                                              image=self.ship_sprites[sprite_idx])
                self.game_canvas.create_text(ship.position[0] + ship.radius,
                                             self.game_height - (ship.position[1] + ship.radius), text=str(ship.id),
                                             fill="white")

    def plot_shields(self, ships: List[Ship]) -> None:
        """
        Plots each ship's shield ring
        """
        for ship in ships:
            if ship.alive:
                # Color shield based on respawn time remaining
                respawn_scaler = max(min(ship.respawn_time_left, 1), 0)
                r = int(120 + (respawn_scaler * (255 - 120)))
                g = int(200 + (respawn_scaler * (0 - 200)))
                b = int(255 + (respawn_scaler * (0 - 255)))
                color = "#%02x%02x%02x" % (r, g, b)
                # Plot shield ring
                self.game_canvas.create_oval(ship.position[0] - ship.radius,
                                             self.game_height - (ship.position[1] + ship.radius),
                                             ship.position[0] + ship.radius,
                                             self.game_height - (ship.position[1] - ship.radius),
                                             fill="black", outline=color)

    def plot_asteroids(self, asteroids: List[Asteroid]) -> None:
        """
        Plots each asteroid object on the game screen
        """
        for asteroid in asteroids:
            self.game_canvas.create_oval(asteroid.position[0] - asteroid.radius,
                                         self.game_height - (asteroid.position[1] + asteroid.radius),
                                         asteroid.position[0] + asteroid.radius,
                                         self.game_height - (asteroid.position[1] - asteroid.radius),
                                         fill="grey")