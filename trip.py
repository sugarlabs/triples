# trip.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""

import random
import pygame

import g
import utils

words = ['smile', 'butterfly', 'lion', 'fish', 'apple', 'tent', 'zebra',
         'leaf', 'tractor', 'bird']


class Locn:
    def __init__(self, x, y, r, c, ind, card, pic):
        self.x = int(x)
        self.y = int(y)
        self.r = r
        self.c = c
        self.ind = ind
        self.card = card  # 0..9
        self.pic = pic
        if words == []:
            self.pic = True
        self.state = 0  # 0 = face down, 1 = face up, 2 = gone, 3 = just found


class Trip:
    def __init__(self, sugar, label, colors):
        self.sugar = sugar
        self.label = label
        self.colors = colors
        self.pics = []
        for ind in range(10):
            pic = utils.load_image(str(ind) + '.png', True)
            self.pics.append(pic)
        self.back = utils.load_image('back.png', True)
        self.front = utils.load_image('front.png', True)
        self.grey = utils.load_image('grey.png', True)
        self.star = utils.load_image('star.png', True)
        self.w = self.back.get_width()
        self.h = self.back.get_height()
        self.nr = g.nr
        self.nc = g.nc
        gutter = (g.sy(32) - self.nc * self.w) / (self.nc + 1.0) / 1.5
        self.locns = []
        ind = 0
        card = 0
        y = gutter
        pic = True
        x0 = (g.w - self.nc * (self.w + gutter)) / 2
        for r in range(self.nr):
            x = x0
            for c in range(self.nc):
                locn = Locn(x, y, r, c, ind, card, pic)
                self.locns.append(locn)
                x += (self.w + gutter)
                ind += 1
                card += 1
                if card == 10:
                    card = 0
                    pic = False
            y += (self.h + gutter)
        self.xn = x0 / 2
        self.yn = y
        self.green = None
        self.tries_cxy = (g.sx(3), g.sy(20.8))
        self.best_xcy = (g.sx(26.5), g.sy(20.8))
        self.star_xy = (self.best_xcy[0] - self.star.get_width() - 5,
                        g.sy(20.1))
        self.gutter = gutter

    def setup(self):
        for locn in self.locns:
            locn.state = 0
        self.shuffle()
        self.green = self.locns[0]
        self.set_mouse()
        self.clicks = []
        self.finished = False
        self.tries = 0
        self.delay = False

    def draw(self):
        for locn in self.locns:
            if locn.state == 0:
                g.screen.blit(self.back, (locn.x, locn.y))
            elif locn.state in (1, 3):
                if locn.pic or not g.words:
                    g.screen.blit(self.pics[locn.card], (locn.x, locn.y))
                else:
                    g.screen.blit(self.front, (locn.x, locn.y))
                    cxy = (locn.x + self.w / 2, locn.y + self.h / 2)
                    utils.text_blit(g.screen, words[locn.card],
                                    g.font1, cxy, utils.BLACK, False)
        if self.green is not None:
            pygame.draw.rect(g.screen, self.colors,
                             (self.green.x, self.green.y, self.w, self.h), 5)
        if self.tries > 0:
            if not self.sugar:
                utils.display_number(self.tries, self.tries_cxy, g.font2,
                                     utils.CREAM)
        if g.best > 0 and not self.sugar:
            g.screen.blit(self.star, (self.star_xy))
            utils.display_number1(g.best, self.best_xcy, g.font2, utils.ORANGE)
        if self.sugar:
            self.label.set_markup(
                '<span><big><b> %s (%s)</b></big></span>' % (
                    str(int(float(self.tries))),
                    str(int(float(g.best)))))
        if len(self.clicks) == 3:
            locn = self.clicks[0]
            g.screen.blit(self.grey, (locn.x, locn.y))
        if g.numbers:
            x = self.xn
            y = self.h / 2 + self.gutter
            for r in range(self.nr):
                n = self.nr - r
                utils.display_number(n, (x, y), g.font1, utils.CREAM)
                y += self.h + self.gutter
            x = self.xn * 2 + self.w / 2
            y = self.yn + g.sy(.4)
            for c in range(self.nc):
                n = c + 1
                utils.display_number(n, (x, y), g.font1, utils.CREAM)
                x += self.w + self.gutter

    def click(self):
        if self.green is not None:
            if self.green.state == 0:
                self.green.state = 1
                self.tries += 1
                if len(self.clicks) < 3:
                    self.clicks.append(self.green)
                else:
                    self.clicks[0].state = 0
                    self.clicks[0] = self.clicks[1]
                    self.clicks[1] = self.clicks[2]
                    self.clicks[2] = self.green
                if len(self.clicks) == 3:
                    if self.clicks[0].card == self.clicks[1].card and\
                            self.clicks[1].card == self.clicks[2].card:
                        for locn in self.clicks:
                            locn.state = 3
                        self.clicks = []
                        self.tries -= 3
                        if self.tries < 0:
                            self.tries = 0
                        self.delay = True
                g.redraw = True
                return True
            if self.green in self.clicks:
                # already showing
                self.make_last(self.green)
                g.redraw = True
                return True
        return False

    def gone(self):
        for locn in self.locns:
            if locn.state == 3:
                locn.state = 2

    def shuffle(self):
        for i in range(100):
            r1 = random.randint(0, len(self.locns) - 1)
            r2 = random.randint(0, len(self.locns) - 1)
            self.locns[r1].card, self.locns[r2].card = \
                self.locns[r2].card, self.locns[r1].card
            self.locns[r1].pic, self.locns[r2].pic = \
                self.locns[r2].pic, self.locns[r1].pic

    def complete(self):
        if self.finished:
            return True
        for locn in self.locns:
            if locn.state != 2:
                return False
        self.finished = True
        self.green = None
        if self.tries < g.best or g.best == 0:
            g.best = self.tries
        return True

    def set_mouse(self):
        locn = self.green
        if locn is not None:
            g.pos = (locn.x + self.w / 2, locn.y + self.h / 2)
            pygame.mouse.set_pos(g.pos)

    def check_mouse(self):
        if not self.complete():
            for locn in self.locns:
                if utils.mouse_in(locn.x, locn.y, locn.x + self.w,
                                  locn.y + self.h):
                    self.green = locn
                    return True
        return False

    def make_last(self, locn):
        self.clicks.remove(locn)
        self.clicks.append(locn)
        return True

    def inc_r(self):
        ind = self.green.ind + self.nc
        if ind >= len(self.locns):
            ind = self.green.c
        self.green = self.locns[ind]
        self.set_mouse()

    def dec_r(self):
        ind = self.green.ind - self.nc
        if ind < 0:
            ind = ind + len(self.locns)
        self.green = self.locns[ind]
        self.set_mouse()

    def inc_c(self):
        c = self.green.c
        if c == self.nc - 1:
            # end of row
            ind = self.green.ind - self.nc + 1
        else:
            ind = self.green.ind + 1
        self.green = self.locns[ind]
        self.set_mouse()

    def dec_c(self):
        c = self.green.c
        if c == 0:
            # start of row
            ind = self.green.ind + self.nc - 1
        else:
            ind = self.green.ind - 1
        self.green = self.locns[ind]
        self.set_mouse()
