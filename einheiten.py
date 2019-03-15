DEFAULT = 'DEFAULT'


class _Unit:
    """Base class for all units"""

    def __init__(self, sort):
        self.sort = sort
        if sort == 'PANZER':
            self.__init_panzer(5)
        self.health = 0
        self.range = 0
        self.damage = 0
        self.max_health = 0

    def __init_panzer(self, health):
        self.sort = 'PANZER'
        self.max_health = 5
        self.range = 2
        self.damage = 2
        self.health = health

    def __repr__(self):
        return self.sort + '=' + str(self.health)


class Unit(_Unit):

    def __init__(self, sort=DEFAULT, string=DEFAULT):
        if sort == DEFAULT and string == DEFAULT:
            raise SyntaxError("Fehler beim erstellen der Unit. Kein Typ oder Str")

        elif sort != DEFAULT:
            super().__init__(sort)

        elif string != DEFAULT:
            unittype = string.split('=')[0]
            if unittype == 'PANZER':
                self.__init_panzer(string.split('=')[1])
