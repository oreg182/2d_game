DEFAULT = 'DEFAULT'


class Gebaeude:
    def __init__(self, owner):
        self.owner = owner


class Headquarter(Gebaeude):
    def __init__(self, owner):
        super().__init__(owner)


class Bunker(Gebaeude):
    def __init__(self, owner):
        super().__init__(owner)
