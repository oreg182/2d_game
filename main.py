from tkinter import *
import random
from _gui import Mybutton
from config import get_confi
from einheiten import Unit  # nur zu testzwecken
from gebaeude import Gebaeude
from _connection import connect
from PIL import Image, ImageDraw, ImageTk
import hashlib
import logging as log
import datetime
from sys import path
from _tkinter import TclError

PATH = path[0]
LOGPATH = PATH + '/logs'
DEFAULT = "DEFAULT"

timestr = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
f = open(LOGPATH + '/' + timestr + '.log', 'w')  # create log folder manually if err
f.close()
log.basicConfig(filename=LOGPATH + '/' + timestr + '.log', level=log.DEBUG)

log.info("=======================STARTED=NEW=MAIN=====================")


class Profile:
    def __init__(self, idnr, name):
        self.name = name
        self.idnr = int(idnr)
        log.debug('New Profile: ' + str(self.name) + ' with id: ' + str(self.idnr))

    def __repr__(self):
        return self.name + '/' + str(self.idnr)

    @staticmethod
    def check_login(name, pw):
        h = hashlib.sha512(bytes(pw, 'utf-8')).hexdigest()
        c = connect('LOGIN', str(name) + '*' + h)
        if c == '0':
            return False
        else:
            return c


PLAYER = Profile(get_confi("DEFAULT_USERID"), get_confi("DEFAULT_USERNAME"))


class Chunk:
    def __init__(self, string, x=0, y=0, idnr=0):
        self.x_coord = x
        self.y_coord = y
        self.idnr = idnr
        self.__ground = DEFAULT
        self.__building = DEFAULT
        self.units_inside = []
        self.image = DEFAULT
        if not string:
            self.generate_random()
        else:
            self.build_from_str(string)

        self.set_image()
        log.debug('created new chunk (' + str(self.x_coord) + '|' + str(self.y_coord))

    def get_ground(self):
        return self.__ground

    def get_building(self):
        return self.__building

    def set_building(self, new):
        self.__building = new
        self.set_image()

    def generate_random(self):
        """gesamten chunk random generieren"""
        self.__ground = random.choice(['wood', 'desert'])
        if not random.randint(0, 6):
            self.__building = Gebaeude('Headquarter', random.choice([PLAYER, Profile(2, 'test')]))

    def build_from_str(self, string: str):
        sl = string.split('*')
        self.idnr = int(sl[0])
        self.x_coord = int(sl[1])
        self.y_coord = int(sl[2])
        self.__ground = sl[3]

        if sl[4] != 'DEFAULT':
            self.__building = Gebaeude(sl[4].split('=')[0], sl[4].split('=')[1])
        if sl[5] != 'EMPTY':
            for u in sl[5].split(']'):
                self.units_inside.append(Unit(string=u))

    def set_image(self):
        backgroundcolors = get_confi("BACKGROUND_COLOR")
        backgroundcolor = backgroundcolors[self.__ground]
        bgimage = Image.new('RGB', (22, 14), backgroundcolor)
        self.image = bgimage
        self.update_image()
        log.debug('created image')

    def update_image(self):
        if isinstance(self.__building, Gebaeude):
            if self.__building.owner == PLAYER:
                c = 'lightgreen'
            else:
                c = 'red'
            draw = ImageDraw.Draw(self.image)
            draw.ellipse((7, 5, 11, 9), c)  # x-r y-r x+r y+r

    def __str__(self):
        """
        :return: id x y ground building units
        """
        units = str()
        for u in self.units_inside:
            units += str(u)
        if units == str():
            units = "EMPTY"
        # Trennzeichen: # * = /
        return '<<Chunk>> id: ' + str(self.idnr) + ' with coords: (' + str(self.x_coord) + '|' + str(
            self.y_coord) + ') datapack:#' + str(self.idnr) + '*' + str(self.x_coord) + '*' + str(
            self.y_coord) + '*' + str(self.get_ground()) + '*' + str(self.get_building()) + '*' + units

    def __repr__(self):
        units = str()
        for u in self.units_inside:
            units += str(u) + ']'
        units = units[:-1]
        return str(self.idnr) + '*' + str(self.x_coord) + '*' + str(self.y_coord) + '*' + str(
            self.get_ground()) + '*' + str(self.get_building()) + '*' + units


class Playground:
    def __init__(self, source='NEW'):
        self.allchunks = list()
        if source == 'NEW':
            self.generate_random_chunks()
        elif source == 'SERVER':
            self.load_playground()

    def generate_random_chunks(self):
        idnr = 0
        for x in range(get_confi("GENERATE_RANDOM_MAP_SIZE_X")):
            row = list()
            for y in range(get_confi('GENERATE_RANDOM_MAP_SIZE_Y')):
                row.append(Chunk(0, x, y, idnr=idnr))
                idnr += 1
            self.allchunks.append(row)

    def load_playground(self):
        playground_str = connect('PLAYGROUND', 'complete')
        for i in range(len(playground_str.split("["))):
            line = playground_str.split('[')[i]
            row = list()
            for j in range(len(line.split(';'))):
                row.append(Chunk(line.split(';')[j]))
            self.allchunks.append(row)

    def get_playground_as_str(self):
        s = str()
        for l in self.allchunks:
            for ob in l:
                s += str(ob).split('#')[1] + ';'
            s = s[:-1]
            s += '['
        s = s[:-1]
        return s

    def __repr__(self):
        return self.get_playground_as_str()


class App:
    def __init__(self):
        self.root = Tk()
        try:
            self.root.state('zoomed')
        except TclError:
            pass
        self.root.title('PLACEHOLDER')
        self.images = list()
        self.loginframe = Frame(self.root)
        self.playgroundframe = Frame(self.root)
        self.infoframe = Frame(self.root)
        self.menuframe = Frame()
        self.infoframeobj = list()
        self.loaded_chunks = list()
        self.displayed_labels = list()
        self.menupunkte = list()
        self.playground = None
        self.build_loginscreen()
        self.root.mainloop()

    def build_loginscreen(self):
        global PLAYER
        l1 = Label(self.loginframe, text='Spielername: ')
        l2 = Label(self.loginframe, text='Passwort: ')
        e1 = Entry(self.loginframe)
        e2 = Entry(self.loginframe)
        b1 = Button(self.loginframe, text='Anmelden', command=lambda: self.check_login(e1.get(), e2.get()))
        b1.grid(row=2, column=0)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        self.loginframe.pack()

    def check_login(self, e1, e2):
        c = Profile.check_login(e1, e2)
        if not c:
            self.loginframe.pack_forget()
            self.playgroundframe.grid(row=0, column=0)
            self.infoframe.grid(row=0, column=1)
            self.menuframe.grid(row=1, column=0)
            self.build_playground()
            self.build_menu()
        else:
            Label(self.loginframe, text=c).grid(row=2, column=1)

    def build_playground(self, center=get_confi("TEST_CENTER_OF_MAP")):
        self.__load_chunks(center)
        self.displayed_labels = list()
        for chunk in self.loaded_chunks:
            self.images.append(ImageTk.PhotoImage(chunk.image))
            self.displayed_labels.append(
                Mybutton(chunk.idnr, (chunk.x_coord, chunk.y_coord), self.playgroundframe, image=self.images[-1],
                         border=1, height=10, width=20, command=lambda c=chunk: self.build_infoscreen(c)))
            self.displayed_labels[-1].grid(row=chunk.x_coord, column=chunk.y_coord)

    def update_playground(self):
        # server request + rebuilt des playground
        pass

    def __load_chunks(self, centerchunkcoord: tuple):
        self.playground = Playground(source="SERVER")
        for x, row in enumerate(self.playground.allchunks):
            if centerchunkcoord[0] - get_confi("BUILD_MAP_FROM_CENTER_LEFT") < x < centerchunkcoord[0] + get_confi(
                    "BUILD_MAP_FROM_CENTER_RIGHT"):
                for y, chunk in enumerate(row):
                    if centerchunkcoord[1] - get_confi("BUILD_MAP_FROM_CENTER_BOTTOM") < y < centerchunkcoord[1] \
                            + get_confi("BUILD_MAP_FROM_CENTER_TOP"):
                        self.loaded_chunks.append(chunk)

    def build_infoscreen(self, chunk: Chunk):
        self.infoframe = Frame(self.root)
        self.infoframe.grid(row=0, column=1)
        for obj in self.infoframeobj:
            obj.pack_forget()
        coords = chunk.x_coord, chunk.y_coord
        coordslbl = Label(self.infoframe, text=str(coords) + '\n' + str(chunk.get_ground()) + '\n'
                                               + 'Building: ' + str(chunk.get_building()) + '\n' + str(
            chunk.units_inside))
        coordslbl.pack(side=TOP)
        if chunk.get_building() == DEFAULT:
            buildbutton = Button(self.infoframe, text='BUILD',
                                 command=lambda c=chunk: self.build_building_in_chunk(Gebaeude('Headquarter', PLAYER),
                                                                                      c))
            buildbutton.pack()
        self.infoframeobj.append(coordslbl)

    def build_menu(self):
        self.menupunkte.append(Label(self.menuframe, text='Menu').grid(row=0, column=0))

    def build_building_in_chunk(self, building, chunk):
        chunk.set_building(building)
        self.update_one_chunk(chunk)
        connect('ACTION', 'BUILD=' + str(building.sort))
        log.debug('gebaude gebaut bei ' + str(chunk.x_coord) + '|' + str(chunk.y_coord))

    def update_one_chunk(self, chunk: Chunk):
        for c in self.displayed_labels:
            if c.idnr == chunk.idnr:
                log.debug('idnrs are equal: ' + str(c.idnr) + ' ' + str(chunk.idnr))
                chunk.update_image()
                self.build_playground()
                self.build_infoscreen(chunk)
                break


if __name__ == '__main__':
    App()
