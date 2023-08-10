from enum import Enum


class Encounters(Enum):
    SAFE = 1
    OVERTAKING_STAR = 2
    OVERTAKING_PORT = 3
    HEADON = 4
    GIVEWAY = 5
    STANDON = 6
    # EMERGENCY = 7


class Range_Situation(Enum):
    INCREASING = 0
    CLOSING_IN = 1
