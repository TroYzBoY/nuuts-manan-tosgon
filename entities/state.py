"""
State enum for game entities
"""
from enum import Enum


class State(Enum):
    IDLE = 0
    ATTACKING = 1
    HURT = 2
    DEAD = 3

