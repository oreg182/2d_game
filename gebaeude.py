class Gebaeude:
    def __init__(self, sort, owner):
        self.owner = owner
        self.sort = sort

    def __repr__(self):
        return self.sort + '=' + str(self.owner)
