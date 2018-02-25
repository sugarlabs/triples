#!/usr/bin/python
# Triples.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""

import sys
from gi.repository import Gtk
import pygame

import g
import utils
import buttons
import load_save
import trip


class Triples:

    def __init__(self, colors, sugar=False):
        self.colors = colors[:]
        self.sugar = sugar
        self.journal = True  # set to False if we come in via main()
        self.canvas = None
        self.label = None

    def display(self):
        g.screen.fill(self.colors[1])
        self.trip.draw()
        buttons.draw()

    def set_label(self, label):
        self.label = label

    def do_click(self):
        if self.trip.complete():
            return
        self.trip.click()

    def do_button(self, bu):
        if bu == 'new':
            self.trip.setup()

    def do_key(self, key):
        if key in g.SQUARE:
            self.do_button('new')
            return
        if key == pygame.K_v:
            g.version_display = not g.version_display
            return
        if not self.trip.complete():
            if key in g.DOWN:
                self.trip.inc_r()
            elif key in g.UP:
                self.trip.dec_r()
            elif key in g.RIGHT:
                self.trip.inc_c()
            elif key in g.LEFT:
                self.trip.dec_c()
            elif key in g.CROSS:
                self.trip.click()
                self.trip.set_mouse()
            elif key == pygame.K_w:
                g.words = not g.words
            elif key == pygame.K_n:
                g.numbers = not g.numbers

    def buttons_setup(self):
        if not self.sugar:
            buttons.Button('new', (g.sx(16), g.sy(20.8)))

    def flush_queue(self):
        flushing = True
        while flushing:
            flushing = False
            if self.journal:
                while Gtk.events_pending():
                    Gtk.main_iteration()
            for event in pygame.event.get():
                flushing = True

    def run(self, restore=False):
        g.init()
        if not self.journal:
            utils.load()
        self.trip = trip.Trip(self.sugar, self.label, self.colors[0])
        self.trip.setup()
        load_save.retrieve()
        self.buttons_setup()
        if self.canvas is not None:
            self.canvas.grab_focus()
        ctrl = False
        pygame.key.set_repeat(600, 120)
        key_ms = pygame.time.get_ticks()
        going = True
        while going:
            if self.journal:
                # Pump GTK messages.
                while Gtk.events_pending():
                    Gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # only in standalone version
                    if not self.journal:
                        utils.save()
                    going = False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos = event.pos
                    self.trip.check_mouse()
                    g.redraw = True
                    if self.canvas is not None:
                        self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw = True
                    if event.button == 1:
                        bu = buttons.check()
                        if bu != '':
                            self.do_button(bu)
                        else:
                            if self.trip.check_mouse():
                                self.do_click()
                        self.flush_queue()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks() - key_ms > 110:
                        key_ms = pygame.time.get_ticks()
                        if ctrl:
                            if event.key == pygame.K_q:
                                if not self.journal:
                                    utils.save()
                                going = False
                                break
                            else:
                                ctrl = False
                        if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                            ctrl = True
                            break
                        self.do_key(event.key)
                        g.redraw = True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl = False
            if not going:
                break
            if g.redraw:
                self.display()
                if g.version_display:
                    utils.version_display()
                g.screen.blit(g.pointer, g.pos)
                pygame.display.flip()
                g.redraw = False
                if self.trip.delay:
                    pygame.time.delay(1000)
                    self.trip.delay = False
                    self.trip.gone()
                    g.redraw = True
                    self.trip.complete()
            g.clock.tick(40)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
    global colors
    game = Triples(([0, 255, 0], [0, 0, 192]))
    game.journal = False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
