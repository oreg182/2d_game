from tkinter import *
import random
from _gui import Mybutton
from config import get_confi
from einheiten import _Unit  # nur zu testzwecken
from gebaeude import Gebaeude, Headquarter
from PIL import ImageTk, Image, ImageDraw
import logging as log
import datetime
from sys import path
import socket as so
PATH = path[0]
LOGPATH = PATH + '/logs'
DEFAULT = "DEFAULT"

timestr = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
f = open(LOGPATH + '/' + timestr + '.log', 'w')
f.close()
log.basicConfig(filename=LOGPATH + '/' + timestr + '.log', level=log.DEBUG)

log.info("=======================STARTED=NEW=MAIN=====================")


class Profile:
    def __init__(self):
        self.name = DEFAULT
        self.id = 0


PLAYER = Profile()


class Chunk:
    def __init__(self, x, y):
        self.x_coord = x
        self.y_coord = y
        self.ground = DEFAULT
        self.building = DEFAULT
        self.units_inside = []
        self.image = DEFAULT

        self.generate_random()
        log.debug('gr done')
        self.set_image()

        self.move_into(_Unit())
        log.debug('created new chunk (' + str(self.x_coord) + '|' + str(self.y_coord))

    def generate_random(self):
        """gesamten chunk random generieren"""
        self.ground = random.choice(['wood', 'desert'])
        if not random.randint(0, 6):
            self.building = Headquarter()
            self.building.owner = random.randint(0, 1)

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
        backgroundcolor = backgroundcolors[self.ground]
        bgimage = Image.new('RGB', (22, 14), backgroundcolor)
        draw = ImageDraw.Draw(bgimage)
        if isinstance(self.building, Gebaeude):
            if self.building.owner == PLAYER.id:
                c = 'lightgreen'
            else:
                c = 'red'
            draw.ellipse((7, 5, 11, 9), c)  # x-r y-r x+r y+r

        log.debug('created image')
        self.image = bgimage


class Playground:
    def __init__(self):
        self.allchunks = list()
        self.generate_random_chunks()

    def generate_random_chunks(self):
        for x in range(get_confi("GENERATE_RANDOM_MAP_SIZE_X")):
            row = list()
            for y in range(get_confi('GENERATE_RANDOM_MAP_SIZE_Y')):
                row.append(Chunk(x, y))
            self.allchunks.append(row)

    def get_playground_from_server(self):
        ipaddress = get_confi('SERVER_IP')
        port = get_confi('SERVER_PORT')
        sock1 = so.socket(so.AF_INET, so.SOCK_STREAM)
        sock1.bind((ipaddress, int(port)))


PLAYGROUND = Playground()


class App:
    def __init__(self):
        self.root = Tk()
        self.root.state('zoomed')
        self.images = list()
        self.playgroundframe = Frame(self.root)
        self.playgroundframe.pack(side=LEFT)
        self.infoframe = Frame(self.root)
        self.infoframe.pack(side=RIGHT)
        self.infoframeobj = list()
        self.loaded_chunks = list()
        self.displayed_labels = list()
        self.build_playground()
        self.root.mainloop()

    def build_infoscreen(self, chunk: Chunk):
        for obj in self.infoframeobj:
            obj.pack_forget()
        coords = chunk.x_coord, chunk.y_coord
        coordslbl = Label(self.infoframe, text=str(coords) + '\n' + str(chunk.ground) + '\n'
                                               + 'Building: ' + str(chunk.building) + '\n' + str(chunk.units_inside))
        coordslbl.pack(side=TOP)
        self.infoframeobj.append(coordslbl)

    def build_playground(self, center=get_confi("TEST_CENTER_OF_MAP")):
        idnr = 0
        self.__load_chunks(center)
        self.displayed_labels = list()
        for chunk in self.loaded_chunks:
            self.images.append(ImageTk.PhotoImage(chunk.image))
            self.displayed_labels.append(
                Mybutton(idnr, (chunk.x_coord, chunk.y_coord), self.playgroundframe, image=self.images[-1],
                         border=1, height=10, width=20, command=lambda c=chunk: self.build_infoscreen(c)).grid(
                    row=chunk.y_coord, column=chunk.x_coord))
            idnr += 1

    def __load_chunks(self, centerchunkcoord: tuple):
        global PLAYGROUND
        for x, row in enumerate(PLAYGROUND.allchunks):
            if centerchunkcoord[0] - get_confi("BUILD_MAP_FROM_CENTER_LEFT") < x < centerchunkcoord[0] + get_confi(
                    "BUILD_MAP_FROM_CENTER_RIGHT"):
                for y, chunk in enumerate(row):
                    if centerchunkcoord[1] - get_confi("BUILD_MAP_FROM_CENTER_BOTTOM") < y < centerchunkcoord[1] \
                            + get_confi("BUILD_MAP_FROM_CENTER_TOP"):
                        self.loaded_chunks.append(chunk)


if __name__ == '__main__':
    a = App()
