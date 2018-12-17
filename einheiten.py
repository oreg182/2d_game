from constants import *


class _Unit:
    """Base class for all units"""

    def __init__(self):
        self.sort = "BASIC"

        self.__health = DEFAULT
        self.__damage = DEFAULT
        self.__range = DEFAULT

#        self.can_fly = False  # optional; nicht berücksichtigen in ersten versionen
#        self.airfield = 0

#        self.can_swim_short = False
#        self.can_swim_long = False

    def __str__(self):
        return "__BASIC_UNIT_CLASS__"


class _Infanterie(_Unit):
    def __init__(self):
        super().__init__()
        self.sort = "INFANTERIE"

    def __str__(self):
        return "__INFANTERIE_CLASS__"


class _Artillerie(_Unit):
    def __init__(self):
        super().__init__()
        self.sort = "ARTILLERIE"

    def __str__(self):
        return "__ARTILLERIE_CLASS__"


class _Panzer(_Unit):
    def __init__(self):
        super().__init__()
        self.sort = "PANZER"

    def __str__(self):
        return "__PANZER_CLASS__"
