from pico2d import *

import game_framework
import game_world
from background import Background
from ground import Ground
from character import Character
from ball import Ball

player = None
ball = None


def collide_circle(a, b):
    ax, ay, ar = a
    bx, by, br = b
    return (ax - bx) ** 2 + (ay - by) ** 2 < (ar + br) ** 2


def init():
    pass


def finish():
    pass


def update():
    pass


def draw():
    pass


def handle_events():
    pass


def pause():
    pass


def resume():
    pass
