import numpy as np
from typing import Dict, Any

class Vectors:
    __slots__ = ('position_vector', 'velocity_vector')
    def __init__(self) -> None:
        self.position = None
    
    @property
    def state(self) -> Dict[str, Any]:
        
        return {
            "position_vector": self.position

        }
