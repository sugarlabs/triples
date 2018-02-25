# g.py - globals
import pygame
import utils
import random

app = 'Triples'
ver = '1.0'
ver = '21'
ver = '22'
# flush_queue() doesn't use gtk on non-XO
ver = '23'
# N=numbers
ver = '24'
# pointer follows green rectangle when running non-standalone
ver = '25'
# widescreen fix
ver = '26'
# Sugar stylize

UP = (264, 273)
DOWN = (258, 274)
LEFT = (260, 276)
RIGHT = (262, 275)
CROSS = (259, 120)
CIRCLE = (265, 111)
SQUARE = (263, 32)
TICK = (257, 13)


def init():  # called by run()
    random.seed()
    global redraw
    global screen, w, h, font1, font2, clock
    global factor, offset, imgf, message, version_display
    global pos, pointer
    redraw = True
    version_display = False
    screen = pygame.display.get_surface()
    pygame.display.set_caption(app)
    screen.fill((70, 0, 70))
    pygame.display.flip()
    w, h = screen.get_size()
    if float(w) / float(h) > 1.5:  # widescreen
        offset = (w - 4 * h / 3) / 2  # we assume 4:3 - centre on widescreen
    else:
        h = int(.75 * w)  # allow for toolbar - works to 4:3
        offset = 0
    factor = float(h) / 24  # measurement scaling factor (32x24 = design units)
    imgf = float(h) / 900  # image scaling factor all images built for 1200x900
    clock = pygame.time.Clock()
    if pygame.font:
        t = int(54 * imgf)
        font1 = pygame.font.Font(None, t)
        t = int(80 * imgf)
        font2 = pygame.font.Font(None, t)
    message = ''
    pos = pygame.mouse.get_pos()
    pointer = utils.load_image('pointer.png', True)
    pygame.mouse.set_visible(False)

    # this activity only
    global best, words, numbers, nc, nr
    best = 0
    words = False
    numbers = False
    w1, h1 = screen.get_size()
    if w1 > h1:
        nc = 6
        nr = 5
    else:
        # factor *= 6./5
        imgf *= 6. / 5
        nc = 5
        nr = 6


def sx(f):  # scale x function
    return int(f * factor + offset + .5)


def sy(f):  # scale y function
    return int(f * factor + .5)
