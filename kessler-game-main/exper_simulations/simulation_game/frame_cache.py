# cache data is a dictionary with lists of asteroids
class FrameCache:
    def __init__(self):
        self._cache = {}
        self._current_frame = 0 

    def save_frame(self, asteroid_data):
        self._cache[self._current_frame] = [ast.state for ast in asteroid_data]
        self._current_frame += 1

    def load_frame(self, frame_num):
        return self._cache.get(frame_num)