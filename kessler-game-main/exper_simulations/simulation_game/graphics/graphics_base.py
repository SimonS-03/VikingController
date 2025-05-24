# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

#import os
from tkinter import *
from typing import List
#from PIL import Image, ImageTk  # type: ignore[import-untyped]

from ..ship import Ship
from ..asteroid import Asteroid
from ..sim_scenario import SimulationScenario


class KesslerGraphics:
    def start(self, scenario: SimulationScenario) -> None:
        raise NotImplementedError('Your derived KesslerController must include a start() method.')

    def update(self, ships: List[Ship], asteroids: List[Asteroid]) -> None:
        raise NotImplementedError('Your derived KesslerController must include an update() method.')

    def close(self) -> None:
        raise NotImplementedError('Your derived KesslerController must include a close() method.')
