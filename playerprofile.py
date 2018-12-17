import json


class Playerprofile:
    def __init__(self, data):
        self.data = data

    def itemconfig(self, **kwargs):
        print(kwargs)
        for el in kwargs:
            self.data[el] = kwargs[el]

    def return_player_attr(self, attr):
        return self.data[attr]


def load_profile(player) -> Playerprofile:
    data = json.load(open('playerprofile_' + player + '.json'))[0]
    pp = Playerprofile(data)
    return pp


a = load_profile('gero')
print(a.return_player_attr("name"))