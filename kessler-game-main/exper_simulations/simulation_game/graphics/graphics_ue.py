# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import socket
import numpy as np
from typing import List

from ..ship import Ship
from ..asteroid import Asteroid
from ..sim_scenario import SimulationScenario
from .graphics_base import KesslerGraphics


class GraphicsUE(KesslerGraphics):
    def __init__(self) -> None:
        # Create udp senders/receivers
        udp_host = 'localhost'
        udp_port = 12345
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_recvr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_recvr.bind(('localhost', 12346))
        self.udp_addr = (udp_host, udp_port)

    def start(self, scenario: SimulationScenario) -> None:
        self.map_size = scenario.map_size
        ship_count = len(scenario.ships())
        team_count = len(np.unique([ship.team for ship in scenario.ships()]))

        # TODO Launch game

        # Wait for graphics engine to be fully initialized before sending scenario initialization message
        print('Waiting for graphics to launch.')
        graphics_ready = False
        while not graphics_ready:
            buf, tmp = self.udp_recvr.recvfrom(2097152)
            graphics_ready = buf.decode('utf-8') == 'graphics_ready'
        print('Graphics ready. Starting simulation')

        start_str = '::start::'
        start_str += 'map:' + str(self.map_size[0]) + ',' + str(self.map_size[1]) + ';'
        start_str += 'ships:' + str(ship_count) + ';'
        start_str += 'teams:' + str(team_count)
        self.udp_sock.sendto(start_str.encode('utf-8'), self.udp_addr)

    def update(self, ships: List[Ship], asteroids: List[Asteroid]) -> None:
        update_parts = ['::frame::']

        for ship in ships:
            ship_part = 's({},{},{},{},{},{});'.format(
                round(self.map_size[0] - ship.position[0]),
                round(ship.position[1]),
                round(180 - ship.heading),
                round(ship.radius),
                round(ship.alive),
                float(ship.respawn_time_left)
            )
            update_parts.append(ship_part)

        for ast in asteroids:
            asteroid_part = 'a({},{},{},{},{},{});'.format(
                round(self.map_size[0] - ast.position[0]),
                round(ast.position[1]),
                round(180 - ast.angle),
                round(ast.radius),
                0,
                0
            )
            update_parts.append(asteroid_part)


        update_str = ''.join(update_parts)

        self.udp_sock.sendto(update_str.encode('utf-8'), self.udp_addr)

    def close(self) -> None:
        self.udp_sock.close()
