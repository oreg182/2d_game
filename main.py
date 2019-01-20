from tkinter import *
import random
from _gui import Mybutton
from config import get_confi
from einheiten import _Unit  # nur zu testzwecken
from gebaeude import Gebaeude, Headquarter
from PIL import Image, ImageDraw, ImageTk
import logging as log
import datetime
from sys import path
from _tkinter import TclError
import json

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

    @staticmethod
    def check_login(e1, e2, file=get_confi("LOGINFILE")):
        with open(file) as f1:
            d = json.load(f1)[0]
        try:
            if d[e1] == e2:  # TODO hash + server check
                return False
            else:
                return 'Falsches Passwort'
        except KeyError:
            return 'Falscher Nutzername'


PLAYER = Profile(get_confi("DEFAULT_USERID"), get_confi("DEFAULT_USERNAME"))


class Chunk:
    def __init__(self, x, y, idnr=0):
        self.x_coord = x
        self.y_coord = y
        self.idnr = idnr
        self.__ground = DEFAULT
        self.__building = DEFAULT
        self.units_inside = []
        self.image = DEFAULT

        self.generate_random()
        self.set_image()

        self.move_into(_Unit())
        log.debug('created new chunk (' + str(self.x_coord) + '|' + str(self.y_coord))

    def set_id(self, idnr):
        self.idnr = idnr

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
            self.__building = Headquarter(random.choice([PLAYER, Profile(2, 'test')]))

    def move_into(self, unit):
        """
        unit in den chunk bewegen
        unit wird dabei in self.untis gespeichert
        """
        self.units_inside.append(unit)

    def move_out(self, unit):
        """
        unit aus dem chunk bewegen
        unit wird aus self.unit gelöscht
        """
        self.units_inside.remove(unit)

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
        return '<<Chunk>> id: ' + str(self.idnr) + ' with coords: ' + str(self.x_coord) + '|' + str(self.y_coord)


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
                row.append(Chunk(x, y, idnr))
                idnr += 1
            self.allchunks.append(row)

    def save_playground(self, file=get_confi("STANDART_SAVE_FILE")):
        pass

    def load_playground(self):
        pass


PLAYGROUND = Playground()


class App:
    def __init__(self, playground=PLAYGROUND):
        self.playground = playground
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
        if not Profile.check_login(e1, e2):
            self.loginframe.pack_forget()
            self.playgroundframe.grid(row=0, column=0)
            self.infoframe.grid(row=0, column=1)
            self.menuframe.grid(row=1, column=0)
            self.build_playground()
            self.build_menu()

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
        pass

    def __load_chunks(self, centerchunkcoord: tuple):
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
                                 command=lambda c=chunk: self.build_building_in_chunk(Headquarter(PLAYER), c))
            buildbutton.pack()
        self.infoframeobj.append(coordslbl)

    def build_menu(self):
        self.menupunkte.append(Label(self.menuframe, text='Menu').grid(row=0, column=0))

    def build_building_in_chunk(self, building, chunk):
        chunk.set_building(building)
        self.update_all(chunk)
        log.debug('gebaude gebaut bei ' + str(chunk.x_coord) + '|' + str(chunk.y_coord))

    def update_all(self, chunk: Chunk):
        for c in self.displayed_labels:
            if c.idnr == chunk.idnr:
                log.debug('idnrs are equal: ' + str(c.idnr) + ' ' + str(chunk.idnr))
                chunk.update_image()
                self.build_playground()
                self.build_infoscreen(chunk)
                break


if __name__ == '__main__':
    App()
